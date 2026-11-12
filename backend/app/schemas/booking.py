from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class LocationOptionResponse(BaseModel):
    id: int | None = None
    place_id: str | None = None
    name: str
    formatted_address: str
    latitude: float
    longitude: float


class SelectedPlaceRequest(BaseModel):
    place_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=160)
    formatted_address: str = Field(min_length=1, max_length=512)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class RideEstimateRequest(BaseModel):
    pickup_location_id: int | None = Field(default=None, gt=0)
    destination_location_id: int | None = Field(default=None, gt=0)
    pickup: SelectedPlaceRequest | None = None
    destination: SelectedPlaceRequest | None = None
    category_id: int

    @model_validator(mode='after')
    def validate_location_pair(self):
        catalog_pair = self.pickup_location_id is not None and self.destination_location_id is not None
        live_pair = self.pickup is not None and self.destination is not None
        if catalog_pair == live_pair:
            raise ValueError('Provide either two catalog locations or two selected places.')
        return self


class UpdateSavedPlaceRequest(BaseModel):
    location_id: int | None = Field(default=None, gt=0)
    location: SelectedPlaceRequest | None = None

    @model_validator(mode='after')
    def validate_location(self):
        if (self.location_id is None) == (self.location is None):
            raise ValueError('Provide one saved-place location.')
        return self


class FareItemResponse(BaseModel):
    label: str
    amount_paise: int


class RideEstimateResponse(BaseModel):
    pickup: LocationOptionResponse
    destination: LocationOptionResponse
    category_name: str
    distance_km: float
    duration_minutes: int
    fare_paise: int
    fare_items: list[FareItemResponse]
    route_geojson: dict | None = None


class RideBookingResponse(BaseModel):
    ride_id: int
    status: str
    pickup_address: str
    destination_address: str
    fare_paise: int
    requested_at: datetime
    message: str


class PassengerRideStatusResponse(BaseModel):
    ride_id: int
    status: str
    message: str
    pickup_address: str
    destination_address: str
    driver_name: str | None = None
    vehicle_name: str | None = None
    vehicle_registration_number: str | None = None
    driver_arrival_minutes: int | None = None
    pickup_latitude: float
    pickup_longitude: float
    destination_latitude: float
    destination_longitude: float
    driver_latitude: float | None = None
    driver_longitude: float | None = None
    driver_heading_degrees: int | None = None
    route_geojson: dict | None = None
    can_cancel: bool = False
    can_end: bool = False
    ride_start_otp: str | None = None
    cancellation_reason: str | None = None


class DriverLocationUpdateRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    heading_degrees: int | None = Field(default=None, ge=0, le=359)
    accuracy_meters: float | None = Field(default=None, ge=0, le=500)
    speed_mps: float | None = Field(default=None, ge=0, le=80)
    recorded_at: datetime | None = None


class DriverRideOfferResponse(BaseModel):
    offer_id: int
    ride_id: int
    pickup_address: str
    destination_address: str
    estimated_distance_km: float
    expected_fare_paise: int
    pickup_minutes_away: int
    expires_at: datetime
    pickup_latitude: float
    pickup_longitude: float
    destination_latitude: float
    destination_longitude: float


class DriverRideOfferDecisionRequest(BaseModel):
    decision: str = Field(pattern='^(accepted|declined)$')


class DriverRideOfferDecisionResponse(BaseModel):
    ride_id: int
    ride_status: str
    message: str


class RideCancellationRequest(BaseModel):
    reason: str = Field(pattern='^(changed_plans|driver_delay|wrong_pickup|safety_concern|vehicle_issue|passenger_no_show|emergency|other)$')
    confirm: bool


class RideActionRequest(BaseModel):
    action: str = Field(pattern='^(arrived|start|complete|confirm_payment)$')
    start_otp: str | None = Field(default=None, pattern='^[0-9]{4}$')
    payment_method: str | None = Field(default='cash', pattern='^(cash|upi)$')


class DriverActiveRideResponse(BaseModel):
    ride_id: int
    status: str
    pickup_address: str
    destination_address: str
    pickup_latitude: float
    pickup_longitude: float
    destination_latitude: float
    destination_longitude: float
    passenger_name: str
    route_geojson: dict | None = None
    can_cancel: bool
    can_end: bool


class RideMutationResponse(BaseModel):
    ride_id: int
    status: str
    message: str


class FareSummaryItemResponse(BaseModel):
    label: str
    amount_paise: int


class RideSummaryResponse(BaseModel):
    ride_id: int
    status: str
    pickup_address: str
    destination_address: str
    distance_km: float
    duration_minutes: int
    fare_paise: int
    commission_paise: int | None = None
    driver_net_paise: int | None = None
    waiting_charge_paise: int | None = None
    payment_status: str | None = None
    payment_method: str | None = None
    fare_items: list[FareSummaryItemResponse]
    passenger_rating_submitted: bool
    driver_rating_submitted: bool


class RideRatingRequest(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=300)


class RideRatingResponse(BaseModel):
    ride_id: int
    score: int
    message: str
