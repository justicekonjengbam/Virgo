from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.driver_auth import get_current_driver
from app.db import get_db
from app.models.ride_hailing import Driver
from app.schemas.driver_dashboard import DriverAvailabilityRequest, DriverDashboardResponse
from app.services.driver_dashboard_service import DriverDashboardService

router = APIRouter(prefix="/drivers/dashboard", tags=["driver-dashboard"])
service = DriverDashboardService()


@router.get("", response_model=DriverDashboardResponse)
def get_dashboard(driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)) -> DriverDashboardResponse:
    return service.dashboard(db, driver)


@router.put("/availability", response_model=DriverDashboardResponse)
def update_availability(
    request: DriverAvailabilityRequest,
    driver: Driver = Depends(get_current_driver),
    db: Session = Depends(get_db),
) -> DriverDashboardResponse:
    return service.set_availability(db, driver, request.is_online)
