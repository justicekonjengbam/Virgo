# backend/app/services/realtime_events.py

## 1. Purpose
A set of small "publish" helpers. Each one builds a channel name and a message and hands it to the hub in `realtime_service.py`. Other services (`ride_lifecycle_service.py`, `ride_matching_service.py`, `outstation_service.py`) call these after they commit to the database. It also holds the code that runs when an offer times out.

## 2. Imports, one by one
Standard library:
- `from datetime import UTC, datetime` (line 1). `datetime` is a date and time object; `UTC` is the timezone object for UTC. *Example:* `datetime.now(UTC)`.
Third-party:
- `from fastapi.encoders import jsonable_encoder` (line 3). Turns Pydantic objects, datetimes and decimals into plain JSON-safe dicts. *Example:* `jsonable_encoder({'t': datetime.now()})` gives a string for `t`.
- `from sqlalchemy.orm import Session` (line 4). Database session type hint.
Project:
- `from app.db import SessionLocal` (line 6). A factory that makes a new database session (`backend/app/db.py`). Needed because the timer runs outside a request.
- `from app.models.ride_hailing import Ride, RideDispatchOffer` (line 7). Table classes (type hints here).
- `from app.services.realtime_service import realtime_hub` (line 8). The shared hub.
Local imports inside functions (lines 20, 30-31, 87) bring in `RideMatchingService` and `Driver` late. This avoids a **circular import** (A imports B while B imports A, which crashes at start). `ride_matching_service.py` imports this file at the top, so this file must not import it at the top.

## 3. Walk through the code
- `passenger_channel(passenger_id, ride_id)` (11-12): returns `'passenger:7:ride:42'`. The string is the channel name clients join.
- `driver_channel(driver_id)` (15-16): returns `'driver:5'`.
- `publish_passenger_status(db, ride)` (19-26): asks `RideMatchingService().passenger_status(db, ride)` for the full status object, `jsonable_encoder` makes it JSON-safe, then `realtime_hub.publish_from_request(channel, {'type': 'ride.status', 'data': ...})` sends it. The `type` string tells the app which handler to run.
- `publish_driver_offer(db, offer)` (29-48): loads the driver (`db.get(Driver, id)` returns the row or `None`). `current_offer(db, driver)` builds the offer payload (and may expire it). If there is a payload, publish `ride.offer`, then make `expires_at` timezone-aware (SQLite may return a naive datetime without timezone; lines 40-44 add UTC), and call `schedule_offer_expiry(offer.id, seconds_left)`.
- `publish_driver_offer_cleared(driver_id, ride_id)` (51-55): sends `ride.offer_cleared` so the driver app hides the popup.
- `publish_driver_ride_event(driver_id, ride, event_type)` (58-62): sends a custom type plus ride id and status, e.g. `ride.completed`.
- `publish_outstation_assignment` (65-69) and `publish_outstation_update` (72-76): tell a driver about an outstation booking. `scheduled_at.isoformat()` makes `'2026-10-30T09:00:00+00:00'`.
- `publish_driver_location(passenger_id, ride_id, payload)` (79-83): sends `driver.location` to the passenger channel.
- `expire_offer_and_publish(offer_id)` (86-100): opens its own session `SessionLocal()`. Calls `service.expire_offer`. It returns `None` if nothing to do, else `(expired_offer, ride, next_offer)`. Then it clears the old driver's popup, updates the passenger and offers the next driver. `finally: db.close()` always returns the connection.

## 4. How data flows
```
RideLifecycleService.action --commit--> publish_passenger_status
   -> RideMatchingService.passenger_status (reads DB)
   -> hub.publish_from_request('passenger:7:ride:42', {type, data})
   -> WebSocket -> passenger app updates screen
```

## 5. Try it
Not directly runnable. With the app running and a WebSocket client on a ride channel, change a ride status and watch a `ride.status` message arrive.

## 6. Can it be better?
- Good: one file lists every event name; names are simple.
- Weak: message types are plain strings (typos are silent). Each publish function builds a new `RideMatchingService()` (cheap, but odd). A publish does not fail if no one listens (fine) but also gives no log. The circular import is a design smell.
- Cleaner: move `passenger_status` and `current_offer` into a separate read-only module so the cycle disappears; use an `Enum` or constants for event types.
- Security: the payload for the passenger includes the start OTP only when status is `driver_arrived` (see matching service); the channel must be protected.

## 7. Check yourself
1. Why does `expire_offer_and_publish` create its own `SessionLocal()`?
2. What is a circular import and where does this file avoid one?
