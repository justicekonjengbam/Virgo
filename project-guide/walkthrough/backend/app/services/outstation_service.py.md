# backend/app/services/outstation_service.py

## 1. Purpose
Handles **outstation** bookings: long trips (150 km or more) booked at least 4 hours ahead and confirmed by an admin. Passenger routes, admin routes and driver routes call it. It uses `MapProviderService` for the route, `realtime_events.py` to push driver messages, and models/schemas for data.

## 2. Imports, one by one
Standard library:
- `from datetime import UTC, datetime, timedelta` (line 1). Date and time tools. *Example:* `datetime.now(UTC) + timedelta(hours=4)`.
- `from decimal import Decimal` (line 2). Exact decimal numbers (floats can be slightly wrong). *Example:* `Decimal('150.5')`. Used for the distance column.
Third-party:
- `from fastapi import HTTPException` (line 4). HTTP error type.
- `from sqlalchemy import func, select` (line 5). `func` calls SQL functions, e.g. `func.count()`.
- `from sqlalchemy.orm import Session` (line 6). Session type.
Project:
- `from app.models.ride_hailing import Driver, DriverVehicleAssignment, Notification, OutstationBooking, Vehicle` (line 8). Table classes.
- `from app.models.user import Passenger` (line 9).
- `from app.schemas.outstation import ...` (line 10). Six request/response classes in `backend/app/schemas/outstation.py`.
- `from app.services.map_provider_service import MapProviderService` (line 11). Route lookup.
- `from app.services.realtime_events import publish_outstation_assignment, publish_outstation_update` (line 12). Push to the driver app.

## 3. Walk through the code
`OPEN_STATUSES = ('requested','confirmed','driver_assigned')` (line 15): statuses that are still "alive".

**Booking life:** requested -> confirmed (admin sets fare) -> driver_assigned -> completed. Or rejected/cancelled.

### `__init__` (19-20)
Takes an optional map provider (so tests can pass a fake). `x or Y` uses `Y` when `x` is `None`.

### `estimate(request)` (22-33)
Input: `OutstationBookingCreate` (pickup, destination, scheduled_at, vehicle type). `_aware` makes the date timezone-aware. Checks: 4 hours to 180 days ahead (line 25), pickup differs from destination (27), then calls `map_provider.route(...)` (29). Distance in km, rounded to 1 decimal. If under 150 raises 422 (31). Returns distance, minutes, fare via `_fare`, and the route GeoJSON. All errors are 422 (data not acceptable).

### `create(db, passenger, request)` (35-55)
Repeats the time and place checks (lines 38-43; duplicates the work in `estimate`). Calls `estimate` (44). Counts the passenger's open bookings with `select(func.count()).select_from(OutstationBooking).where(... .in_(OPEN_STATUSES))`; `.in_` means SQL `IN (...)`. At 3 or more raise 409 (conflict). Looks for a duplicate request (same time and places), 409 if found. Creates the `OutstationBooking` with status `'requested'`. `db.add(booking); db.flush()` queues the insert and sends it so `booking.id` exists. `_notify` adds a notification. `db.commit(); db.refresh(booking)` saves and reloads. Returns `_response`.

### `passenger_list` (57-59): all of the passenger's bookings, newest departure first.

### `cancel` (61-74)
Finds the booking owned by this passenger (404 otherwise). Only open bookings can be cancelled (409). `hours_remaining` is hours until departure. The cutoff is 24 h if a driver is assigned, else 6 h (line 68). Too late gives 409. Otherwise it sets status, time and reason, adds a notification, and commits.

### `admin_list` (76-80): optional status filter, soonest first.

### `eligible_drivers` (82-116)
Booking must be `confirmed`. `conflict_ids` is a **subquery** (a SELECT used inside another query) that lists drivers who already have an assignment within 12 hours of this one. The main query joins `Driver`, `DriverVehicleAssignment` and `Vehicle` (a **join** links rows of two tables by matching columns), keeps active drivers with a verified vehicle and an assignment that has not ended (`ended_at IS NULL`), excludes the conflicts (`not_in`) and sorts by rating, then completed rides, then name. Returns a list built from `(driver, vehicle)` rows.

