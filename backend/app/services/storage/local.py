import base64
import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path

from app.core.config import get_settings
from app.services.storage.base import BaseStorageService
from app.services.storage.crypto import (
    HEADER_MAGIC,
    derive_encryption_key,
    encrypt_document_bytes,
    decrypt_document_bytes,
)


class LocalStorageService(BaseStorageService):
    """
    Secure filesystem storage for development and standalone environments.
    Guarantees private storage with AES-256-GCM authenticated at-rest encryption,
    path-traversal protection, and short-lived signed preview tokens.
    """

    def __init__(self, base_dir: str | Path | None = None, secret_key: str | None = None):
        settings = get_settings()
        self.base_dir = Path(base_dir or settings.local_storage_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.secret_key = secret_key or settings.jwt_secret_key
        encryption_secret = getattr(settings, "local_storage_encryption_key", None) or self.secret_key
        self.encryption_key = derive_encryption_key(encryption_secret)

    def _resolve_safe_path(self, key: str) -> Path:
        """Protects against path traversal attacks."""
        clean_key = key.lstrip("/\\")
        target = (self.base_dir / clean_key).resolve()
        if not str(target).startswith(str(self.base_dir)):
            raise ValueError("Access denied: invalid storage key path traversal.")
        return target

    def upload(self, file_data: bytes, key: str, content_type: str, metadata: dict | None = None) -> str:
        target = self._resolve_safe_path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Encrypt at rest with AES-256-GCM authenticated encryption
        encrypted_bytes = encrypt_document_bytes(file_data, self.encryption_key, associated_data=key.encode("utf-8"))
        target.write_bytes(encrypted_bytes)

        # Store metadata sidecar file (no secret keys or sensitive data)
        meta_path = target.with_suffix(target.suffix + ".meta.json")
        meta_payload = {
            "content_type": content_type,
            "plain_size": len(file_data),
            "stored_size": len(encrypted_bytes),
            "encrypted": True,
            "uploaded_at": int(time.time()),
            "metadata": metadata or {},
        }
        meta_path.write_text(json.dumps(meta_payload), encoding="utf-8")
        return key

    def download(self, key: str) -> tuple[bytes, str]:
        target = self._resolve_safe_path(key)
        if not target.is_file():
            raise FileNotFoundError(f"Document object not found: {key}")

        raw_data = target.read_bytes()
        if raw_data.startswith(HEADER_MAGIC):
            data = decrypt_document_bytes(raw_data, self.encryption_key, associated_data=key.encode("utf-8"))
        else:
            data = raw_data

        meta_path = target.with_suffix(target.suffix + ".meta.json")
        content_type = "application/octet-stream"
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                content_type = meta.get("content_type", content_type)
            except Exception:
                pass
        return data, content_type

    def delete(self, key: str) -> bool:
        target = self._resolve_safe_path(key)
        deleted = False
        if target.is_file():
            target.unlink()
            deleted = True
        meta_path = target.with_suffix(target.suffix + ".meta.json")
        if meta_path.is_file():
            meta_path.unlink()
        return deleted

    def exists(self, key: str) -> bool:
        try:
            return self._resolve_safe_path(key).is_file()
        except ValueError:
            return False

    def generate_signed_url(self, key: str, expires_in_seconds: int = 300) -> str:
        """
        Generates a tamper-proof short-lived signed preview URL.
        Valid for `expires_in_seconds` (default 5 minutes).
        """
        exp = int(time.time()) + expires_in_seconds
        payload = f"{key}:{exp}"
        signature = hmac.new(self.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        token_str = f"{payload}:{signature}"
        token = base64.urlsafe_b64encode(token_str.encode()).decode()
        return f"/api/v1/documents/preview/{token}"

    @classmethod
    def verify_preview_token(cls, token: str, secret_key: str) -> tuple[str | None, str | None]:
        """
        Validates token integrity and expiry.
        Returns (key, None) if valid, or (None, error_reason) if invalid/expired.
        """
        try:
            raw = base64.urlsafe_b64decode(token.encode()).decode()
            parts = raw.split(":")
            if len(parts) != 3:
                return None, "Malformed preview token format."
            key, exp_str, signature = parts
            exp = int(exp_str)
        except Exception:
            return None, "Invalid preview token encoding."

        # Verify HMAC signature in constant time
        payload = f"{key}:{exp}"
        expected = hmac.new(secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not secrets.compare_digest(expected, signature):
            return None, "Preview token signature verification failed."

        # Verify expiration
        if time.time() > exp:
            return None, "Preview token has expired. Request a new preview."

        return key, None

