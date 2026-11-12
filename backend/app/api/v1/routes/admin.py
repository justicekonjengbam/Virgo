from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies.admin_auth import get_current_admin, require_admin_permission
from app.db import get_db
from app.models.user import AdminUser
from app.schemas.admin import (
    AdminAssignDriverRequest,
    AdminAuthResponse,
    AdminCancelRideRequest,
    AdminDriverDocumentResponse,
    AdminDriverResponse,
    AdminLoginRequest,
    AdminPasswordChangeRequest,
    AdminPasswordChangeResponse,
    AdminProfileResponse,
    AdminRateCardResponse,
    AdminRateCardUpdateRequest,
    AdminRideDetailResponse,
    AdminRideListItemResponse,
    AdminSupportTicketResponse,
    AdminSupportTicketUpdate,
)
from app.schemas.admin_review import DriverDocumentReviewRequest, DriverDocumentReviewResponse
from app.schemas.driver_documents import (
    DriverDocumentDetailResponse,
    DriverDocumentListResponse,
    DriverDocumentPreviewResponse,
)
from app.services.admin_auth_service import AdminAuthService
from app.services.admin_operations_service import AdminOperationsService
from app.services.document_management_service import DocumentManagementService
from app.services.driver_document_review_service import DriverDocumentReviewService

router = APIRouter(prefix='/admin', tags=['admin'])
auth_service = AdminAuthService()
operations_service = AdminOperationsService()
document_service = DriverDocumentReviewService()
document_mgmt_service = DocumentManagementService()


@router.post('/auth/login', response_model=AdminAuthResponse)
def login(request: AdminLoginRequest, db: Session = Depends(get_db)) -> AdminAuthResponse:
    return auth_service.login(db, request)


@router.get('/auth/me', response_model=AdminProfileResponse)
def me(admin: AdminUser = Depends(get_current_admin)) -> AdminProfileResponse:
    return auth_service._profile(admin)


@router.post('/auth/change-password', response_model=AdminPasswordChangeResponse)
def change_password(request: AdminPasswordChangeRequest, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)) -> AdminPasswordChangeResponse:
    auth_service.change_password(db, admin, request)
    return AdminPasswordChangeResponse(message='Password changed. Sign in again with your new password.')


@router.get('/drivers', response_model=list[AdminDriverResponse])
def list_drivers(driver_status: str | None = None, _: AdminUser = Depends(require_admin_permission('drivers:read')), db: Session = Depends(get_db)) -> list[AdminDriverResponse]:
    return operations_service.drivers(db, driver_status)


@router.get('/driver-documents', response_model=list[AdminDriverDocumentResponse])
def list_driver_documents(status_filter: str | None = None, _: AdminUser = Depends(require_admin_permission('drivers:read')), db: Session = Depends(get_db)) -> list[AdminDriverDocumentResponse]:
    return operations_service.documents(db, status_filter)


@router.get('/drivers/{driver_id}/documents', response_model=DriverDocumentListResponse)
def get_driver_documents(
    driver_id: int,
    admin: AdminUser = Depends(require_admin_permission('drivers:read')),
    db: Session = Depends(get_db),
) -> DriverDocumentListResponse:
    return document_mgmt_service.get_driver_document_list(db, driver_id, requester_role=admin.role)


