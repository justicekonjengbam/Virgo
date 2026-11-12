from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class AdminLoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=128)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class AdminProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    permissions: list[str]
    last_login_at: datetime | None = None


class AdminAuthResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    admin: AdminProfileResponse


class AdminPasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)

    @model_validator(mode='after')
    def passwords_must_differ(self) -> 'AdminPasswordChangeRequest':
        if self.current_password == self.new_password:
            raise ValueError('Choose a new password different from the current password.')
        return self


class AdminPasswordChangeResponse(BaseModel):
    message: str


class AdminDriverDocumentResponse(BaseModel):
    driver_id: int
    driver_name: str
    operating_city: str | None
    vehicle_registration_number: str | None
    document_type: str
    document_number: str
    verification_status: str
    review_note: str | None
    created_at: datetime


class AdminDriverResponse(BaseModel):
    id: int
    full_name: str
    phone_number: str
    operating_city: str | None
    status: str
    vehicle_category: str | None
    vehicle_name: str | None
    vehicle_registration_number: str | None
    vehicle_verification_status: str | None
    document_statuses: dict[str, str]


TicketStatus = Literal['open', 'in_progress', 'resolved', 'closed']


class AdminSupportTicketResponse(BaseModel):
    id: int
    passenger_name: str
    category: str
    status: str
    subject: str
    description: str
    created_at: datetime
    assigned_admin_id: int | None
    resolution_note: str | None


class AdminSupportTicketUpdate(BaseModel):
    status: TicketStatus
    resolution_note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode='after')
    def resolution_needs_a_note(self) -> 'AdminSupportTicketUpdate':
        if self.status in {'resolved', 'closed'} and not (self.resolution_note or '').strip():
            raise ValueError('Add a resolution note before resolving or closing a ticket.')
        return self


class AdminRideListItemResponse(BaseModel):
    id: int
    passenger_id: int
    passenger_name: str
    passenger_phone: str
    driver_id: int | None = None
    driver_name: str | None = None
    driver_phone: str | None = None
    vehicle_name: str | None = None
    vehicle_registration_number: str | None = None
    category_code: str
    category_name: str
    status: str
    pickup_address: str
    destination_address: str
    fare_paise: int
    payment_status: str | None = None
    requested_at: datetime
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None


class AdminRideEventResponse(BaseModel):
    id: int
    actor_type: str
    actor_id: int | None = None
    event_type: str
    payload: dict | None = None
    occurred_at: datetime


class AdminRideDetailResponse(BaseModel):
    id: int
    status: str
    passenger_id: int
    passenger_name: str
    passenger_phone: str
    driver_id: int | None = None
    driver_name: str | None = None
    driver_phone: str | None = None
    vehicle_id: int | None = None
    vehicle_name: str | None = None
    vehicle_registration_number: str | None = None
    category_code: str
    category_name: str
    pickup_address: str
    pickup_latitude: float
    pickup_longitude: float
    destination_address: str
    destination_latitude: float
    destination_longitude: float
    estimated_distance_km: float
    final_distance_km: float | None = None
    actual_waiting_minutes: float | None = None
    rate_card_version: int | None = None
    requested_at: datetime
    accepted_at: datetime | None = None
    arrived_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    cancelled_by: str | None = None
    fare_paise: int
    base_fare_paise: int | None = None
    distance_fare_paise: int | None = None
    waiting_charge_paise: int | None = None
    surcharge_paise: int | None = None
    discount_paise: int | None = None
    gst_paise: int | None = None
    commission_paise: int | None = None
    driver_net_paise: int | None = None
    payment_status: str | None = None
    payment_method: str | None = None
    events: list[AdminRideEventResponse] = []


class AdminAssignDriverRequest(BaseModel):
    driver_id: int | None = None
    driver_phone: str | None = None


class AdminCancelRideRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=255)


class AdminRateCardResponse(BaseModel):
    id: int
    category_code: str
    version: int
    is_active: bool
    base_fare_paise: int
    first_tier_km: float
    first_tier_rate_paise: int
    second_tier_rate_paise: int
    waiting_charge_per_minute_paise: int
    waiting_grace_period_minutes: int
    surcharge_distance_threshold_km: float
    surcharge_percentage: float
    cancellation_fee_paise: int
    gst_rate: float
    commission_rate: float
    updated_at: datetime


class AdminRateCardUpdateRequest(BaseModel):
    base_fare_paise: int | None = None
    first_tier_km: float | None = None
    first_tier_rate_paise: int | None = None
    second_tier_rate_paise: int | None = None
    waiting_charge_per_minute_paise: int | None = None
    waiting_grace_period_minutes: int | None = None
    surcharge_distance_threshold_km: float | None = None
    surcharge_percentage: float | None = None
    cancellation_fee_paise: int | None = None
    gst_rate: float | None = None
    commission_rate: float | None = None
    is_active: bool | None = None

