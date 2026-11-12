import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import SessionLocal
from app.models.ride_hailing import Driver, Ride
from app.models.user import Passenger
from app.services.realtime_events import driver_channel, passenger_channel
from app.services.realtime_service import realtime_hub
from app.services.ride_matching_service import RideMatchingService

router = APIRouter(prefix='/realtime', tags=['realtime'])


def _bearer_token(websocket: WebSocket) -> str | None:
    value = websocket.headers.get('authorization', '')
    return value[7:] if value.lower().startswith('bearer ') else None


def _decode(websocket: WebSocket, actor: str | None) -> int | None:
    token = _bearer_token(websocket)
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            get_settings().jwt_secret_key,
            algorithms=[get_settings().jwt_algorithm],
        )
        if payload.get('type') != 'access' or payload.get('actor') != actor:
            return None
        return int(payload['sub'])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None


async def _keep_alive(websocket: WebSocket, channel: str) -> None:
    try:
        while True:
            message = await websocket.receive_text()
            if message == 'ping':
                await websocket.send_json({'type': 'pong'})
    except WebSocketDisconnect:
        pass
    finally:
        realtime_hub.disconnect(channel, websocket)


@router.websocket('/passengers/rides/{ride_id}')
async def passenger_ride_events(websocket: WebSocket, ride_id: int) -> None:
    passenger_id = _decode(websocket, None)
    db: Session = SessionLocal()
    try:
        passenger = db.get(Passenger, passenger_id) if passenger_id else None
        ride = db.get(Ride, ride_id)
        if not passenger or not ride or ride.passenger_id != passenger.id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        channel = passenger_channel(passenger.id, ride.id)
        await realtime_hub.connect(channel, websocket)
        snapshot = RideMatchingService().passenger_status(db, ride)
        await websocket.send_json({'type': 'ride.status', 'data': snapshot.model_dump(mode='json')})
        await _keep_alive(websocket, channel)
    finally:
        db.close()


@router.websocket('/drivers/me')
async def driver_events(websocket: WebSocket) -> None:
    driver_id = _decode(websocket, 'driver')
    db: Session = SessionLocal()
    try:
        driver = db.get(Driver, driver_id) if driver_id else None
        if not driver or driver.status in {'suspended', 'deactivated'}:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        channel = driver_channel(driver.id)
        await realtime_hub.connect(channel, websocket)
        offer = RideMatchingService().current_offer(db, driver)
        await websocket.send_json(
            {
                'type': 'ride.offer' if offer else 'ride.offer_cleared',
                'data': offer.model_dump(mode='json') if offer else None,
            },
        )
        await _keep_alive(websocket, channel)
    finally:
        db.close()