@router.post('/drivers/{driver_id}/documents/{document_type}/upload', response_model=DriverDocumentDetailResponse, status_code=status.HTTP_201_CREATED)
async def upload_driver_document(
    driver_id: int,
    document_type: str,
    file: UploadFile = File(...),
    document_number: str = Form(...),
    expires_at: str | None = Form(None),
    admin: AdminUser = Depends(require_admin_permission('documents:upload')),
    db: Session = Depends(get_db),
) -> DriverDocumentDetailResponse:
    parsed_expires_at = None
    if expires_at and expires_at.strip():
        try:
            parsed_expires_at = datetime.fromisoformat(expires_at.strip().replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid date format for expiry. Use ISO format (YYYY-MM-DD).")
    contents = await file.read()
    return document_mgmt_service.upload_document(
        db=db,
        admin=admin,
        driver_id=driver_id,
        document_type=document_type,
        file_bytes=contents,
        filename=file.filename or 'document.pdf',
        declared_content_type=file.content_type,
        document_number=document_number,
        expires_at=parsed_expires_at,
    )


@router.get('/drivers/{driver_id}/documents/{document_type}/preview', response_model=DriverDocumentPreviewResponse)
def preview_driver_document(
    driver_id: int,
    document_type: str,
    admin: AdminUser = Depends(require_admin_permission('documents:review')),
    db: Session = Depends(get_db),
) -> DriverDocumentPreviewResponse:
    return document_mgmt_service.preview_document(db, admin, driver_id, document_type)


@router.put('/drivers/{driver_id}/documents/{document_type}/review', response_model=DriverDocumentDetailResponse)
def review_driver_document(
    driver_id: int,
    document_type: str,
    request: DriverDocumentReviewRequest,
    admin: AdminUser = Depends(require_admin_permission('documents:review')),
    db: Session = Depends(get_db),
) -> DriverDocumentDetailResponse:
    return document_mgmt_service.review_document(
        db, admin, driver_id, document_type, request.status, request.review_note
    )


@router.delete('/drivers/{driver_id}/documents/{document_type}', status_code=status.HTTP_204_NO_CONTENT)
def delete_driver_document(
    driver_id: int,
    document_type: str,
    admin: AdminUser = Depends(require_admin_permission('documents:delete')),
    db: Session = Depends(get_db),
) -> None:
    document_mgmt_service.delete_document(db, admin, driver_id, document_type)


@router.get('/support-tickets', response_model=list[AdminSupportTicketResponse])
def list_support_tickets(ticket_status: str | None = None, _: AdminUser = Depends(require_admin_permission('support:manage')), db: Session = Depends(get_db)) -> list[AdminSupportTicketResponse]:
    return operations_service.tickets(db, ticket_status)


@router.patch('/support-tickets/{ticket_id}', response_model=AdminSupportTicketResponse)
def update_support_ticket(ticket_id: int, request: AdminSupportTicketUpdate, admin: AdminUser = Depends(require_admin_permission('support:manage')), db: Session = Depends(get_db)) -> AdminSupportTicketResponse:
    return operations_service.update_ticket(db, ticket_id, request, admin.id)


# ==================== Milestone 3: Local Ride Operations ====================


@router.get('/rides', response_model=list[AdminRideListItemResponse])
def list_rides(
    status_filter: str | None = None,
    search: str | None = None,
    _: AdminUser = Depends(require_admin_permission('rides:read')),
    db: Session = Depends(get_db),
) -> list[AdminRideListItemResponse]:
    return operations_service.rides(db, status_filter, search)


@router.get('/rides/{ride_id}', response_model=AdminRideDetailResponse)
def get_ride_detail(
    ride_id: int,
    _: AdminUser = Depends(require_admin_permission('rides:read')),
    db: Session = Depends(get_db),
) -> AdminRideDetailResponse:
    return operations_service.ride_detail(db, ride_id)


@router.post('/rides/{ride_id}/assign-driver', response_model=AdminRideDetailResponse)
def assign_driver(
    ride_id: int,
    request: AdminAssignDriverRequest,
    admin: AdminUser = Depends(require_admin_permission('rides:manage')),
    db: Session = Depends(get_db),
) -> AdminRideDetailResponse:
    return operations_service.assign_driver(
        db=db,
        ride_id=ride_id,
        driver_id=request.driver_id,
        driver_phone=request.driver_phone,
        admin_id=admin.id,
    )


@router.post('/rides/{ride_id}/cancel', response_model=AdminRideDetailResponse)
def cancel_ride(
    ride_id: int,
    request: AdminCancelRideRequest,
    admin: AdminUser = Depends(require_admin_permission('rides:manage')),
    db: Session = Depends(get_db),
) -> AdminRideDetailResponse:
    return operations_service.cancel_ride(db=db, ride_id=ride_id, reason=request.reason, admin_id=admin.id)


@router.get('/rate-cards', response_model=list[AdminRateCardResponse])
def list_rate_cards(
    _: AdminUser = Depends(require_admin_permission('rate_cards:read')),
    db: Session = Depends(get_db),
) -> list[AdminRateCardResponse]:
    return operations_service.rate_cards(db)


@router.put('/rate-cards/{card_id}', response_model=AdminRateCardResponse)
def update_rate_card(
    card_id: int,
    request: AdminRateCardUpdateRequest,
    admin: AdminUser = Depends(require_admin_permission('rate_cards:manage')),
    db: Session = Depends(get_db),
) -> AdminRateCardResponse:
    return operations_service.update_rate_card(db=db, card_id=card_id, request=request, admin_id=admin.id)

