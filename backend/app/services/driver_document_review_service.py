from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.driver_repository import DriverRepository
from app.models.ride_hailing import Driver
from app.schemas.admin_review import DriverDocumentReviewRequest, DriverDocumentReviewResponse


class DriverDocumentReviewService:
    """Applies an admin decision and derives active-vehicle verification atomically."""

    required_document_types = {
        'driving_licence', 'vehicle_registration', 'aadhaar', 'vehicle_insurance',
    }

    def __init__(self, repository: DriverRepository | None = None):
        self.repository = repository or DriverRepository()

    def review(
        self,
        db: Session,
        driver_id: int,
        document_type: str,
        request: DriverDocumentReviewRequest,
        reviewer: str,
    ) -> DriverDocumentReviewResponse:
        document = self.repository.get_document(db, driver_id, document_type)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Driver document was not found.')

        document.verification_status = request.status
        document.review_note = request.review_note.strip() if request.review_note else None
        document.reviewed_by = reviewer
        document.reviewed_at = datetime.now(UTC)

        vehicle = self.repository.get_active_vehicle(db, driver_id)
        driver = db.get(Driver, driver_id)
        documents = self.repository.get_documents(db, driver_id)
        if vehicle:
            statuses = {item.document_type: item.verification_status for item in documents}
            if any(value == 'rejected' for value in statuses.values()):
                vehicle.verification_status = 'rejected'
            elif self.required_document_types <= statuses.keys() and all(
                statuses[document_name] == 'verified' for document_name in self.required_document_types
            ):
                vehicle.verification_status = 'verified'
            else:
                vehicle.verification_status = 'pending'
            db.add(vehicle)
            if driver and vehicle.verification_status == 'verified' and driver.status == 'pending':
                driver.status = 'active'
                db.add(driver)

        db.add(document)
        db.commit()
        db.refresh(document)
        return DriverDocumentReviewResponse(
            driver_id=driver_id,
            document_type=document.document_type,
            document_status=document.verification_status,
            vehicle_verification_status=vehicle.verification_status if vehicle else 'pending',
            reviewed_at=document.reviewed_at,
            review_note=document.review_note,
        )
