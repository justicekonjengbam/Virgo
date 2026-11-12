from datetime import UTC, datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.ride_hailing import Ride, RideDispatchOffer
from app.services.realtime_service import realtime_hub


def passenger_channel(passenger_id: int, ride_id: int) -> str:
    return f'passenger:{passenger_id}:ride:{ride_id}'


def driver_channel(driver_id: int) -> str:
    return f'driver:{driver_id}'


def publish_passenger_status(db: Session, ride: Ride) -> None:
    from app.services.ride_matching_service import RideMatchingService

    status = RideMatchingService().passenger_status(db, ride)
    realtime_hub.publish_from_request(
        passenger_channel(ride.passenger_id, ride.id),
        {'type': 'ride.status', 'data': jsonable_encoder(status)},
    )


def publish_driver_offer(db: Session, offer: RideDispatchOffer) -> None:
    from app.models.ride_hailing import Driver
    from app.services.ride_matching_service import RideMatchingService

    driver = db.get(Driver, offer.driver_id)
    payload = RideMatchingService().current_offer(db, driver) if driver else None
    if payload:
        realtime_hub.publish_from_request(
            driver_channel(offer.driver_id),
            {'type': 'ride.offer', 'data': jsonable_encoder(payload)},
        )
        expires_at = (
            offer.expires_at.replace(tzinfo=UTC)
            if offer.expires_at.tzinfo is None
            else offer.expires_at
        )
        realtime_hub.schedule_offer_expiry(
            offer.id,
            (expires_at - datetime.now(UTC)).total_seconds(),
        )


def publish_driver_offer_cleared(driver_id: int, ride_id: int) -> None:
    realtime_hub.publish_from_request(
        driver_channel(driver_id),
        {'type': 'ride.offer_cleared', 'data': {'ride_id': ride_id}},
    )


def publish_driver_ride_event(driver_id: int, ride: Ride, event_type: str) -> None:
    realtime_hub.publish_from_request(
        driver_channel(driver_id),
        {'type': event_type, 'data': {'ride_id': ride.id, 'status': ride.status}},
    )


def publish_outstation_assignment(driver_id: int, booking_id: int, scheduled_at: datetime) -> None:
    realtime_hub.publish_from_request(
        driver_channel(driver_id),
        {'type': 'outstation.assigned', 'data': {'booking_id': booking_id, 'scheduled_at': scheduled_at.isoformat()}},
    )


def publish_outstation_update(driver_id: int, booking_id: int, booking_status: str) -> None:
    realtime_hub.publish_from_request(
        driver_channel(driver_id),
        {'type': 'outstation.updated', 'data': {'booking_id': booking_id, 'status': booking_status}},
    )


def publish_driver_location(passenger_id: int, ride_id: int, payload: dict) -> None:
    realtime_hub.publish_from_request(
        passenger_channel(passenger_id, ride_id),
        {'type': 'driver.location', 'data': payload},
    )


def expire_offer_and_publish(offer_id: int) -> None:
    from app.services.ride_matching_service import RideMatchingService

    db = SessionLocal()
    try:
        service = RideMatchingService()
        result = service.expire_offer(db, offer_id)
        if not result:
            return
        expired_offer, ride, next_offer = result
        publish_driver_offer_cleared(expired_offer.driver_id, ride.id)
        publish_passenger_status(db, ride)
        if next_offer:
            publish_driver_offer(db, next_offer)
    finally:
        db.close()
