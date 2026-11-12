# backend/app/services/ride_lifecycle_service.py

## 1. Purpose
Controls what happens to a ride after a driver is chosen: arrived, start, complete, cancel, summary and rating. Called by passenger and driver routes. It calls `realtime_events.py` to push updates. `ride_matching_service.py` imports it for `_ride_start_otp`.

## 2. Imports, one by one
- `from datetime import UTC, datetime` (line 1). Time tools; `datetime.now(UTC)` is the current time in UTC.
- `from fastapi import HTTPException, status` (line 3). HTTP errors and named codes (`status.HTTP_409_CONFLICT`).
- `from sqlalchemy import select` (line 4). Builds SQL queries.
- `from sqlalchemy.orm import Session` (line 5). Session type.
- `from app.models.ride_hailing import Driver, FareLineItem, FareQuote, Rating, Ride, RideDispatchOffer, RideEvent` (line 7). Table classes. `RideEvent` is an audit log row.
- `from app.models.user import Passenger` (line 8).
- `from app.schemas.booking import ...` (line 9). Response shapes from `backend/app/schemas/booking.py`.
- `from app.services.realtime_events import publish_driver_ride_event, publish_passenger_status` (line 10). Push messages.

## 3. Walk through the code
Constants (13-15): `ACTIVE_STATUSES` (ride not finished) and two sets of allowed cancel reasons. A **set** (`{...}`) is fast for "is x in it?" checks.

**Ride states used here:** driver_arriving -> driver_arrived -> in_progress -> completed (or cancelled).

- `passenger_active` / `driver_active` (19-27): `db.scalar(select(Ride).where(...).order_by(Ride.requested_at.desc()))` returns the newest active ride or `None`.
- `driver_snapshot` (29-41): builds `DriverActiveRideResponse` for the driver app: addresses, coordinates (as floats), passenger name, route, and flags. `can_cancel` is true while arriving or arrived; `can_end` while in progress.
- `cancel_by_passenger` (43-57): finds the ride owned by this passenger (404). `confirm` must be true (400). Ride must be active (409). Reason must be allowed (422). If the trip already started, only `safety_concern` or `emergency` are allowed (409). Picks an event name, calls `_cancel`, returns a message. Example: `reason='changed_plans'` while `driver_arriving` works; while `in_progress` it fails.
- `cancel_by_driver` (59-73): same style. Allowed statuses: arriving, arrived, in progress. Vehicle issue is allowed mid-trip.
- `action(db, driver, ride_id, action, start_otp)` (75-108): the state machine. `transitions` is a dict mapping `(current_status, action)` to `(new_status, message)`. `.get` returns `None` for an illegal pair, then 409 (line 86). For `start`, it computes the expected OTP from the passenger phone (last 4 digits) and compares; mismatch gives 422. Then sets the status. `start` stores `started_at`. `complete` stores `completed_at`, copies the estimated distance as final, computes duration (at least 1 second), marks the newest fare quote `is_final = True`, and increases `completed_rides_count`. It adds a `RideEvent`, commits, refreshes, and then pushes to passenger and driver.
- `summary` (110-123): only for completed rides (409). Loads the final quote, its line items, and which sides have rated. `item.item_type.replace('_',' ').title()` turns `base_fare` into `Base Fare`. Distance is metres / 1000, minutes are seconds / 60.
- `rate` (125-138): completed ride only; one rating per rater type (409 if repeated). Adds the `Rating`, `db.flush()`, and if a passenger rated, recalculates the driver's average over all passenger ratings with `sum(values)/len(values)` rounded to 2 decimals. Commits. Note: the average uses a join to `Ride` to filter by the driver.
- `_ride_start_otp(passenger)` (140-145, staticmethod): keeps only the digits of the phone and returns the last 4. Raises 409 if fewer than 4 digits.
- `_cancel(...)` (147-159, staticmethod): sets status `cancelled`, who and why, logs a `RideEvent`, marks all `pending` offers as `cancelled`, commits, refreshes, publishes to passenger and to the driver (if any).
- `_aware` (161-163): adds UTC to a naive datetime.

## 4. How data flows
```
Driver app -- POST action=start, otp --> action()
   SELECT Ride -> transitions lookup -> OTP check -> UPDATE ride -> INSERT RideEvent -> COMMIT
   -> publish_passenger_status -> hub -> Passenger app
   -> publish_driver_ride_event -> hub -> Driver app
```

## 5. Try it
Not directly runnable. A quick pure check of the OTP rule:
`uv run python -c "from app.services.ride_lifecycle_service import RideLifecycleService as R; print(R._ride_start_otp(type('P',(),{'phone_number':'+919876543210'})()))"` run in `backend/`. `type('P',(),{...})()` builds a throwaway object with a `phone_number`. Expected: `3210`.

## 6. Can it be better?
- Good: a transitions table is easy to read; every change writes an audit event; messages are sent after commit.
- Weak (security): the start OTP is the last 4 digits of the passenger's phone. It is guessable, and anyone who knows the phone knows the OTP. A random OTP stored per ride is safer. `action` has no check that `action` is one of the three names beyond the dict lookup (fine). Two drivers or taps at once can race (no row lock). `final_distance_meters` is just the estimate, not measured. Rating average is recomputed over all rows each time (fine for small data). No `@transaction`: partial failure between commit and publish is possible but harmless.
- Cleaner: `ride.otp = secrets.randbelow(10000)` formatted to 4 digits, saved on the ride at `driver_arrived`.

## 7. Check yourself
1. What happens if a driver sends `action='start'` while the ride status is `driver_arriving`?
2. Why are the publish calls placed after `db.commit()`?
