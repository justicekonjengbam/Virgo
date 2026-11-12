from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_passenger
from app.db import get_db
from app.models.user import Passenger
from app.schemas.profile import PassengerProfileResponse, PassengerProfileUpdateRequest
from app.services.passenger_profile_service import PassengerProfileService

router = APIRouter(prefix='/passengers/me/profile', tags=['passenger-profile'])
service = PassengerProfileService()


@router.get('', response_model=PassengerProfileResponse)
def get_profile(passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> PassengerProfileResponse:
    return service.get(db, passenger)


@router.patch('', response_model=PassengerProfileResponse)
def update_profile(request: PassengerProfileUpdateRequest, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> PassengerProfileResponse:
    return service.update(db, passenger, request)
