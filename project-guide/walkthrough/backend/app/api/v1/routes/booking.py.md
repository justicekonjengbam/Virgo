# backend/app/api/v1/routes/booking.py

## 1. Purpose
Passenger ride routes: list locations, get a price estimate, book a ride, see status, cancel, see summary, rate the driver, edit a saved place. Used by `passenger-app/`. Mounted at `router.py:27`. URLs start with `/api/v1/passengers/me` ("me" = the logged-in passenger).

## 2. Imports, one by one
- `from fastapi import APIRouter, Depends, HTTPException, status` (`booking.py:1`). `HTTPException` stops the request with an error code. *Example:* `raise HTTPException(status_code=404, detail='x')` sends `{"detail":"x"}` with 404. `Depends` = dependency injection; `status` = named HTTP codes.
- `from sqlalchemy import select` (`booking.py:2`). Builds a SQL SELECT in Python. *Example:* `select(Ride).where(Ride.id == 1)`.
- `from sqlalchemy.orm import Session` (`booking.py:3`). The database session type.
- `get_current_passenger` from `app/api/dependencies/auth.py` (`booking.py:5`). Reads the bearer token and returns the `Passenger` row, or 401.
- `get_db` (`booking.py:6`), `Passenger` (`app/models/user.py`, `:7`), `Ride` (`app/models/ride_hailing.py`, `:8`): model classes are table definitions.
- Schemas (`booking.py:9-10`) from `app/schemas/booking.py` and `app/schemas/home.py`: JSON shapes in/out.
- `BookingService`, `RideMatchingService`, `RideLifecycleService` (`booking.py:11-13`) from `app/services/`: business logic.

## 3. Walk through the code, top to bottom
- `router`, `service`, `matching_service`, `lifecycle_service` (`booking.py:15-18`): prefix and three shared service objects.
- Every route has `passenger: Passenger = Depends(get_current_passenger)`. So all are login-only. When the value is unused the name is `_`.

**`get_locations`** `GET /locations` (`booking.py:21-23`): `service.locations(db)` returns pick-up/drop-off options.
**`estimate_ride`** `POST /ride-estimates` (`booking.py:26-28`): `service.estimate(db, request)` returns prices; nothing is saved (I infer this; check the service).
**`book_ride`** `POST /rides`, 201 (`booking.py:31-33`): reuses `RideEstimateRequest` as input; `service.book` creates the ride row.
**`get_active_ride`** `GET /rides/active/current` (`booking.py:36-39`): `lifecycle_service.passenger_active` finds the open ride; if found, `matching_service.passenger_status` builds the status; else returns `None` (JSON `null`). Declared before `/rides/{ride_id}/status` on purpose-ish: different path shape, so no clash.
**`get_ride_status`** `GET /rides/{ride_id}/status` (`booking.py:42-47`): `db.scalar(select(Ride).where(Ride.id == ride_id, Ride.passenger_id == passenger.id))` runs the query and returns the first row or `None`. The second condition stops a passenger reading another passenger's ride. Missing gives 404.
**`cancel_ride`** `POST /rides/{ride_id}/cancel` (`booking.py:50-52`): `lifecycle_service.cancel_by_passenger(db, passenger, ride_id, reason, confirm)`. `confirm` likely means "I accept the cancel fee" (unverified).
**`ride_summary`** `GET /rides/{ride_id}/summary` (`booking.py:55-60`): same ownership lookup, then `lifecycle_service.summary(db, ride, 'passenger')`.
**`rate_driver`** `POST /rides/{ride_id}/rating` (`booking.py:63-68`): same lookup, then `lifecycle_service.rate(db, ride, 'passenger', score, comment)`.
**`update_saved_place`** `PATCH /saved-places/{saved_place_id}` (`booking.py:71-73`): `service.update_saved_place` edits a favorite place.

## 4. How data flows
```
passenger-app --GET /rides/9/status + Bearer--> get_current_passenger -> Passenger
   -> select Ride where id=9 and passenger_id=me --> database
   -> none? 404 : matching_service.passenger_status(db, ride)
   <- PassengerRideStatusResponse JSON
```

## 5. Try it
Needs a token. `curl -s -H "Authorization: Bearer <secret>" localhost:8000/api/v1/passengers/me/locations` (`-H` adds a header). Expect a JSON list of locations; without the header, a 401/403 error.

## 6. Can it be better?
- Good: ownership check in the query; thin routes.
- Weak: the same 4-line "find my ride or 404" block appears three times (`:44-46`, `:57-59`, `:65-67`). `book_ride` reuses the estimate schema. No idempotency key: a double tap may book two rides (unverified).
- Cleaner way:
```python
def _my_ride(db, passenger, ride_id): ...  # returns Ride or raises 404
```
or a `Depends` function.
- Security: ownership checks are present in these routes; the service methods taking `ride_id` (`cancel_by_passenger`) must check ownership too. Verify.

## 7. Check yourself
1. Why does the ride query filter on both `Ride.id` and `Ride.passenger_id`?
2. What does `get_active_ride` return when there is no active ride?
