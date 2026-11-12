from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.driver_auth import get_current_driver
from app.db import get_db
from app.models.ride_hailing import Driver
from app.schemas.driver_menu import DriverRideRequestResponse, DriverSupportArticleResponse, DriverTripHistoryItemResponse
from app.services.driver_menu_service import DriverMenuService

router = APIRouter(prefix='/drivers/menu', tags=['driver-menu'])
service = DriverMenuService()


@router.get('/ride-request', response_model=DriverRideRequestResponse)
def get_ride_request(_: Driver = Depends(get_current_driver)) -> DriverRideRequestResponse:
    return service.current_ride_request()


@router.get('/trip-history', response_model=list[DriverTripHistoryItemResponse])
def get_trip_history(driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> list[DriverTripHistoryItemResponse]:
    return service.trip_history(db, driver.id)


@router.get('/support', response_model=list[DriverSupportArticleResponse])
def get_support(_: Driver = Depends(get_current_driver)) -> list[DriverSupportArticleResponse]:
    return service.support()
