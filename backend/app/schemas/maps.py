from pydantic import BaseModel


class MapConfigResponse(BaseModel):
    style_url: str
    attribution: str
    service_area: list[float]
    service_center: list[float]
    service_radius_km: float
    offline_mode: bool = False


class GeocodedPlaceResponse(BaseModel):
    place_id: str
    name: str
    formatted_address: str
    latitude: float
    longitude: float


class RouteResponse(BaseModel):
    distance_meters: int
    duration_seconds: int
    geometry: dict
    toll_fare_paise: int = 0
    is_estimated: bool = False
    route_type: str = 'road'
