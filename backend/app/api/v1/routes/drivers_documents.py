from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.driver_auth import get_current_driver
from app.db import get_db
from app.models.ride_hailing import Driver
from app.schemas.driver_documents import DriverDocumentListResponse
from app.services.document_management_service import DocumentManagementService

router = APIRouter(prefix="/drivers/me/documents", tags=["driver-documents"])
service = DocumentManagementService()


@router.get("", response_model=DriverDocumentListResponse)
def get_my_documents(
    driver: Driver = Depends(get_current_driver),
    db: Session = Depends(get_db),
) -> DriverDocumentListResponse:
    """
    Read-only view of the driver's verified document compliance status.
    Drivers do not upload documents themselves; physical verification is conducted by Virgo executives.
    """
    return service.get_driver_document_list(db, driver.id, requester_role="driver")