### `admin_update` (118-159)
Big function: one `request.status` decides the branch.
- `confirmed` (123-129): booking must be `requested`; distance from the request or stored; must be at least 150; stores distance, recomputes fare, sets `confirmed_at`.
- `driver_assigned` (130-144): needs status `confirmed` and a driver phone. Searches the driver by three phone formats (`9876543210`, `919876543210`, `+919876543210`). Finds the open vehicle assignment. Checks the driver is active and the vehicle verified (note: line 139 checks `not driver` again, it can never be true after line 135). Checks no other assignment within 12 hours. Sets driver, vehicle, `assigned_at`.
- `rejected`/`cancelled` (145-148): needs a note.
- `completed` (149-150): only from `driver_assigned`.
Then line 151 sets status, note and admin id. Notification copy is made, saved. After commit, it pushes to the driver: a new assignment or an update (lines 155-158). Pushing after commit is correct: the driver never hears about a change that was rolled back.
Gap: there is no check that the new status is a legal step for every value (e.g. `requested` again).

### `driver_assignments` (161-168)
Bookings for this driver with status assigned or completed in the last 90 days. For each, loads passenger and vehicle with `db.get` (one query each) and builds a response. `order_by(status.desc(), scheduled_at)` puts `driver_assigned` before `completed` (alphabetical reverse).

### `_response` (170-175)
Builds the big response, handling missing driver, vehicle or passenger. `can_cancel` is true if open and enough hours remain.

### `_fare(distance_km, preference, scheduled_at)` (177-183)
Prices in paise: base plus per-extra-km beyond 150 km, plus a fixed 50000 (Rs 500). A 15 percent night surcharge before 06:00 or from 21:00 (UTC hour; see weak points). Example: sedan, 200 km at noon: 250000 + 50*1600 + 50000 = 380000 paise (Rs 3800). Raises `KeyError` for an unknown vehicle type.

### `_notify`, `_notification_copy`, `_aware`, `_local_phone` (185-203)
`_notify` adds a `Notification` row (no commit). `_notification_copy` returns title and body; `f'{x:,.0f}'` formats with thousands separators. `_aware` turns a naive datetime into UTC and converts aware ones to UTC. `_local_phone` keeps digits and returns the last 10, so `+91 98765 43210` gives `9876543210`.

## 4. How data flows
```
Passenger app -> POST outstation -> create() -> estimate() -> MapProviderService.route -> Geoapify
   -> DB insert OutstationBooking(requested) + Notification
Admin panel -> admin_update(confirmed) -> fare saved -> admin_update(driver_assigned)
   -> commit -> publish_outstation_assignment -> hub -> Driver app
```

## 5. Try it
Not directly runnable. After starting the backend, use the admin app or curl the admin outstation route. Example failure: scheduling 1 hour ahead gives HTTP 422 "Choose a departure between 4 hours and 180 days".

## 6. Can it be better?
- Good: real business rules, conflict checks, notifications after commit.
- Weak: long one-line statements (51, 167, 175) are hard to read. Time checks are duplicated between `estimate` and `create`. `_fare` uses UTC hour for "night" (India is UTC+5:30), so night pricing is wrong by hours. Magic numbers (150, 4, 180, 12, 24, 6, 3, 1.15, prices) should be constants or settings. `_fare` raises `KeyError` for unknown types. N+1 queries in lists. Phone matching with three formats is fragile. No row lock, so two admins can race.
- Cleaner: `PRICING = {...}` constant and `ZoneInfo('Asia/Kolkata')` for the night rule.
- Security: admin id is stored; make sure the admin routes check the role.

## 7. Check yourself
1. Why does the code call `publish_outstation_assignment` after `db.commit()`?
2. A sedan trip of 300 km at 14:00: what is the fare in paise?
