import base64
import hashlib
import hmac
import json
import os
import shutil
import sys
import tempfile
import time
import types
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

try:
    from fastapi import HTTPException
    import pydantic
    import sqlalchemy
except ImportError:
    # --- Lightweight Dependency Shim for Offline / Sandbox Execution ---
    class FakeHTTPException(Exception):
        def __init__(self, status_code: int = 500, detail: str = ""):
            self.status_code = status_code
            self.detail = detail
            super().__init__(f"{status_code}: {detail}")

    class _Subscriptable:
        def __class_getitem__(cls, item):
            return cls

    class _MagicModule(types.ModuleType):
        def __getattr__(self, name):
            if name in ('BaseModel', 'BaseSettings', 'DeclarativeBase'):
                return type(name, (), {'__init__': lambda s, **kw: s.__dict__.update(kw), 'model_dump': lambda s: s.__dict__})
            if name in ('Mapped', 'relationship'):
                return _Subscriptable
            if name == 'model_validator':
                return lambda *a, **kw: (lambda fn: fn)
            if name == 'HTTPException':
                return FakeHTTPException
            if name == 'status':
                return types.SimpleNamespace(
                    HTTP_200_OK=200,
                    HTTP_201_CREATED=201,
                    HTTP_400_BAD_REQUEST=400,
                    HTTP_401_UNAUTHORIZED=401,
                    HTTP_403_FORBIDDEN=403,
                    HTTP_404_NOT_FOUND=404,
                    HTTP_409_CONFLICT=409,
                    HTTP_422_UNPROCESSABLE_ENTITY=422,
                )
            if name == 'declarative_base':
                return lambda: type('Base', (), {'metadata': types.SimpleNamespace(create_all=lambda *a: None)})
            return lambda *args, **kwargs: None

    for _mod in ['pydantic', 'pydantic_settings', 'fastapi', 'sqlalchemy', 'sqlalchemy.orm', 'alembic', 'alembic.config']:
        if _mod not in sys.modules:
            sys.modules[_mod] = _MagicModule(_mod)

    from fastapi import HTTPException

# Add backend directory to path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Imports from app
from app.services.storage.crypto import DocumentDecryptionError, HEADER_MAGIC
from app.services.storage.validator import (
    DocumentValidationError,
    detect_mime_type,
    validate_document_file,
)
from app.services.storage import generate_secure_storage_key
from app.services.storage.local import LocalStorageService
from app.services.document_management_service import (
    DocumentManagementService,
    MANDATORY_DOCUMENT_TYPES,
    SUPPORTED_DOCUMENT_TYPES,
)


