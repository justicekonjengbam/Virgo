from pydantic import BaseModel


class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    relationship: str | None
