from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

DocumentTypeEnum = Literal[
    'aadhaar',
    'driving_licence',
    'vehicle_registration',
    'vehicle_insurance',
    'police_verification',
    'driver_photo',
    'permit',
]

VerificationStatusEnum = Literal['missing', 'pending', 'verified', 'rejected', 'expired']
ExpiryStatusEnum = Literal['not_applicable', 'valid', 'expiring_soon', 'expired']


class DriverDocumentDetailResponse(BaseModel):
    id: int | None = None
    driver_id: int
    document_type: str
    label: str
    description: str | None = None
    required: bool = True
    document_number: str | None = None
    verification_status: str
    status: str | None = None  # Compatibility alias for verification_status
    original_filename: str | None = None
    file_size_bytes: int | None = None
    mime_type: str | None = None
    uploaded_at: datetime | None = None
    expires_at: datetime | None = None
    expiry_status: str = 'not_applicable'
    expiry_warning: str | None = None
    rejection_reason: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    has_file: bool = False


class DriverDocumentPreviewResponse(BaseModel):
    driver_id: int
    document_type: str
    preview_url: str
    expires_in_seconds: int = 300


class DriverDocumentListResponse(BaseModel):
    driver_id: int
    driver_name: str
    full_name: str | None = None
    phone_number: str | None = None
    can_go_online: bool
    blocking_reasons: list[str] = Field(default_factory=list)
    total_documents: int = 0
    verified_count: int = 0
    pending_count: int = 0
    missing_count: int = 0
    rejected_count: int = 0
    expired_count: int = 0
    documents: list[DriverDocumentDetailResponse]

