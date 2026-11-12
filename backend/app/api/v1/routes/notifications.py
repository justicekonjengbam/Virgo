from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_passenger
from app.db import get_db
from app.models.ride_hailing import Notification
from app.models.user import Passenger
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix='/passengers/me/notifications', tags=['notifications'])


@router.get('', response_model=list[NotificationResponse])
def list_notifications(passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> list[Notification]:
    return list(db.scalars(select(Notification).where(Notification.passenger_id == passenger.id).order_by(Notification.created_at.desc()).limit(100)).all())


@router.patch('/{notification_id}/read', response_model=NotificationResponse)
def mark_read(notification_id: int, passenger: Passenger = Depends(get_current_passenger), db: Session = Depends(get_db)) -> Notification:
    notification = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.passenger_id == passenger.id))
    if not notification:
        raise HTTPException(status_code=404, detail='Notification was not found.')
    notification.read_at = notification.read_at or datetime.now(UTC)
    db.commit(); db.refresh(notification)
    return notification
