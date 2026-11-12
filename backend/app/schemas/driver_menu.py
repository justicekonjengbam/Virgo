from datetime import datetime

from pydantic import BaseModel, Field


class DriverRideRequestResponse(BaseModel):
    pickup_address: str
    destination_address: str
    estimated_distance_km: float = Field(ge=0)
    expected_fare_paise: int = Field(ge=0)
    pickup_minutes_away: int = Field(ge=0)


class DriverTripHistoryItemResponse(BaseModel):
    id: int
    pickup_address: str
    destination_address: str
    category: str
    completed_at: datetime | None
    fare_paise: int


class DriverSupportArticleResponse(BaseModel):
    id: str
    title: str
    body: str