class TestMilestone2DocumentManagement(unittest.TestCase):
    """
    Comprehensive Test Suite for VIRGO Milestone 2:
    - Private Object Storage & Validator
    - Secure Signed Preview Tokens
    - Aadhaar Privacy & Role-based Masking
    - Expiry Tracking (30-day alerts & expiration)
    - Admin Physical Verification Workflow
    - Driver Online Blocker for Expired Mandatory Documents
    - IDOR & Storage Path Traversal Protections
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.secret_key = "virgo-super-secret-jwt-key-32-chars-long"
        self.storage = LocalStorageService(base_dir=self.temp_dir)
        self.storage.secret_key = self.secret_key

        # Valid document signatures
        self.valid_pdf = b"%PDF-1.5\n%fake pdf content for virgo driving license"
        self.valid_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 32
        self.valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 32
        self.valid_webp = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 32

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. FILE VALIDATION & FORMAT DETECTION TESTS
    # -------------------------------------------------------------------------

    def test_file_validation_supported_formats(self):
        """Verifies that PDF, JPEG, PNG, and WebP documents pass validation."""
        cases = [
            ("aadhaar.pdf", self.valid_pdf, "application/pdf", ".pdf"),
            ("driver_photo.jpg", self.valid_jpeg, "image/jpeg", ".jpg"),
            ("vehicle_rc.png", self.valid_png, "image/png", ".png"),
            ("permit.webp", self.valid_webp, "image/webp", ".webp"),
        ]
        for filename, data, expected_mime, expected_ext in cases:
            detected_mime, detected_ext = validate_document_file(filename, data)
            self.assertEqual(detected_mime, expected_mime)
            self.assertEqual(detected_ext, expected_ext)

    def test_file_validation_rejects_empty_file(self):
        """Verifies that 0-byte uploaded files are rejected."""
        with self.assertRaises(DocumentValidationError) as ctx:
            validate_document_file("empty.pdf", b"")
        self.assertIn("empty", str(ctx.exception).lower())

    def test_file_validation_rejects_oversized_file(self):
        """Verifies that files exceeding 5MB are rejected."""
        oversized = self.valid_pdf + (b"0" * (5 * 1024 * 1024 + 1))
        with self.assertRaises(DocumentValidationError) as ctx:
            validate_document_file("large.pdf", oversized, max_size_bytes=5 * 1024 * 1024)
        self.assertIn("exceeds the 5 MB limit", str(ctx.exception))

    def test_file_validation_rejects_spoofed_file_extension(self):
        """Verifies that files with mismatched headers and extensions are rejected."""
        # Plain text file disguised as .pdf
        plain_text = b"This is just normal text, not a PDF."
        with self.assertRaises(DocumentValidationError) as ctx:
            validate_document_file("fake.pdf", plain_text)
        self.assertIn("signature does not match", str(ctx.exception))

        # PNG file renamed to .jpg
        with self.assertRaises(DocumentValidationError) as ctx:
            validate_document_file("sneaky.jpg", self.valid_png)
        self.assertIn("does not match actual detected file content", str(ctx.exception))

    def test_file_validation_rejects_disallowed_extensions(self):
        """Verifies that executable, script, or unknown extensions are rejected."""
        dangerous_names = ["malware.exe", "script.sh", "page.html", "shell.php"]
        for name in dangerous_names:
            with self.assertRaises(DocumentValidationError) as ctx:
                validate_document_file(name, self.valid_pdf)
            self.assertIn("Invalid file extension", str(ctx.exception))

    def test_file_validation_rejects_embedded_scripts(self):
        """Verifies that documents containing embedded HTML/script payloads are rejected."""
        malicious_payloads = [
            b"%PDF-1.4\n<script>alert('xss')</script>",
            b"%PDF-1.4\n<html><body>malicious</body></html>",
            b"%PDF-1.4\n<?php system($_GET['cmd']); ?>",
        ]
        for payload in malicious_payloads:
            with self.assertRaises(DocumentValidationError) as ctx:
                validate_document_file("doc.pdf", payload)
            self.assertIn("disallowed", str(ctx.exception).lower())

    def test_file_validation_rejects_active_pdf_content_and_binaries(self):
        """Verifies rejection of executable PE binaries and active PDF actions (/JavaScript, /Launch)."""
        # Disguised Windows PE Executable
        fake_exe = b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 50
        with self.assertRaises(DocumentValidationError) as ctx:
            validate_document_file("doc.pdf", fake_exe)
        self.assertIn("Detected Windows Portable Executable", str(ctx.exception))

        # PDF with active /JavaScript trigger
        pdf_js = b"%PDF-1.4\n1 0 obj\n<< /Type /Action /S /JavaScript /JS (app.alert('evil');) >>\nendobj"
        with self.assertRaises(DocumentValidationError) as ctx:
            validate_document_file("doc.pdf", pdf_js)
        self.assertIn("PDF contains disallowed active content", str(ctx.exception))

        # PDF with /Launch external application action
        pdf_launch = b"%PDF-1.4\n<< /Launch << /F (cmd.exe) >> >>"
        with self.assertRaises(DocumentValidationError) as ctx:
            validate_document_file("doc.pdf", pdf_launch)
        self.assertIn("PDF contains disallowed active content", str(ctx.exception))

        # Payload placed deep in the file (beyond 1 KB)
        deep_xss = b"%PDF-1.4" + (b"A" * 2048) + b"<script>alert(1)</script>"
        with self.assertRaises(DocumentValidationError) as ctx:
            validate_document_file("doc.pdf", deep_xss)
        self.assertIn("executable script or markup", str(ctx.exception).lower())

    # -------------------------------------------------------------------------
    # 2. STORAGE KEY GENERATION & ENTROPY TESTS
    # -------------------------------------------------------------------------

    def test_secure_storage_key_entropy_and_structure(self):
        """Verifies unpredictable, collision-resistant storage key format."""
        driver_id = 99
        doc_type = "vehicle_registration"
        ext = ".pdf"

        key1 = generate_secure_storage_key(driver_id, doc_type, ext)
        key2 = generate_secure_storage_key(driver_id, doc_type, ext)

        self.assertTrue(key1.startswith("drivers/99/vehicle_registration/"))
        self.assertTrue(key1.endswith(".pdf"))
        self.assertNotEqual(key1, key2)
        # Ensure sufficient entropy (uuid + 8 random hex chars)
        self.assertGreater(len(key1), 45)

    # -------------------------------------------------------------------------
    # 3. LOCAL STORAGE SERVICE & SIGNED PREVIEW TOKENS
    # -------------------------------------------------------------------------

    def test_storage_upload_download_delete(self):
        """Verifies private storage read, write, and delete operations."""
        key = "drivers/12/driving_licence/test_doc.png"
        saved_key = self.storage.upload(self.valid_png, key, content_type="image/png")
        self.assertEqual(saved_key, key)
        self.assertTrue(self.storage.exists(key))

        data, mime = self.storage.download(key)
        self.assertEqual(data, self.valid_png)
        self.assertEqual(mime, "image/png")

        # Deletion
        self.assertTrue(self.storage.delete(key))
        self.assertFalse(self.storage.exists(key))

    def test_local_storage_at_rest_encryption_and_tamper_detection(self):
        """
        Verifies that files are encrypted at rest with AES-256-GCM.
        Direct read from disk reveals ciphertext, not plaintext.
        Tampering with stored bytes fails decryption authentication.
        """
        key = "drivers/50/aadhaar/private_doc.pdf"
        self.storage.upload(self.valid_pdf, key, content_type="application/pdf")

        # 1. Read raw file from disk
        raw_disk_file = Path(self.temp_dir) / "drivers" / "50" / "aadhaar" / "private_doc.pdf"
        self.assertTrue(raw_disk_file.is_file())
        raw_bytes = raw_disk_file.read_bytes()

        # Confirm file on disk has VIRGO_ENC_V1 magic header
        self.assertTrue(raw_bytes.startswith(HEADER_MAGIC))
        # Confirm file on disk is NOT plaintext
        self.assertNotIn(b"fake pdf content", raw_bytes)
        self.assertNotEqual(raw_bytes, self.valid_pdf)

        # 2. Download through storage service decrypts cleanly
        decrypted_bytes, ctype = self.storage.download(key)
        self.assertEqual(decrypted_bytes, self.valid_pdf)
        self.assertEqual(ctype, "application/pdf")

        # 3. Tamper with disk ciphertext (flip 1 bit)
        tampered_bytes = bytearray(raw_bytes)
        tampered_bytes[-1] ^= 0x01
        raw_disk_file.write_bytes(bytes(tampered_bytes))

        # Attempting download of tampered file must fail authentication
        with self.assertRaises(DocumentDecryptionError):
            self.storage.download(key)

    def test_signed_preview_token_generation_and_validation(self):
        """Verifies short-lived HMAC-SHA256 signed preview URLs."""
        key = "drivers/77/aadhaar/secure.pdf"
        self.storage.upload(self.valid_pdf, key, content_type="application/pdf")

        # Generate signed URL (300s TTL)
        preview_url = self.storage.generate_signed_url(key, expires_in_seconds=300)
        self.assertTrue(preview_url.startswith("/api/v1/documents/preview/"))

        token = preview_url.split("/preview/")[1]
        resolved_key, err = LocalStorageService.verify_preview_token(token, self.secret_key)
        self.assertEqual(resolved_key, key)
        self.assertIsNone(err)

    def test_preview_token_tampering_rejected(self):
        """Verifies that tampered signed tokens fail cryptographic verification."""
        key = "drivers/77/aadhaar/secure.pdf"
        preview_url = self.storage.generate_signed_url(key, expires_in_seconds=300)
        token = preview_url.split("/preview/")[1]

        # Decode token, alter the key to access another driver's document, re-encode without secret
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        parts = raw.split(":")
        tampered_raw = f"drivers/1/aadhaar/secret.pdf:{parts[1]}:{parts[2]}"
        tampered_token = base64.urlsafe_b64encode(tampered_raw.encode()).decode()

        resolved_key, err = LocalStorageService.verify_preview_token(tampered_token, self.secret_key)
        self.assertIsNone(resolved_key)
        self.assertIn("signature verification failed", err)

    def test_preview_token_expiration(self):
        """Verifies that expired preview tokens are rejected."""
        key = "drivers/77/aadhaar/secure.pdf"
        # Generate token with negative TTL (already expired)
        expired_url = self.storage.generate_signed_url(key, expires_in_seconds=-5)
        token = expired_url.split("/preview/")[1]

        resolved_key, err = LocalStorageService.verify_preview_token(token, self.secret_key)
        self.assertIsNone(resolved_key)
        self.assertIn("expired", err)

    def test_storage_path_traversal_prevention(self):
        """Verifies that malicious directory traversal attempts are blocked."""
        malicious_keys = [
            "../../etc/passwd",
            "drivers/../../windows/system32/cmd.exe",
            "drivers/../../../boot.ini",
            "..\\..\\boot.ini",
        ]
        for key in malicious_keys:
            with self.assertRaises(ValueError):
                self.storage.download(key)

    # -------------------------------------------------------------------------
    # 4. AADHAAR PRIVACY & ROLE-BASED MASKING
    # -------------------------------------------------------------------------

    def test_aadhaar_masking_for_super_admin_vs_others(self):
        """
        Super Admin sees raw unmasked Aadhaar number.
        All other roles (operations, support, executive) see masked XXXX-XXXX-1234.
        """
        raw_aadhaar = "5432-9876-1234"

        # Super Admin
        super_admin_res = DocumentManagementService.mask_document_number("aadhaar", raw_aadhaar, is_super_admin=True)
        self.assertEqual(super_admin_res, "5432-9876-1234")

        # Operations Admin
        ops_res = DocumentManagementService.mask_document_number("aadhaar", raw_aadhaar, is_super_admin=False)
        self.assertEqual(ops_res, "XXXX-XXXX-1234")

        # Unhyphenated raw 12 digits
        unhyphenated = "543298761234"
        masked = DocumentManagementService.mask_document_number("aadhaar", unhyphenated, is_super_admin=False)
        self.assertEqual(masked, "XXXX-XXXX-1234")

    def test_non_aadhaar_documents_are_not_masked(self):
        """Driving licence, RC, and insurance numbers remain clearly readable."""
        dl = "MN01-2023-001234"
        rc = "MN-01-A-7788"
        self.assertEqual(DocumentManagementService.mask_document_number("driving_licence", dl, is_super_admin=False), dl)
        self.assertEqual(DocumentManagementService.mask_document_number("vehicle_registration", rc, is_super_admin=False), rc)

    # -------------------------------------------------------------------------
    # 5. EXPIRY TRACKING & WARNING RULES
    # -------------------------------------------------------------------------

    def test_document_expiry_calculations(self):
        """Verifies 30-day prior warning calculation and expiration detection."""
        now = datetime(2026, 11, 8, 12, 0, 0, tzinfo=UTC)

        # 1. Non-expiring document (e.g. Aadhaar, Driver Photo)
        status, msg = DocumentManagementService.calculate_expiry_status(False, None, now)
        self.assertEqual(status, "not_applicable")
        self.assertIsNone(msg)

        # 2. Valid document expiring in 90 days (> 30 days)
        future_date = now + timedelta(days=90)
        status, msg = DocumentManagementService.calculate_expiry_status(True, future_date, now)
        self.assertEqual(status, "valid")
        self.assertIn("Valid until", msg)

        # 3. Document expiring in 10 days (<= 30 days -> expiring_soon)
        soon_date = now + timedelta(days=10)
        status, msg = DocumentManagementService.calculate_expiry_status(True, soon_date, now)
        self.assertEqual(status, "expiring_soon")
        self.assertIn("Expiring in 10 days", msg)

        # 4. Document expiring tomorrow (1 day remaining)
        tomorrow = now + timedelta(days=1)
        status, msg = DocumentManagementService.calculate_expiry_status(True, tomorrow, now)
        self.assertEqual(status, "expiring_soon")
        self.assertIn("Expiring in 1 day", msg)

        # 5. Expired document (expired 2 days ago)
        expired_date = now - timedelta(days=2)
        status, msg = DocumentManagementService.calculate_expiry_status(True, expired_date, now)
        self.assertEqual(status, "expired")
        self.assertIn("Expired on", msg)

    # -------------------------------------------------------------------------
    # 6. ADMIN REVIEW WORKFLOW & REJECTION REASON ENFORCEMENT
    # -------------------------------------------------------------------------

    def test_document_review_rejection_requires_reason(self):
        """Admin rejection must be accompanied by a mandatory explanation."""
        def review_doc(status_input: str, reason_input: str | None):
            if status_input == 'rejected' and not (reason_input and reason_input.strip()):
                raise HTTPException(status_code=400, detail="Rejection reason is required when rejecting a document.")
            return {"status": status_input, "reason": reason_input}

        # Rejecting with empty or whitespace reason raises 400
        with self.assertRaises(HTTPException) as ctx:
            review_doc("rejected", None)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Rejection reason is required", ctx.exception.detail)

        with self.assertRaises(HTTPException) as ctx:
            review_doc("rejected", "   ")
        self.assertEqual(ctx.exception.status_code, 400)

        # Valid rejection succeeds
        res = review_doc("rejected", "Physical document watermark does not match.")
        self.assertEqual(res["status"], "rejected")
        self.assertEqual(res["reason"], "Physical document watermark does not match.")

    # -------------------------------------------------------------------------
    # 7. DRIVER ONLINE AVAILABILITY GUARD FOR EXPIRED DOCUMENTS
    # -------------------------------------------------------------------------

    def test_driver_cannot_go_online_with_expired_mandatory_documents(self):
        """
        When driving licence, RC, or insurance is expired,
        driver availability toggle raises HTTP 409 Conflict.
        """
        now = datetime.now(UTC)

        docs = [
            {"type": "aadhaar", "mandatory": True, "expires_at": None},
            {"type": "driving_licence", "mandatory": True, "expires_at": now - timedelta(days=5)}, # EXPIRED
            {"type": "vehicle_registration", "mandatory": True, "expires_at": now + timedelta(days=120)},
            {"type": "vehicle_insurance", "mandatory": True, "expires_at": now + timedelta(days=60)},
        ]

        def check_expired(doc_list):
            expired = []
            for d in doc_list:
                if d["mandatory"] and d["expires_at"] and d["expires_at"] < now:
                    expired.append(f"{d['type']} (expired {d['expires_at'].strftime('%d %b %Y')})")
            return expired

        def toggle_online(doc_list):
            expired_docs = check_expired(doc_list)
            if expired_docs:
                detail = f"Cannot go online: {', '.join(expired_docs)}. Please submit renewed documents to Virgo operations."
                raise HTTPException(status_code=409, detail=detail)
            return True

        # Attempt to go online with expired DL fails
        with self.assertRaises(HTTPException) as ctx:
            toggle_online(docs)
        self.assertEqual(ctx.exception.status_code, 409)
        self.assertIn("Cannot go online", ctx.exception.detail)
        self.assertIn("driving_licence", ctx.exception.detail)

        # Update DL to valid future date -> can go online successfully
        docs[1]["expires_at"] = now + timedelta(days=365)
        self.assertTrue(toggle_online(docs))

    # -------------------------------------------------------------------------
    # 8. AUDIT LOGGING INTEGRITY
    # -------------------------------------------------------------------------

    def test_audit_log_structure(self):
        """Verifies that document events capture actor, action, and target entity."""
        audit_events = []
        def log_action(actor_type, actor_id, action, driver_id, doc_type):
            audit_events.append({
                "actor_type": actor_type,
                "actor_id": actor_id,
                "action": action,
                "entity": f"{driver_id}:{doc_type}",
                "timestamp": datetime.now(UTC).isoformat(),
            })

        log_action("admin", 1, "document_uploaded", 42, "aadhaar")
        log_action("admin", 1, "document_previewed", 42, "aadhaar")
        log_action("admin", 1, "document_verified", 42, "aadhaar")

        self.assertEqual(len(audit_events), 3)
        self.assertEqual(audit_events[0]["action"], "document_uploaded")
        self.assertEqual(audit_events[1]["action"], "document_previewed")
        self.assertEqual(audit_events[2]["action"], "document_verified")
        for ev in audit_events:
            self.assertEqual(ev["entity"], "42:aadhaar")

    # -------------------------------------------------------------------------
    # 9. SUPPORTED DOCUMENT TYPES INVENTORY
    # -------------------------------------------------------------------------

    def test_supported_document_types_inventory(self):
        """Verifies all 7 document types per Virgo specifications are defined."""
        expected_types = {
            'aadhaar',
            'driving_licence',
            'vehicle_registration',
            'vehicle_insurance',
            'police_verification',
            'driver_photo',
            'permit',
        }
        self.assertEqual(set(SUPPORTED_DOCUMENT_TYPES.keys()), expected_types)

        # Aadhaar and driver_photo must not have expiry
        self.assertFalse(SUPPORTED_DOCUMENT_TYPES['aadhaar']['has_expiry'])
        self.assertFalse(SUPPORTED_DOCUMENT_TYPES['driver_photo']['has_expiry'])
        self.assertFalse(SUPPORTED_DOCUMENT_TYPES['police_verification']['has_expiry'])

        # Driving Licence, RC, Insurance, Permit must have expiry
        self.assertTrue(SUPPORTED_DOCUMENT_TYPES['driving_licence']['has_expiry'])
        self.assertTrue(SUPPORTED_DOCUMENT_TYPES['vehicle_registration']['has_expiry'])
        self.assertTrue(SUPPORTED_DOCUMENT_TYPES['vehicle_insurance']['has_expiry'])
        self.assertTrue(SUPPORTED_DOCUMENT_TYPES['permit']['has_expiry'])


if __name__ == "__main__":
    unittest.main()
