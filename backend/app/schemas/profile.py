import re

from pydantic import BaseModel, Field, field_validator, model_validator


class PassengerProfileResponse(BaseModel):
    full_name: str
    phone_number: str
    email: str | None
    preferred_language: str


class PassengerProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    email: str | None = Field(default=None, max_length=254)
    preferred_language: str | None = Field(default=None, min_length=2, max_length=10)

    @model_validator(mode='after')
    def at_least_one_field(self) -> 'PassengerProfileUpdateRequest':
        if self.full_name is None and self.email is None and self.preferred_language is None:
            raise ValueError('Choose at least one profile field to update.')
        return self

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', normalized):
            raise ValueError('Enter a valid email address.')
        return normalized
