from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_passenger
from app.db import get_db
from app.models.user import Passenger
from app.schemas.emergency import EmergencyContactResponse
from app.services.emergency_contact_service import EmergencyContactService

router = APIRouter(prefix='/passengers/me/emergency-contacts', tags=['passenger-emergency-contacts'])
service = EmergencyContactService()


@router.get('', response_model=list[EmergencyContactResponse])
def get_emergency_contacts(passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> list[EmergencyContactResponse]:
    return service.list_for_passenger(db, passenger)
