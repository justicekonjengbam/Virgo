"""
Authenticated at-rest encryption for Virgo private local storage.
Uses AES-256-GCM (Authenticated Encryption with Associated Data).
Keys are derived from environment variables and never stored alongside documents.
"""

import ctypes
import hashlib
import hmac
import os
import secrets
import sys
from pathlib import Path

HEADER_MAGIC = b"VIRGO_ENC_V1\x00"  # 13 bytes
IV_LENGTH = 12                     # 12 bytes recommended for AES-GCM
TAG_LENGTH = 16                    # 16 bytes auth tag


class DocumentCryptoError(Exception):
    """Base error for document storage cryptographic operations."""
    pass


class DocumentDecryptionError(DocumentCryptoError):
    """Raised when document decryption or authentication tag verification fails."""
    pass


# ---------------------------------------------------------------------------
# Key Derivation (HKDF-SHA256)
# ---------------------------------------------------------------------------

def derive_encryption_key(secret_source: str, salt: bytes = b"virgo-document-storage-salt-v1") -> bytes:
    """
    Derives a cryptographically strong 256-bit (32-byte) AES key from the secret string.
    Uses HKDF with SHA-256.
    """
    if not secret_source:
        raise ValueError("Secret source for key derivation cannot be empty.")
    
    # Extract
    prk = hmac.new(salt, secret_source.encode("utf-8"), hashlib.sha256).digest()
    # Expand
    info = b"virgo-storage-aes-256-gcm-key"
    okm = hmac.new(prk, info + b"\x01", hashlib.sha256).digest()
    return okm[:32]


# ---------------------------------------------------------------------------
# OpenSSL AES-256-GCM Native Engine via ctypes
# ---------------------------------------------------------------------------

_libcrypto = None

def _get_libcrypto():
    global _libcrypto
    if _libcrypto is not None:
        return _libcrypto

    # 1. Try python DLLs folder
    candidates = [
        Path(sys.base_prefix) / "DLLs" / "libcrypto-3-x64.dll",
        Path(sys.base_prefix) / "DLLs" / "libcrypto-1_1-x64.dll",
        Path(sys.prefix) / "libcrypto.so",
        Path("/usr/lib/libcrypto.so"),
        Path("/usr/lib/x86_64-linux-gnu/libcrypto.so"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                _libcrypto = ctypes.CDLL(str(candidate))
                return _libcrypto
            except Exception:
                continue

    # 2. Try system library resolution
    for name in ("libcrypto-3-x64.dll", "libcrypto.so.3", "libcrypto.so", "crypto"):
        try:
            _libcrypto = ctypes.CDLL(name)
            return _libcrypto
        except Exception:
            continue

    return None


def _init_openssl_gcm():
    lib = _get_libcrypto()
    if not lib:
        return None

    try:
        EVP_CIPHER_CTX_new = lib.EVP_CIPHER_CTX_new
        EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
        EVP_CIPHER_CTX_free = lib.EVP_CIPHER_CTX_free
        EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]

        EVP_EncryptInit_ex = lib.EVP_EncryptInit_ex
        EVP_EncryptInit_ex.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        EVP_EncryptInit_ex.restype = ctypes.c_int

        EVP_EncryptUpdate = lib.EVP_EncryptUpdate
        EVP_EncryptUpdate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.c_int]
        EVP_EncryptUpdate.restype = ctypes.c_int

        EVP_EncryptFinal_ex = lib.EVP_EncryptFinal_ex
        EVP_EncryptFinal_ex.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        EVP_EncryptFinal_ex.restype = ctypes.c_int

        EVP_CIPHER_CTX_ctrl = lib.EVP_CIPHER_CTX_ctrl
        EVP_CIPHER_CTX_ctrl.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
        EVP_CIPHER_CTX_ctrl.restype = ctypes.c_int

        EVP_aes_256_gcm = lib.EVP_aes_256_gcm
        EVP_aes_256_gcm.restype = ctypes.c_void_p

        EVP_DecryptInit_ex = lib.EVP_DecryptInit_ex
        EVP_DecryptInit_ex.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        EVP_DecryptInit_ex.restype = ctypes.c_int

        EVP_DecryptUpdate = lib.EVP_DecryptUpdate
        EVP_DecryptUpdate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.c_int]
        EVP_DecryptUpdate.restype = ctypes.c_int

        EVP_DecryptFinal_ex = lib.EVP_DecryptFinal_ex
        EVP_DecryptFinal_ex.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        EVP_DecryptFinal_ex.restype = ctypes.c_int

        return {
            "ctx_new": EVP_CIPHER_CTX_new,
            "ctx_free": EVP_CIPHER_CTX_free,
            "encrypt_init": EVP_EncryptInit_ex,
            "encrypt_update": EVP_EncryptUpdate,
            "encrypt_final": EVP_EncryptFinal_ex,
            "decrypt_init": EVP_DecryptInit_ex,
            "decrypt_update": EVP_DecryptUpdate,
            "decrypt_final": EVP_DecryptFinal_ex,
            "ctrl": EVP_CIPHER_CTX_ctrl,
            "cipher": EVP_aes_256_gcm,
        }
    except Exception:
        return None

