import logging
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ride_hailing import AuditLog, Driver, DriverDocument, DriverVehicleAssignment, Vehicle
from app.models.user import AdminUser
from app.schemas.driver_documents import (
    DriverDocumentDetailResponse,
    DriverDocumentListResponse,
    DriverDocumentPreviewResponse,
)
from app.services.storage import (
    DocumentValidationError,
    generate_secure_storage_key,
    get_storage_service,
    validate_document_file,
)

logger = logging.getLogger(__name__)

SUPPORTED_DOCUMENT_TYPES: dict[str, dict] = {
    'aadhaar': {
        'label': 'Aadhaar Card',
        'has_expiry': False,
        'mandatory': True,
        'description': 'Government-issued UIDAI Aadhaar identity verification card',
    },
    'driving_licence': {
        'label': 'Driving Licence',
        'has_expiry': True,
        'mandatory': True,
        'description': 'Valid commercial / non-transport driving licence issued by RTO',
    },
    'vehicle_registration': {
        'label': 'Registration Certificate (RC)',
        'has_expiry': True,
        'mandatory': True,
        'description': 'Official Motor Vehicle Registration Certificate issued by RTO',
    },
    'vehicle_insurance': {
        'label': 'Vehicle Insurance',
        'has_expiry': True,
        'mandatory': True,
        'description': 'Current comprehensive or third-party vehicle insurance policy',
    },
    'police_verification': {
        'label': 'Police Verification / Self-Declaration',
        'has_expiry': False,
        'mandatory': True,
        'description': 'Police verification clearance certificate or self-declaration for mobility drivers',
    },
    'driver_photo': {
        'label': 'Driver Photograph',
        'has_expiry': False,
        'mandatory': True,
        'description': 'Recent clear passport-size photograph against a plain background',
    },
    'permit': {
        'label': 'Commercial/State Permit',
        'has_expiry': True,
        'mandatory': False,
        'description': 'Commercial taxi / transport permit where applicable for commercial vehicles',
    },
}

MANDATORY_DOCUMENT_TYPES = {
    doc_type for doc_type, info in SUPPORTED_DOCUMENT_TYPES.items() if info['mandatory']
}


