from pydantic import BaseModel, Field


class DriverAvailabilityRequest(BaseModel):
    is_online: bool


class DriverVehicleStatusResponse(BaseModel):
    category: str
    make: str
    model: str
    registration_number: str
    seat_count: int
    color: str | None
    verification_status: str


class DriverDashboardResponse(BaseModel):
    full_name: str
    is_online: bool
    online_minutes: int = Field(ge=0)
    safety_score: int | None = Field(default=None, ge=0, le=100)
    rating: float | None = Field(default=None, ge=1, le=5)
    today_earnings_paise: int = Field(ge=0)
    month_earnings_paise: int = Field(ge=0)
    today_completed_rides: int = Field(ge=0)
    month_completed_rides: int = Field(ge=0)
    vehicle: DriverVehicleStatusResponse | None = None
