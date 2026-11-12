from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.driver_auth import get_current_driver
from app.db import get_db
from app.models.ride_hailing import Driver, Ride
from app.schemas.booking import DriverActiveRideResponse, DriverLocationUpdateRequest, DriverRideOfferDecisionRequest, DriverRideOfferDecisionResponse, DriverRideOfferResponse, RideActionRequest, RideCancellationRequest, RideMutationResponse, RideRatingRequest, RideRatingResponse, RideSummaryResponse
from app.services.ride_matching_service import RideMatchingService
from app.services.ride_lifecycle_service import RideLifecycleService

router = APIRouter(prefix='/drivers/me', tags=['driver-matching'])
service = RideMatchingService()
lifecycle_service = RideLifecycleService()


@router.put('/location', status_code=204)
def update_location(request: DriverLocationUpdateRequest, driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> None:
    service.update_driver_location(db, driver, request.latitude, request.longitude, request.heading_degrees, request.accuracy_meters, request.speed_mps, request.recorded_at)


@router.get('/ride-offers/current', response_model=DriverRideOfferResponse | None)
def current_offer(driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> DriverRideOfferResponse | None:
    return service.current_offer(db, driver)


@router.post('/ride-offers/{offer_id}/response', response_model=DriverRideOfferDecisionResponse)
def respond_to_offer(offer_id: int, request: DriverRideOfferDecisionRequest, driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> DriverRideOfferDecisionResponse:
    return service.respond(db, driver, offer_id, request.decision)


@router.get('/rides/active', response_model=DriverActiveRideResponse | None)
def active_ride(driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> DriverActiveRideResponse | None:
    return lifecycle_service.driver_snapshot(db, driver)


@router.post('/rides/{ride_id}/cancel', response_model=RideMutationResponse)
def cancel_ride(ride_id: int, request: RideCancellationRequest, driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> RideMutationResponse:
    return lifecycle_service.cancel_by_driver(db, driver, ride_id, request.reason, request.confirm)


@router.post('/rides/{ride_id}/actions', response_model=RideMutationResponse)
def ride_action(ride_id: int, request: RideActionRequest, driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> RideMutationResponse:
    return lifecycle_service.action(db, driver, ride_id, request.action, request.start_otp, request.payment_method)


@router.get('/rides/{ride_id}/summary', response_model=RideSummaryResponse)
def ride_summary(ride_id: int, driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> RideSummaryResponse:
    ride = db.scalar(select(Ride).where(Ride.id == ride_id, Ride.driver_id == driver.id))
    if not ride:
        raise HTTPException(status_code=404, detail='Ride was not found.')
    return lifecycle_service.summary(db, ride, 'driver')


@router.post('/rides/{ride_id}/rating', response_model=RideRatingResponse)
def rate_passenger(ride_id: int, request: RideRatingRequest, driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> RideRatingResponse:
    ride = db.scalar(select(Ride).where(Ride.id == ride_id, Ride.driver_id == driver.id))
    if not ride:
        raise HTTPException(status_code=404, detail='Ride was not found.')
    return lifecycle_service.rate(db, ride, 'driver', request.score, request.comment)