class DocumentManagementService:
    """Enterprise document management for driver identity and compliance verification."""

    @staticmethod
    def mask_document_number(doc_type: str, number: str | None, is_super_admin: bool) -> str | None:
        if not number:
            return None
        if doc_type == 'aadhaar':
            if is_super_admin:
                return number
            digits = [c for c in number if c.isdigit()]
            if len(digits) >= 4:
                return f"XXXX-XXXX-{''.join(digits[-4:])}"
            return "XXXX-XXXX-XXXX"
        return number

    @staticmethod
    def calculate_expiry_status(
        has_expiry: bool, expires_at: datetime | None, now: datetime
    ) -> tuple[str, str | None]:
        if not has_expiry or not expires_at:
            return 'not_applicable', None

        # Ensure tz-aware comparison
        aware_expiry = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=UTC)
        if aware_expiry < now:
            return 'expired', f"Expired on {aware_expiry.strftime('%d %b %Y')}. Document renewal is mandatory."

        days_remaining = (aware_expiry - now).days
        if days_remaining <= 30:
            unit = 'day' if days_remaining == 1 else 'days'
            return 'expiring_soon', f"Expiring in {days_remaining} {unit} ({aware_expiry.strftime('%d %b %Y')}). Renewal required soon."

        return 'valid', f"Valid until {aware_expiry.strftime('%d %b %Y')}"

    def get_driver_document_list(
        self,
        db: Session,
        driver_id: int,
        requester_role: str | None = None,
    ) -> DriverDocumentListResponse:
        driver = db.get(Driver, driver_id)
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Driver not found.')

        existing_docs = {
            doc.document_type: doc
            for doc in db.scalars(select(DriverDocument).where(DriverDocument.driver_id == driver_id)).all()
        }

        now = datetime.now(UTC)
        is_super_admin = (requester_role == 'super_admin')
        items: list[DriverDocumentDetailResponse] = []
        blocking_reasons: list[str] = []

        for doc_type, info in SUPPORTED_DOCUMENT_TYPES.items():
            doc = existing_docs.get(doc_type)
            if not doc:
                if info['mandatory']:
                    blocking_reasons.append(f"Missing mandatory document: {info['label']}")
                items.append(
                    DriverDocumentDetailResponse(
                        id=None,
                        driver_id=driver_id,
                        document_type=doc_type,
                        label=info['label'],
                        description=info.get('description'),
                        required=info.get('mandatory', True),
                        document_number=None,
                        verification_status='missing',
                        status='missing',
                        original_filename=None,
                        file_size_bytes=None,
                        mime_type=None,
                        uploaded_at=None,
                        expires_at=None,
                        expiry_status='not_applicable',
                        expiry_warning=None,
                        rejection_reason=None,
                        reviewed_by=None,
                        reviewed_at=None,
                        has_file=False,
                    )
                )
                continue

            # Calculate expiry
            expiry_status, expiry_warning = self.calculate_expiry_status(
                info['has_expiry'], doc.expires_at, now
            )

            # Check online blockers
            if info['mandatory']:
                if doc.verification_status == 'rejected':
                    blocking_reasons.append(f"Rejected mandatory document: {info['label']} ({doc.review_note or 'needs re-verification'})")
                elif doc.verification_status == 'pending':
                    blocking_reasons.append(f"Unverified mandatory document: {info['label']} is under review")
                elif expiry_status == 'expired':
                    blocking_reasons.append(f"Expired mandatory document: {info['label']} has expired")

            effective_status = 'expired' if (doc.verification_status == 'verified' and expiry_status == 'expired') else doc.verification_status

            items.append(
                DriverDocumentDetailResponse(
                    id=doc.id,
                    driver_id=driver_id,
                    document_type=doc_type,
                    label=info['label'],
                    description=info.get('description'),
                    required=info.get('mandatory', True),
                    document_number=self.mask_document_number(doc_type, doc.document_number, is_super_admin),
                    verification_status=effective_status,
                    status=effective_status,
                    original_filename=doc.original_filename,
                    file_size_bytes=doc.file_size_bytes,
                    mime_type=doc.mime_type,
                    uploaded_at=doc.created_at,
                    expires_at=doc.expires_at,
                    expiry_status=expiry_status,
                    expiry_warning=expiry_warning,
                    rejection_reason=doc.rejection_reason or doc.review_note,
                    reviewed_by=doc.reviewed_by,
                    reviewed_at=doc.reviewed_at,
                    has_file=bool(doc.storage_key),
                )
            )

        verified_count = sum(1 for it in items if it.verification_status == 'verified')
        pending_count = sum(1 for it in items if it.verification_status == 'pending')
        missing_count = sum(1 for it in items if it.verification_status == 'missing')
        rejected_count = sum(1 for it in items if it.verification_status == 'rejected')
        expired_count = sum(1 for it in items if it.verification_status == 'expired')
        total_documents = len(items)

        can_go_online = (len(blocking_reasons) == 0 and driver.status == 'active')
        return DriverDocumentListResponse(
            driver_id=driver.id,
            driver_name=driver.full_name,
            full_name=driver.full_name,
            phone_number=getattr(driver, 'phone_number', None),
            can_go_online=can_go_online,
            blocking_reasons=blocking_reasons,
            total_documents=total_documents,
            verified_count=verified_count,
            pending_count=pending_count,
            missing_count=missing_count,
            rejected_count=rejected_count,
            expired_count=expired_count,
            documents=items,
        )

    def upload_document(
        self,
        db: Session,
        admin: AdminUser,
        driver_id: int,
        document_type: str,
        file_bytes: bytes,
        filename: str,
        declared_content_type: str | None,
        document_number: str,
        expires_at: datetime | None = None,
    ) -> DriverDocumentDetailResponse:
        driver = db.get(Driver, driver_id)
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Driver not found.')

        if document_type not in SUPPORTED_DOCUMENT_TYPES:
            allowed = ", ".join(SUPPORTED_DOCUMENT_TYPES.keys())
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unsupported document type '{document_type}'. Supported: {allowed}")

        clean_number = document_number.strip()
        if not clean_number:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Document number is required.")

        # Document validation (MIME, magic bytes, size, security)
        try:
            actual_mime, ext = validate_document_file(filename, file_bytes, declared_content_type)
        except DocumentValidationError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        # Generate unique unpredictable storage key
        storage_key = generate_secure_storage_key(driver_id, document_type, ext)

        # Upload to secure storage provider
        storage = get_storage_service()
        try:
            storage.upload(
                file_data=file_bytes,
                key=storage_key,
                content_type=actual_mime,
                metadata={'driver_id': driver_id, 'document_type': document_type, 'uploaded_by': admin.id},
            )
        except Exception as error:
            logger.error("Failed to upload document to storage: %s", error, exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Secure document storage service failed to save the file.") from error

        # Upsert document record in DB
        doc = db.scalar(select(DriverDocument).where(
            DriverDocument.driver_id == driver_id,
            DriverDocument.document_type == document_type,
        ))
        old_storage_key = None
        if doc:
            old_storage_key = doc.storage_key
            doc.document_number = clean_number
            doc.storage_key = storage_key
            doc.original_filename = filename
            doc.mime_type = actual_mime
            doc.file_size_bytes = len(file_bytes)
            doc.verification_status = 'pending'
            doc.review_note = None
            doc.rejection_reason = None
            doc.reviewed_by = None
            doc.reviewed_at = None
            doc.expires_at = expires_at
        else:
            doc = DriverDocument(
                driver_id=driver_id,
                document_type=document_type,
                document_number=clean_number,
                storage_key=storage_key,
                original_filename=filename,
                mime_type=actual_mime,
                file_size_bytes=len(file_bytes),
                verification_status='pending',
                expires_at=expires_at,
            )
            db.add(doc)

        # Audit log entry (NEVER log Aadhaar number or document content)
        db.add(AuditLog(
            actor_type='admin',
            actor_id=admin.id,
            action='document_upload',
            entity_type='driver_document',
            entity_id=f"{driver_id}:{document_type}",
            metadata_json={
                'filename': filename,
                'file_size': len(file_bytes),
                'mime_type': actual_mime,
                'expires_at': expires_at.isoformat() if expires_at else None,
            },
        ))

        db.commit()
        db.refresh(doc)

        # Clean up old file if replacing
        if old_storage_key and old_storage_key != storage_key:
            try:
                storage.delete(old_storage_key)
            except Exception:
                pass

        # Reconcile vehicle status
        self._reconcile_driver(db, driver_id)

        now = datetime.now(UTC)
        expiry_status, expiry_warning = self.calculate_expiry_status(
            SUPPORTED_DOCUMENT_TYPES[document_type]['has_expiry'], doc.expires_at, now
        )

        return DriverDocumentDetailResponse(
            id=doc.id,
            driver_id=driver_id,
            document_type=doc.document_type,
            label=SUPPORTED_DOCUMENT_TYPES[document_type]['label'],
            document_number=self.mask_document_number(document_type, doc.document_number, admin.role == 'super_admin'),
            verification_status=doc.verification_status,
            original_filename=doc.original_filename,
            file_size_bytes=doc.file_size_bytes,
            mime_type=doc.mime_type,
            uploaded_at=doc.created_at,
            expires_at=doc.expires_at,
            expiry_status=expiry_status,
            expiry_warning=expiry_warning,
            rejection_reason=None,
            reviewed_by=None,
            reviewed_at=None,
            has_file=True,
        )

    def preview_document(
        self,
        db: Session,
        admin: AdminUser,
        driver_id: int,
        document_type: str,
    ) -> DriverDocumentPreviewResponse:
        doc = db.scalar(select(DriverDocument).where(
            DriverDocument.driver_id == driver_id,
            DriverDocument.document_type == document_type,
        ))
        if not doc or not doc.storage_key:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file has not been uploaded yet.")

        # IDOR prevention: verify document matches driver
        if doc.driver_id != driver_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Document access denied.")

        storage = get_storage_service()
        if not storage.exists(doc.storage_key):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored document file could not be located.")

        signed_url = storage.generate_signed_url(doc.storage_key, expires_in_seconds=300)

        # Audit log entry for document preview
        db.add(AuditLog(
            actor_type='admin',
            actor_id=admin.id,
            action='document_preview',
            entity_type='driver_document',
            entity_id=f"{driver_id}:{document_type}",
            metadata_json={'ip': 'admin_session'},
        ))
        db.commit()

        return DriverDocumentPreviewResponse(
            driver_id=driver_id,
            document_type=document_type,
            preview_url=signed_url,
            expires_in_seconds=300,
        )

    def review_document(
        self,
        db: Session,
        admin: AdminUser,
        driver_id: int,
        document_type: str,
        status_decision: str,
        rejection_reason: str | None,
    ) -> DriverDocumentDetailResponse:
        if status_decision not in ('verified', 'rejected'):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Status must be 'verified' or 'rejected'.")

        if status_decision == 'rejected' and not (rejection_reason or '').strip():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A rejection reason is mandatory when rejecting a document.")

        doc = db.scalar(select(DriverDocument).where(
            DriverDocument.driver_id == driver_id,
            DriverDocument.document_type == document_type,
        ))
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver document was not found.")

        doc.verification_status = status_decision
        doc.review_note = rejection_reason.strip() if rejection_reason else None
        doc.rejection_reason = doc.review_note
        doc.reviewed_by = admin.email
        doc.reviewed_at = datetime.now(UTC)

        # Audit log entry
        db.add(AuditLog(
            actor_type='admin',
            actor_id=admin.id,
            action=f"document_{status_decision}",
            entity_type='driver_document',
            entity_id=f"{driver_id}:{document_type}",
            metadata_json={'rejection_reason': doc.rejection_reason},
        ))

        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Reconcile vehicle and driver status
        self._reconcile_driver(db, driver_id)

        now = datetime.now(UTC)
        expiry_status, expiry_warning = self.calculate_expiry_status(
            SUPPORTED_DOCUMENT_TYPES.get(document_type, {}).get('has_expiry', False), doc.expires_at, now
        )

        return DriverDocumentDetailResponse(
            id=doc.id,
            driver_id=driver_id,
            document_type=doc.document_type,
            label=SUPPORTED_DOCUMENT_TYPES.get(document_type, {}).get('label', document_type),
            document_number=self.mask_document_number(document_type, doc.document_number, admin.role == 'super_admin'),
            verification_status=doc.verification_status,
            original_filename=doc.original_filename,
            file_size_bytes=doc.file_size_bytes,
            mime_type=doc.mime_type,
            uploaded_at=doc.created_at,
            expires_at=doc.expires_at,
            expiry_status=expiry_status,
            expiry_warning=expiry_warning,
            rejection_reason=doc.rejection_reason,
            reviewed_by=doc.reviewed_by,
            reviewed_at=doc.reviewed_at,
            has_file=bool(doc.storage_key),
        )

    def delete_document(
        self,
        db: Session,
        admin: AdminUser,
        driver_id: int,
        document_type: str,
    ) -> None:
        doc = db.scalar(select(DriverDocument).where(
            DriverDocument.driver_id == driver_id,
            DriverDocument.document_type == document_type,
        ))
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver document not found.")

        # Delete file from storage
        if doc.storage_key:
            try:
                get_storage_service().delete(doc.storage_key)
            except Exception as error:
                logger.warning("Could not delete file from storage: %s", error)

        # Delete DB row
        db.delete(doc)

        # Audit log entry
        db.add(AuditLog(
            actor_type='admin',
            actor_id=admin.id,
            action='document_deleted',
            entity_type='driver_document',
            entity_id=f"{driver_id}:{document_type}",
        ))

        db.commit()

        # Reconcile vehicle and driver status
        self._reconcile_driver(db, driver_id)

    def check_expired_mandatory_documents(self, db: Session, driver_id: int) -> list[str]:
        """Checks for any expired mandatory documents that must block the driver from operating."""
        now = datetime.now(UTC)
        docs = db.scalars(select(DriverDocument).where(DriverDocument.driver_id == driver_id)).all()
        expired: list[str] = []
        for doc in docs:
            if doc.document_type in MANDATORY_DOCUMENT_TYPES and doc.expires_at:
                aware = doc.expires_at if doc.expires_at.tzinfo else doc.expires_at.replace(tzinfo=UTC)
                if aware < now:
                    label = SUPPORTED_DOCUMENT_TYPES.get(doc.document_type, {}).get('label', doc.document_type)
                    expired.append(f"{label} (expired {aware.strftime('%d %b %Y')})")
        return expired

    def _reconcile_driver(self, db: Session, driver_id: int) -> None:
        driver = db.get(Driver, driver_id)
        if not driver:
            return

        vehicle = db.scalar(select(Vehicle).join(
            DriverVehicleAssignment, DriverVehicleAssignment.vehicle_id == Vehicle.id,
        ).where(
            DriverVehicleAssignment.driver_id == driver_id,
            DriverVehicleAssignment.ended_at.is_(None),
        ).order_by(DriverVehicleAssignment.started_at.desc()))

        docs = db.scalars(select(DriverDocument).where(DriverDocument.driver_id == driver_id)).all()
        doc_statuses = {d.document_type: d.verification_status for d in docs}

        now = datetime.now(UTC)
        has_expired = False
        for d in docs:
            if d.document_type in MANDATORY_DOCUMENT_TYPES and d.expires_at:
                aware = d.expires_at if d.expires_at.tzinfo else d.expires_at.replace(tzinfo=UTC)
                if aware < now:
                    has_expired = True

        if vehicle:
            if any(s == 'rejected' for s in doc_statuses.values()):
                vehicle.verification_status = 'rejected'
            elif has_expired:
                vehicle.verification_status = 'expired'
            elif (
                MANDATORY_DOCUMENT_TYPES <= doc_statuses.keys()
                and all(doc_statuses[t] == 'verified' for t in MANDATORY_DOCUMENT_TYPES)
            ):
                vehicle.verification_status = 'verified'
            else:
                vehicle.verification_status = 'pending'
            db.add(vehicle)

            if vehicle.verification_status == 'verified' and driver.status == 'pending':
                driver.status = 'active'
                db.add(driver)
            elif vehicle.verification_status in ('expired', 'rejected') and driver.is_online:
                driver.is_online = False
                db.add(driver)

        db.commit()

