from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_passenger
from app.db import get_db
from app.models.user import Passenger
from app.schemas.home import HomeResponse
from app.services.home_service import HomeService

router = APIRouter(prefix='/passengers/me', tags=['passenger-home'])
service = HomeService()


@router.get('/home', response_model=HomeResponse)
def get_home(
    passenger: Passenger = Depends(get_current_passenger),
    db: Session = Depends(get_db),
) -> HomeResponse:
    return service.get_home(db, passenger)
