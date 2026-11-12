from fastapi import APIRouter, Depends, Query

from app.api.dependencies.auth import get_current_passenger
from app.models.user import Passenger
from app.schemas.maps import GeocodedPlaceResponse, MapConfigResponse
from app.services.map_provider_service import MapProviderService

router = APIRouter(prefix='/maps', tags=['maps'])
service = MapProviderService()


@router.get('/config', response_model=MapConfigResponse)
def map_config() -> MapConfigResponse:
    return service.config()


@router.get('/places', response_model=list[GeocodedPlaceResponse])
def search_places(
    q: str = Query(min_length=2, max_length=120),
    scope: str = Query(default='local', pattern='^(local|outstation)$'),
    _: Passenger = Depends(get_current_passenger),
) -> list[GeocodedPlaceResponse]:
    return service.search(q.strip(), outstation=scope == 'outstation')


@router.get('/reverse', response_model=GeocodedPlaceResponse)
def reverse_geocode(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    scope: str = Query(default='local', pattern='^(local|outstation)$'),
    _: Passenger = Depends(get_current_passenger),
) -> GeocodedPlaceResponse:
    return service.reverse(latitude, longitude, outstation=scope == 'outstation')