_openssl_funcs = _init_openssl_gcm()


# ---------------------------------------------------------------------------
# Encrypt & Decrypt Routines
# ---------------------------------------------------------------------------

def encrypt_document_bytes(data: bytes, key: bytes, associated_data: bytes = b"") -> bytes:
    """
    Encrypts raw document bytes using AES-256-GCM.
    Returns: HEADER_MAGIC (13B) + IV (12B) + TAG (16B) + CIPHERTEXT.
    """
    if len(key) != 32:
        raise ValueError("AES-256 key must be exactly 32 bytes.")

    iv = secrets.token_bytes(IV_LENGTH)

    # 1. Try python cryptography module if installed
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(key)
        # AESGCM.encrypt appends 16-byte tag to the ciphertext
        ct_with_tag = aesgcm.encrypt(iv, data, associated_data or None)
        tag = ct_with_tag[-16:]
        ciphertext = ct_with_tag[:-16]
        return HEADER_MAGIC + iv + tag + ciphertext
    except ImportError:
        pass

    # 2. Use native OpenSSL libcrypto
    if _openssl_funcs:
        fn = _openssl_funcs
        ctx = fn["ctx_new"]()
        try:
            fn["encrypt_init"](ctx, fn["cipher"](), None, None, None)
            fn["ctrl"](ctx, 0x9, len(iv), None)  # EVP_CTRL_GCM_SET_IVLEN
            fn["encrypt_init"](ctx, None, None, key, iv)
            outlen = ctypes.c_int(0)
            if associated_data:
                fn["encrypt_update"](ctx, None, ctypes.byref(outlen), associated_data, len(associated_data))

            buf = ctypes.create_string_buffer(len(data) + 16)
            ptr = ctypes.cast(buf, ctypes.c_void_p).value
            fn["encrypt_update"](ctx, ptr, ctypes.byref(outlen), data, len(data))
            total_len = outlen.value
            fn["encrypt_final"](ctx, ptr + total_len, ctypes.byref(outlen))
            total_len += outlen.value

            tag = ctypes.create_string_buffer(TAG_LENGTH)
            fn["ctrl"](ctx, 0x10, TAG_LENGTH, tag)  # EVP_CTRL_GCM_GET_TAG
            return HEADER_MAGIC + iv + tag.raw[:TAG_LENGTH] + buf.raw[:total_len]
        finally:
            fn["ctx_free"](ctx)

    # 3. Encrypt-then-MAC fallback using standard library HKDF+HMAC-SHA256 keystream
    return _encrypt_fallback(data, key, iv, associated_data)


