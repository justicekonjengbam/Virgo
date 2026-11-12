import secrets
import uuid
from functools import lru_cache

from app.core.config import get_settings
from app.services.storage.base import BaseStorageService
from app.services.storage.local import LocalStorageService
from app.services.storage.validator import (
    ALLOWED_EXTENSIONS,
    DocumentValidationError,
    detect_mime_type,
    validate_document_file,
)


@lru_cache
def get_storage_service() -> BaseStorageService:
    settings = get_settings()
    backend = settings.storage_backend.lower().strip()
    if backend in ("s3", "r2"):
        try:
            from app.services.storage.s3 import S3StorageService
            return S3StorageService()
        except Exception as error:
            if settings.environment != "production":
                # Fall back to local in non-production if boto3 is not yet configured
                return LocalStorageService()
            raise error
    return LocalStorageService()


def generate_secure_storage_key(driver_id: int, document_type: str, extension: str) -> str:
    """
    Generates an unpredictable, collision-resistant object key.
    Format: drivers/{driver_id}/{document_type}/{uuid4}_{random_hex}.{ext}
    """
    clean_ext = extension.lstrip(".")
    unique_id = uuid.uuid4().hex
    random_entropy = secrets.token_hex(8)
    return f"drivers/{driver_id}/{document_type}/{unique_id}_{random_entropy}.{clean_ext}"


__all__ = [
    "BaseStorageService",
    "LocalStorageService",
    "DocumentValidationError",
    "ALLOWED_EXTENSIONS",
    "detect_mime_type",
    "validate_document_file",
    "get_storage_service",
    "generate_secure_storage_key",
]

