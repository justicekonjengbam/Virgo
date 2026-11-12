from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.admin_auth import require_admin_permission
from app.api.dependencies.auth import get_current_passenger
from app.api.dependencies.driver_auth import get_current_driver
from app.db import get_db
from app.models.ride_hailing import Driver
from app.models.user import AdminUser, Passenger
from app.schemas.outstation import AdminOutstationUpdate, DriverOutstationAssignmentResponse, EligibleOutstationDriverResponse, OutstationBookingCreate, OutstationBookingResponse, OutstationCancellationRequest, OutstationEstimateResponse
from app.services.outstation_service import OutstationService

router = APIRouter(tags=['outstation'])
service = OutstationService()


@router.post('/passengers/me/outstation-estimates', response_model=OutstationEstimateResponse)
def estimate_booking(request: OutstationBookingCreate, _: Passenger = Depends(get_current_passenger)) -> OutstationEstimateResponse:
    return service.estimate(request)


@router.post('/passengers/me/outstation-bookings', response_model=OutstationBookingResponse, status_code=201)
def create_booking(request: OutstationBookingCreate, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> OutstationBookingResponse:
    return service.create(db, passenger, request)


@router.get('/passengers/me/outstation-bookings', response_model=list[OutstationBookingResponse])
def passenger_bookings(passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> list[OutstationBookingResponse]:
    return service.passenger_list(db, passenger)


@router.post('/passengers/me/outstation-bookings/{booking_id}/cancel', response_model=OutstationBookingResponse)
def cancel_booking(booking_id: int, request: OutstationCancellationRequest, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> OutstationBookingResponse:
    return service.cancel(db, passenger, booking_id, request.reason)


@router.get('/admin/outstation-bookings', response_model=list[OutstationBookingResponse])
def admin_bookings(status_filter: str | None = None, _: AdminUser = Depends(require_admin_permission('outstation:manage')), db: Session = Depends(get_db)) -> list[OutstationBookingResponse]:
    return service.admin_list(db, status_filter)


@router.patch('/admin/outstation-bookings/{booking_id}', response_model=OutstationBookingResponse)
def update_booking(booking_id: int, request: AdminOutstationUpdate, admin: AdminUser = Depends(require_admin_permission('outstation:manage')), db: Session = Depends(get_db)) -> OutstationBookingResponse:
    return service.admin_update(db, booking_id, request, admin.id)


@router.get('/admin/outstation-bookings/{booking_id}/eligible-drivers', response_model=list[EligibleOutstationDriverResponse])
def eligible_drivers(booking_id: int, _: AdminUser = Depends(require_admin_permission('outstation:manage')), db: Session = Depends(get_db)) -> list[EligibleOutstationDriverResponse]:
    return service.eligible_drivers(db, booking_id)


@router.get('/drivers/me/outstation-assignments', response_model=list[DriverOutstationAssignmentResponse])
def driver_assignments(driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> list[DriverOutstationAssignmentResponse]:
    return service.driver_assignments(db, driver)
