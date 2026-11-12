from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_passenger
from app.db import get_db
from app.models.user import Passenger
from app.models.ride_hailing import Ride
from app.schemas.booking import LocationOptionResponse, PassengerRideStatusResponse, RideBookingResponse, RideCancellationRequest, RideEstimateRequest, RideEstimateResponse, RideMutationResponse, RideRatingRequest, RideRatingResponse, RideSummaryResponse, UpdateSavedPlaceRequest
from app.schemas.home import PlaceResponse
from app.services.booking_service import BookingService
from app.services.ride_matching_service import RideMatchingService
from app.services.ride_lifecycle_service import RideLifecycleService

router = APIRouter(prefix='/passengers/me', tags=['passenger-booking'])
service = BookingService()
matching_service = RideMatchingService()
lifecycle_service = RideLifecycleService()


@router.get('/locations', response_model=list[LocationOptionResponse])
def get_locations(_: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> list[LocationOptionResponse]:
    return service.locations(db)


@router.post('/ride-estimates', response_model=RideEstimateResponse)
def estimate_ride(request: RideEstimateRequest, _: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> RideEstimateResponse:
    return service.estimate(db, request)


@router.post('/rides', response_model=RideBookingResponse, status_code=status.HTTP_201_CREATED)
def book_ride(request: RideEstimateRequest, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> RideBookingResponse:
    return service.book(db, passenger, request)


@router.get('/rides/active/current', response_model=PassengerRideStatusResponse | None)
def get_active_ride(passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> PassengerRideStatusResponse | None:
    ride = lifecycle_service.passenger_active(db, passenger)
    return matching_service.passenger_status(db, ride) if ride else None


@router.get('/rides/{ride_id}/status', response_model=PassengerRideStatusResponse)
def get_ride_status(ride_id: int, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> PassengerRideStatusResponse:
    ride = db.scalar(select(Ride).where(Ride.id == ride_id, Ride.passenger_id == passenger.id))
    if not ride:
        raise HTTPException(status_code=404, detail='Ride was not found.')
    return matching_service.passenger_status(db, ride)


@router.post('/rides/{ride_id}/cancel', response_model=RideMutationResponse)
def cancel_ride(ride_id: int, request: RideCancellationRequest, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> RideMutationResponse:
    return lifecycle_service.cancel_by_passenger(db, passenger, ride_id, request.reason, request.confirm)


@router.get('/rides/{ride_id}/summary', response_model=RideSummaryResponse)
def ride_summary(ride_id: int, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> RideSummaryResponse:
    ride = db.scalar(select(Ride).where(Ride.id == ride_id, Ride.passenger_id == passenger.id))
    if not ride:
        raise HTTPException(status_code=404, detail='Ride was not found.')
    return lifecycle_service.summary(db, ride, 'passenger')


@router.post('/rides/{ride_id}/rating', response_model=RideRatingResponse)
def rate_driver(ride_id: int, request: RideRatingRequest, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> RideRatingResponse:
    ride = db.scalar(select(Ride).where(Ride.id == ride_id, Ride.passenger_id == passenger.id))
    if not ride:
        raise HTTPException(status_code=404, detail='Ride was not found.')
    return lifecycle_service.rate(db, ride, 'passenger', request.score, request.comment)


@router.patch('/saved-places/{saved_place_id}', response_model=PlaceResponse)
def update_saved_place(saved_place_id: int, request: UpdateSavedPlaceRequest, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> PlaceResponse:
    return service.update_saved_place(db, passenger, saved_place_id, request)
