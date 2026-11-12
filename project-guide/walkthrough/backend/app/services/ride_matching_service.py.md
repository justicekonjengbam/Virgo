# backend/app/services/ride_matching_service.py

## 1. Purpose
This is **dispatch**: choose the nearest suitable driver, offer the ride for 30 seconds, handle accept/decline/timeout, track driver GPS, and build the status the passenger sees. Called by booking and driver routes and by `realtime_events.py`. It calls `DriverReadinessService` and `RideLifecycleService`.

## 2. Imports, one by one
Standard library:
- `from datetime import UTC, datetime, timedelta` (line 1). Times and durations. *Example:* `timedelta(seconds=30)`.
- `from math import asin, cos, radians, sin, sqrt` (line 2). For the haversine distance.
Third-party:
- `from fastapi import HTTPException, status` (line 4). HTTP errors.
- `from sqlalchemy import select` (line 5).
- `from sqlalchemy.exc import IntegrityError` (line 6). Raised when the database rejects data (for example a unique index broken). Used at line 287.
- `from sqlalchemy.orm import Session` (line 7).
Project:
- `from app.models.ride_hailing import (...)` (lines 9-12). Driver, DriverCurrentLocation (last GPS point), DriverVehicleAssignment (which car a driver uses), FareQuote, Ride, RideDispatchOffer, RideEvent, RideCategory, Vehicle.
- `from app.schemas.booking import ...` (lines 13-15): the three response classes.
- `from app.services.realtime_events import (...)` (lines 16-21): four publish helpers.
- `from app.services.ride_lifecycle_service import RideLifecycleService` (line 22): reuses the OTP helper.
- `from app.services.driver_readiness_service import DriverReadinessService` (line 23): checks whether a driver's documents are complete.
(Line numbers: the file's own numbering; see the code.)

## 3. Walk through the code
Class constants (lines 27-37 of the file): `offer_ttl` 30 seconds; `maximum_pickup_distance_km` 40; `city_centres` for drivers with no GPS; `readiness_service`. The docstring says production should use Redis or PostGIS instead of scanning drivers in Python.

### `dispatch(db, ride)` (line 40)
Only for `searching` rides. Gets driver ids already offered this ride (so nobody is asked twice). `_nearest_candidate` returns `(driver, distance)` or `None`. If none: the ride is cancelled with reason `no_eligible_driver`, an event `matching_failed` is added, returns `None`. Else creates a `RideDispatchOffer` that expires in 30 seconds and a `ride_offered` event. It only does `db.add`, so the caller commits.

### `current_offer(db, driver)` (line 56)
Newest `pending` offer for the driver. If expired: expire it and make the next offer (`_expire_and_retry`), commit, then tell the driver (clear), passenger (status) and the next driver. Returns `None`. Otherwise checks the ride is still `searching` and builds `DriverRideOfferResponse` with the latest fare quote. `pickup_minutes_away=4` is hard-coded (a placeholder).

### `respond(db, driver, offer_id, decision)` (line 88)
The offer must belong to this driver (404). If not pending or expired: expire it and 409. Ride must still be searching. Then `offer.status = decision` (should be `accepted` or `declined`; this function does not validate the string, the schema must). On `accepted`: reject if the driver already has an active ride; require an active, verified vehicle and `is_online`; set driver, vehicle, status `driver_arriving`; add event. Else: add a `ride_declined` event and `dispatch` again for the next driver. Then `commit` inside `try`. **IntegrityError** is caught: the database probably has a unique rule (one active ride per driver), so a race gives 409 with `rollback()` (undo the pending changes). After commit it refreshes and publishes. Returns the decision response.

### `passenger_status(db, ride)` (line 134)
Loads driver, vehicle, latest quote. A chain of `if/elif` picks the message. Loads the driver's last location; for arriving/arrived rides computes the ETA: distance / 25 km/h * 60 minutes, at least 1 (0 if arrived). Builds `PassengerRideStatusResponse`, including flags `can_cancel`, `can_end`, and `ride_start_otp` only at `driver_arrived`.

### `update_driver_location(...)` (line 179)
Finds the driver's live ride. Offline drivers with no ride get 409. `captured_at` defaults to now; naive times become UTC. Rejects readings older than 120 s (422) and accuracy worse than 150 m (422). If a previous location exists, computes implied speed in m/s (distance in metres / seconds). If less than 120 s passed and speed is over 55 m/s (198 km/h), reject as a GPS jump. Then updates or inserts the `DriverCurrentLocation`, commits, and publishes `driver.location` to the passenger if on a ride.

### `expire_offer(db, offer_id)` (line 215)
Used by the timer. Returns `None` unless the offer is still pending and expired. Otherwise expires, retries, commits and returns `(offer, ride, next_offer)`.

### `_expire_and_retry(db, offer)` (line 227)
Marks the offer `expired`, logs `ride_offer_expired`, and calls `dispatch` for the next driver if the ride is still searching.

### `_nearest_candidate(db, ride, excluded_driver_ids)` (line 235)
Loads the ride category. First, for online drivers whose status is `pending`, calls `readiness_service.reconcile` (activate them if all documents are approved). Then a join query: online, `active`, verified vehicle in the same category code, with an unended assignment, and optional current location (`outerjoin` keeps drivers without GPS). For each row: skip excluded drivers and drivers with an active ride; ignore a location older than 5 minutes; use `_driver_coordinates`; keep drivers within 40 km. Returns the closest by `min(..., key=lambda item: item[1])`. A **lambda** is a tiny unnamed function: here "take the second element".

### Helpers
`_driver_coordinates` uses the GPS point or the city centre by `operating_city` (`casefold` is a strong lowercase). `_active_vehicle` finds the newest open assignment's vehicle. `_distance_km` is haversine. `_is_expired` fixes naive datetimes and compares to `now`.

## 4. How data flows
```
Passenger books -> ride.status=searching -> dispatch() -> offer row (30s)
  commit -> publish_driver_offer -> hub -> Driver app popup
  Driver taps Accept -> respond() -> ride=driver_arriving -> commit
     -> publish cleared + passenger status -> Passenger app
  No answer in 30s -> hub timer -> expire_offer() -> next driver or ride cancelled
```

## 5. Try it
The distance helper is pure: run in `backend/`:
`uv run python -c "from app.services.ride_matching_service import RideMatchingService as R; print(round(R._distance_km(15.4589,75.0078,15.3647,75.1240),1))"`
`-c` runs a line of Python. Expected: about `15.5` (km between Dharwad and Hubballi centres). I am not certain of the second decimal; the value should be close to 15 km.

## 6. Can it be better?
- Good: handles timeouts, races (IntegrityError), stale GPS, speed jumps, and skips drivers already asked.
- Weak: `_nearest_candidate` loads every online driver and does 2-3 queries per driver (slow with many drivers). It also runs `reconcile` (a write) inside a read path. `decision` is not validated here. `pickup_minutes_away=4` is fake. ETA uses a fixed 25 km/h. The offer timer lives in memory (`realtime_service.py`); after a restart pending offers are only expired when someone asks. `current_offer` has side effects (writes) although it sounds like a read. Constants are magic numbers (120, 150, 55, 5 minutes).
- Cleaner: do the distance filter in SQL (PostGIS, or a bounding box) and fetch active rides for all candidates in one query.
- Security: driver can only answer their own offers (line 252 checks `driver_id`). The OTP is exposed only at `driver_arrived`.

## 7. Check yourself
1. What stops the same driver from being offered the same ride twice?
2. What happens if two drivers accept the same ride at the same instant?
