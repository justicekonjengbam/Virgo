from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.phone import normalize_phone_e164


def normalize_phone(value: str) -> str:
    return normalize_phone_e164(value)


class PassengerSignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = normalize_phone(value)
        return normalized


class PasswordLoginRequest(BaseModel):
    phone_number: str
    password: str = Field(min_length=8, max_length=128)

    _normalize_phone = field_validator("phone_number")(normalize_phone)


class OtpRequest(BaseModel):
    phone_number: str
    _normalize_phone = field_validator("phone_number")(normalize_phone)


class OtpVerificationRequest(OtpRequest):
    otp: str = Field(pattern=r"^\d{6}$")


class RefreshRequest(BaseModel):
    refresh_token: str


class FirebaseLoginRequest(BaseModel):
    id_token: str = Field(min_length=1)
    full_name: str | None = Field(default=None, min_length=2, max_length=120)


class DriverFirebaseLoginRequest(BaseModel):
    """Verified Firebase identity used only to sign in an existing Driver."""

    id_token: str = Field(min_length=1)


class DriverFirebaseSignupRequest(DriverFirebaseLoginRequest):
    """Verified Firebase identity and required personal information for Driver registration."""

    full_name: str = Field(min_length=2, max_length=120)


class DriverOnboardingRequest(BaseModel):
    operating_city: str = Field(min_length=2, max_length=120)
    registration_number: str = Field(min_length=4, max_length=32)
    vehicle_make: str = Field(min_length=2, max_length=80)
    vehicle_model: str = Field(min_length=2, max_length=80)
    vehicle_year: int = Field(ge=1990, le=2100)
    vehicle_color: str | None = Field(default=None, max_length=40)
    vehicle_category: str = Field(pattern=r"^(car|bike|auto)$")
    seat_count: int = Field(ge=1, le=8)

    @field_validator("registration_number")
    @classmethod
    def normalize_registration_number(cls, value: str) -> str:
        return "".join(value.upper().split())


class DriverDocumentInput(BaseModel):
    document_type: str = Field(pattern=r"^(driving_licence|vehicle_registration|aadhaar|vehicle_insurance)$")
    document_number: str = Field(min_length=4, max_length=128)
    storage_key: str = Field(min_length=8, max_length=512)


class DriverRegistrationRequest(DriverFirebaseSignupRequest):
    operating_city: str = Field(min_length=2, max_length=120)
    registration_number: str = Field(min_length=4, max_length=32)
    vehicle_make: str = Field(min_length=2, max_length=80)
    vehicle_model: str = Field(min_length=2, max_length=80)
    vehicle_year: int = Field(ge=1990, le=2100)
    vehicle_color: str | None = Field(default=None, max_length=40)
    vehicle_category: str = Field(pattern=r"^(car|bike|auto)$")
    seat_count: int = Field(ge=1, le=8)
    documents: list[DriverDocumentInput] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def require_each_document_once(self) -> "DriverRegistrationRequest":
        expected = {"driving_licence", "vehicle_registration", "aadhaar", "vehicle_insurance"}
        if {item.document_type for item in self.documents} != expected:
            raise ValueError("Upload each required Driver document exactly once.")
        return self


class DriverProfileResponse(BaseModel):
    id: int
    full_name: str
    phone_number: str
    status: str
    operating_city: str | None
    onboarding_completed: bool


class DriverProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    operating_city: str | None = Field(default=None, min_length=2, max_length=120)

    @model_validator(mode='after')
    def at_least_one_field(self) -> 'DriverProfileUpdateRequest':
        if self.full_name is None and self.operating_city is None:
            raise ValueError('Choose at least one profile field to update.')
        return self


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class DriverAuthResponse(TokenResponse):
    driver: DriverProfileResponse


class OtpRequestResponse(BaseModel):
    message: str
    development_otp: str | None = None
