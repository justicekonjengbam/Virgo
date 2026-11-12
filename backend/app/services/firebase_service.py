from pathlib import Path

import firebase_admin
from fastapi import HTTPException, status
from firebase_admin import credentials

from app.core.config import get_settings


def initialize_firebase() -> None:
    """Initialize Firebase Admin once, without exposing credential details to clients."""
    if firebase_admin._apps:
        return
    credential_path = get_settings().firebase_credentials_path
    if not credential_path or not Path(credential_path).is_file():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Firebase Admin is not configured. Set FIREBASE_CREDENTIALS_PATH to a readable service-account JSON file.',
        )
    firebase_admin.initialize_app(credentials.Certificate(credential_path))
