from datetime import datetime

from pydantic import BaseModel


class PlaceResponse(BaseModel):
    id: int
    label: str
    formatted_address: str
    latitude: float
    longitude: float


class RideCategoryResponse(BaseModel):
    id: int
    code: str
    display_name: str
    seat_count: int
    base_fare_paise: int
    estimated_arrival_minutes: int
    icon_key: str


class RecentRideResponse(BaseModel):
    id: int
    pickup_address: str
    destination_address: str
    completed_at: datetime | None
    final_duration_seconds: int | None
    fare_paise: int


class HomeResponse(BaseModel):
    passenger_name: str
    saved_places: list[PlaceResponse]
    ride_categories: list[RideCategoryResponse]
    recent_rides: list[RecentRideResponse]


class PlaceSuggestionResponse(BaseModel):
    place_id: str
    description: str
