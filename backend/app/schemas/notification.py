from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    body: str
    data_json: dict | None
    read_at: datetime | None
    created_at: datetime
