from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


VehiclePreference = Literal['sedan', 'suv', 'muv']
OutstationStatus = Literal['requested', 'confirmed', 'driver_assigned', 'completed', 'cancelled', 'rejected']


class OutstationLocation(BaseModel):
    place_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=160)
    formatted_address: str = Field(min_length=5, max_length=512)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class OutstationBookingCreate(BaseModel):
    scheduled_at: datetime
    pickup: OutstationLocation
    destination: OutstationLocation
    preferred_vehicle_type: VehiclePreference | None = None


class OutstationEstimateResponse(BaseModel):
    distance_km: float
    duration_minutes: int
    estimated_fare_paise: int
    route_geojson: dict
    disclaimer: str = 'Estimated fare only. The support team will confirm the booking and final estimate.'


class OutstationBookingResponse(BaseModel):
    id: int
    scheduled_at: datetime
    pickup_address: str
    destination_address: str
    preferred_vehicle_type: str | None
    status: str
    estimated_distance_km: float | None
    estimated_fare_paise: int | None
    support_note: str | None
    driver_name: str | None
    driver_phone_number: str | None
    vehicle_name: str | None
    vehicle_registration_number: str | None
    can_cancel: bool
    created_at: datetime
    passenger_name: str
    passenger_phone_number: str
    pickup_latitude: float | None
    pickup_longitude: float | None
    destination_latitude: float | None
    destination_longitude: float | None
    route_geojson: dict | None


class OutstationCancellationRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=255)


class AdminOutstationUpdate(BaseModel):
    status: Literal['confirmed', 'driver_assigned', 'completed', 'cancelled', 'rejected']
    estimated_distance_km: float | None = Field(default=None, ge=150, le=5000)
    driver_phone_number: str | None = None
    support_note: str | None = Field(default=None, max_length=1000)

    @field_validator('driver_phone_number')
    @classmethod
    def normalize_driver_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        digits = ''.join(character for character in value if character.isdigit())
        if len(digits) == 12 and digits.startswith('91'):
            digits = digits[2:]
        if len(digits) != 10 or digits[0] not in '6789':
            raise ValueError('Enter a valid 10-digit Indian driver mobile number.')
        return digits


class EligibleOutstationDriverResponse(BaseModel):
    full_name: str
    phone_number: str
    operating_city: str | None
    rating: float
    completed_rides: int
    vehicle_name: str
    vehicle_registration_number: str
    vehicle_category: str
    seat_count: int


class DriverOutstationAssignmentResponse(BaseModel):
    id: int
    status: str
    scheduled_at: datetime
    pickup_address: str
    destination_address: str
    passenger_name: str
    passenger_phone_number: str
    estimated_distance_km: float
    estimated_fare_paise: int
    vehicle_name: str
    vehicle_registration_number: str
