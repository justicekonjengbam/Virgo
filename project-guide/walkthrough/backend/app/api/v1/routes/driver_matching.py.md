# backend/app/api/v1/routes/driver_matching.py

## 1. Purpose
The driver's live ride routes: send GPS location, get the current ride offer, accept or reject it, see the active ride, cancel, do ride actions (arrive, start, finish), see a summary and rate the passenger. Used by `driver-app/`. Mounted at `router.py:24`. URLs start with `/api/v1/drivers/me`.

## 2. Imports, one by one
- `from fastapi import APIRouter, Depends, HTTPException` (`driver_matching.py:1`): router, dependency injection, and `HTTPException` (stops a request with an error; *example:* `HTTPException(404, 'x')`).
- `from sqlalchemy import select` (`:2`): builds SQL SELECT in Python. `from sqlalchemy.orm import Session` (`:3`): session type.
- `get_current_driver` (`:5`, from `app/api/dependencies/driver_auth.py`), `get_db` (`:6`), `Driver, Ride` (`:7`, `app/models/ride_hailing.py`).
- Many schemas from `app/schemas/booking.py` (`:8`): JSON shapes, for example `DriverLocationUpdateRequest` (latitude, longitude, heading, accuracy, speed, time).
- `RideMatchingService` (`:9`) finds and handles offers; `RideLifecycleService` (`:10`) handles the ride states.

## 3. Walk through the code, top to bottom
- `router` with prefix `/drivers/me` (`:12`); `service` = matching, `lifecycle_service` (`:13-14`).
- **`update_location`** `PUT /location`, status 204 (`:17-19`). 204 = success with no body. Passes seven values to `service.update_driver_location`, which stores the position so the system can match nearby passengers. The app calls this often.
- **`current_offer`** `GET /ride-offers/current` (`:22-24`). Returns the offer waiting for this driver, or `None` (`null`). `DriverRideOfferResponse | None` means "either this shape or nothing".
- **`respond_to_offer`** `POST /ride-offers/{offer_id}/response` (`:27-29`). Body has `decision` (accept or reject; exact values unverified). `service.respond` applies it.
- **`active_ride`** `GET /rides/active` (`:32-34`). `lifecycle_service.driver_snapshot` returns the current ride or `None`.
- **`cancel_ride`** `POST /rides/{ride_id}/cancel` (`:37-39`). `cancel_by_driver(db, driver, ride_id, reason, confirm)`.
- **`ride_action`** `POST /rides/{ride_id}/actions` (`:42-44`). Body `action` plus `start_otp`. The passenger tells the driver a code; the driver types it to start the trip. The service checks it.
- **`ride_summary`** `GET /rides/{ride_id}/summary` (`:47-52`). `db.scalar(select(Ride).where(Ride.id == ride_id, Ride.driver_id == driver.id))` returns the first row or `None`. The driver filter blocks reading others' rides. Missing gives 404.
- **`rate_passenger`** `POST /rides/{ride_id}/rating` (`:55-60`). Same lookup, then `lifecycle_service.rate(db, ride, 'driver', score, comment)`.

## 4. How data flows
```
driver-app --PUT /drivers/me/location {lat,lng,...}--> get_current_driver
   -> RideMatchingService.update_driver_location --> UPDATE/INSERT in database
   <- 204 (no body)
```

## 5. Try it
`curl -s -w '%{http_code}\n' -X PUT -H "Authorization: Bearer <secret>" -H 'content-type: application/json' -d '{"latitude":1.0,"longitude":2.0}' localhost:8000/api/v1/drivers/me/location`. `-w` prints the status code after the call. Expect `204`, or `422` if required fields are missing (the schema may need more fields; check `DriverLocationUpdateRequest`).

## 6. Can it be better?
- Good: ownership check in query; clear route names.
- Weak: the "ride or 404" block is copied twice (`:49-51`, `:57-59`) and again in `booking.py`. Two routes in this file named `cancel_ride`/`ride_summary` also exist in `booking.py`; fine because they are in different modules, but confusing in stack traces.
- Cleaner way: one shared helper `get_owned_ride(db, ride_id, driver=None, passenger=None)`.
- Security: location updates have no visible rate limit. The 404 for foreign rides avoids revealing they exist (good).

## 7. Check yourself
1. What does status 204 mean for `update_location`?
2. How does `ride_summary` stop driver A from reading driver B's ride?