def decrypt_document_bytes(encrypted_payload: bytes, key: bytes, associated_data: bytes = b"") -> bytes:
    """
    Authenticates and decrypts document bytes using AES-256-GCM.
    Raises DocumentDecryptionError if the file is corrupted, tampered with, or invalid key.
    """
    if len(key) != 32:
        raise ValueError("AES-256 key must be exactly 32 bytes.")

    header_len = len(HEADER_MAGIC)
    min_len = header_len + IV_LENGTH + TAG_LENGTH
    if len(encrypted_payload) < min_len or not encrypted_payload.startswith(HEADER_MAGIC):
        raise DocumentDecryptionError("Invalid document encryption container or corrupted header.")

    iv = encrypted_payload[header_len : header_len + IV_LENGTH]
    tag = encrypted_payload[header_len + IV_LENGTH : header_len + IV_LENGTH + TAG_LENGTH]
    ciphertext = encrypted_payload[header_len + IV_LENGTH + TAG_LENGTH :]

    # 1. Try python cryptography module
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(key)
        # AESGCM expects ciphertext + tag
        return aesgcm.decrypt(iv, ciphertext + tag, associated_data or None)
    except ImportError:
        pass
    except Exception as exc:
        raise DocumentDecryptionError("Document authentication tag check failed (cryptography).") from exc

    # 2. Use native OpenSSL libcrypto
    if _openssl_funcs:
        fn = _openssl_funcs
        ctx = fn["ctx_new"]()
        try:
            fn["decrypt_init"](ctx, fn["cipher"](), None, None, None)
            fn["ctrl"](ctx, 0x9, len(iv), None)  # EVP_CTRL_GCM_SET_IVLEN
            fn["decrypt_init"](ctx, None, None, key, iv)
            outlen = ctypes.c_int(0)
            if associated_data:
                fn["decrypt_update"](ctx, None, ctypes.byref(outlen), associated_data, len(associated_data))

            buf = ctypes.create_string_buffer(len(ciphertext) + 16)
            ptr = ctypes.cast(buf, ctypes.c_void_p).value
            fn["decrypt_update"](ctx, ptr, ctypes.byref(outlen), ciphertext, len(ciphertext))
            total_len = outlen.value

            tag_buf = ctypes.create_string_buffer(tag, TAG_LENGTH)
            fn["ctrl"](ctx, 0x11, TAG_LENGTH, tag_buf)  # EVP_CTRL_GCM_SET_TAG

            ret = fn["decrypt_final"](ctx, ptr + total_len, ctypes.byref(outlen))
            if ret <= 0:
                raise DocumentDecryptionError("Authentication tag verification failed. Document may be tampered.")
            total_len += outlen.value
            return buf.raw[:total_len]
        finally:
            fn["ctx_free"](ctx)

    # 3. Fallback
    return _decrypt_fallback(ciphertext, key, iv, tag, associated_data)


# ---------------------------------------------------------------------------
# Fallback Encrypt-then-MAC for environments without OpenSSL or cryptography
# ---------------------------------------------------------------------------

def _derive_stream_keys(key: bytes, iv: bytes):
    prk = hmac.new(iv, key, hashlib.sha256).digest()
    enc_key = hmac.new(prk, b"stream-enc-v1", hashlib.sha256).digest()
    mac_key = hmac.new(prk, b"stream-mac-v1", hashlib.sha256).digest()
    return enc_key, mac_key

def _keystream(enc_key: bytes, length: int) -> bytes:
    stream = bytearray()
    counter = 0
    while len(stream) < length:
        block = hmac.new(enc_key, counter.to_bytes(8, "big"), hashlib.sha256).digest()
        stream.extend(block)
        counter += 1
    return bytes(stream[:length])

def _encrypt_fallback(data: bytes, key: bytes, iv: bytes, associated_data: bytes) -> bytes:
    enc_key, mac_key = _derive_stream_keys(key, iv)
    ks = _keystream(enc_key, len(data))
    ciphertext = bytes(a ^ b for a, b in zip(data, ks))
    tag = hmac.new(mac_key, HEADER_MAGIC + iv + ciphertext + associated_data, hashlib.sha256).digest()[:TAG_LENGTH]
    return HEADER_MAGIC + iv + tag + ciphertext

def _decrypt_fallback(ciphertext: bytes, key: bytes, iv: bytes, tag: bytes, associated_data: bytes) -> bytes:
    enc_key, mac_key = _derive_stream_keys(key, iv)
    expected_tag = hmac.new(mac_key, HEADER_MAGIC + iv + ciphertext + associated_data, hashlib.sha256).digest()[:TAG_LENGTH]
    if not secrets.compare_digest(tag, expected_tag):
        raise DocumentDecryptionError("Authentication tag verification failed. Document may be tampered.")
    ks = _keystream(enc_key, len(ciphertext))
    return bytes(a ^ b for a, b in zip(ciphertext, ks))

