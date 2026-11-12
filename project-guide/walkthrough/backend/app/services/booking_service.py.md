# backend/app/services/booking_service.py

## 1. Purpose
This file turns "I want a ride from A to B" into a price estimate and then a saved ride. It also lists known places and updates a passenger's saved place (Home/Work). API routes for booking call `BookingService`. It calls the map service (`map_provider_service.py`), the matching service (`ride_matching_service.py`), the realtime publishers (`realtime_events.py`), and the database models.

## 2. Imports, one by one

### Standard library
- `from datetime import UTC, datetime` (`booking_service.py:1`). Date/time values and the UTC zone. *Example:* `datetime.now(UTC)` is the current time in UTC.
- `from dataclasses import dataclass` (`:2`). A decorator (a line starting with `@` that changes the class below it) that writes `__init__` for you. *Example:* `@dataclass class P: x: int` lets you write `P(3)`.
- `from zoneinfo import ZoneInfo` (`:3`). Time zones by name. *Example:* `ZoneInfo('Asia/Kolkata')` is Indian time. Used for the night charge.

### Third-party
- `from fastapi import HTTPException, status` (`:5`). Raise HTTP errors with named codes.
- `from sqlalchemy import select` (`:6`). Builds a SELECT query. *Example:* `select(Ride).where(Ride.id == 1)`.
- `from sqlalchemy.exc import IntegrityError` (`:7`). The error the database gives when a rule (unique key, constraint) is broken.
- `from sqlalchemy.orm import Session` (`:8`). A database session; used as a type.

### Project
- `from app.models.ride_hailing import FareLineItem, FareQuote, LocationCatalog, Ride, RideCategory, RideEvent, SavedPlace` (`:10`). Database table classes in `backend/app/models/ride_hailing.py`.
- `from app.models.user import Passenger` (`:11`). Passenger table class.
- `from app.schemas.booking import ...` (`:12`). Pydantic shapes for requests and answers (`FareItemResponse`, `LocationOptionResponse`, `RideBookingResponse`, `RideEstimateRequest`, `RideEstimateResponse`, `SelectedPlaceRequest`).
- `from app.schemas.home import PlaceResponse` (`:13`). The answer shape for a saved place.
- `from app.services.ride_matching_service import RideMatchingService` (`:14`). Finds a driver for a ride.
- `from app.services.realtime_events import publish_driver_offer, publish_passenger_status` (`:15`). Send live messages (websocket pushes) to driver and passenger apps.
- `from app.services.map_provider_service import MapProviderService` (`:16`). Gets routes (distance, time, geometry) from a map provider.

## 3. Walk through the code

### `BookingLocation` (`:19-26`)
`@dataclass(frozen=True)` makes a small read-only record: `id`, `place_id`, `name`, `formatted_address`, `latitude`, `longitude`. `frozen=True` means you cannot change it after creation. *Example:* `BookingLocation(None, 'abc', 'Home', 'Addr', 15.3, 75.1)`. It is one common shape for both catalog places and map-picked places.

### `class BookingService` class attributes (`:29-42`)
- `matching_service` and `map_service` (`:30-31`) are created once and shared.
- `active_statuses` (`:32`) lists ride states that count as "still going".
- `catalog` (`:33-39`) is a seed list of five places (name, address, latitude, longitude).
- `per_km_paise` (`:40`): price per km in paise (1 rupee = 100 paise). 1500 = Rs 15.
- `night_surcharge_rate = 0.20` (`:41`): 20 percent extra at night.
- `india_timezone` (`:42`).

### `locations(db)` (`:44-48`)
`db.scalar(select(LocationCatalog.id).limit(1))` returns the first id or `None`. If the table is empty, `db.add_all(...)` adds the five catalog rows and `db.commit()` saves them. Then it returns all rows ordered by name, each converted by `_location`. So the first call fills the table (a "lazy seed"). Output: list of `LocationOptionResponse`.

### `estimate(db, request)` (`:50-75`)
1. `_locations_for_request` gives pickup and destination (`:51`).
2. `db.get(RideCategory, request.category_id)` fetches one row by primary key, or `None`. Missing or inactive gives 404 (`:52-54`).
3. `self.map_service.route((lat, lon), (lat, lon))` returns an object with `distance_meters`, `duration_seconds`, `toll_fare_paise`, `geometry` (`:55-58`).
4. `distance_km = round(max(1.2, meters/1000), 1)`: at least 1.2 km, one decimal (`:59`). `duration` is at least 1 minute (`:60`).
5. Price: base fare + `round(distance_km * rate)` (`:61-63`). Unknown category code falls back to 1200.
6. Night charge: `_is_night(datetime.now(self.india_timezone))` is true from 22:00 to 04:59 (`:64`, `:151-153`). Charge = 20 percent of subtotal.
7. `parking_fare = 0` is a placeholder (`:65`). `toll_tax` comes from the route.
8. Five `FareItemResponse` lines are built (`:67-73`); `{per_km_rate / 100:g}` formats 1500/100 as `15`. The total is `sum(...)` (`:74`).
9. Returns `RideEstimateResponse` (`:75`).
*Example:* car, base 18000, 5.0 km: distance 7500, subtotal 25500, day time total 25500 + toll.

### `book(db, passenger, request)` (`:77-105`)
1. Look for an active ride of this passenger: `Ride.status.in_(self.active_statuses)` is SQL `status IN (...)`. If found, 409 (`:78-86`).
2. `self.estimate` again to get a price (`:87`) and reload the category (`:88`).
3. Build `Ride(...)` with addresses, coordinates, estimated distance and time, and route (`:89`). Status starts as `'searching'`.
4. `db.add(ride)`; `db.flush()` sends the INSERT to the database inside the open transaction without committing, so `ride.id` exists. If the database refuses (unique index for one active ride per passenger, I think; check the model), `IntegrityError` is caught, `db.rollback()` undoes, and 409 is raised (`:90-95`). This protects against two fast taps.
5. Create a `FareQuote` (`is_final=False`) and flush to get its id (`:96`). Create `FareLineItem` rows, with `item_type` made from the label: `Base fare` becomes `base_fare` (`:97`).
6. Add a `RideEvent` (an audit log line) `ride_requested` (`:98`).
7. `self.matching_service.dispatch(db, ride)` picks a driver and returns an offer or `None` (`:99`).
8. `db.commit()` saves everything at once; `db.refresh(ride)` reloads values (`:100`).
9. Publish live updates to passenger and, if an offer exists, to the driver (`:101-103`).
10. Message text depends on whether status is still `searching` (`:104`). Returns `RideBookingResponse` (`:105`).
Note: publishing happens after commit, so apps never hear about a ride that was rolled back. Good.

### `update_saved_place(db, passenger, saved_place_id, request)` (`:107-130`)
Finds the saved place that belongs to this passenger (`:108`; this check stops one user editing another's place). The new location is either a map pick (`request.location`) or a catalog row (`request.location_id`) (`:111-117`). Copies address, lat, lon, and place id, commits, and returns `PlaceResponse`. The `request` argument has no type hint; the shape comes from `schemas/home.py` (I am not sure of the exact class name).

### `_locations_for_request` (`:132-149`)
Either uses `request.pickup`/`request.destination` (map-picked), or looks up catalog ids (404 if missing). Rejects the same place: equal `place_id` or both coordinates closer than 0.0001 degrees (about 11 metres) (`:142-146`), with 400. Then `ensure_in_service_area` raises if outside the supported area (`:147-148`).

### Static helpers (`:151-165`)
`@staticmethod` means the method does not need `self`. `_is_night`, `_location` (to API shape; `getattr(item, 'place_id', None)` handles catalog rows that have no `place_id`), `_catalog_location` (place id becomes `catalog:7`), `_selected_location`.

## 4. How data flows
```
Passenger app --POST estimate/book--> route --> BookingService.book
   active ride? --yes--> 409
   estimate --> MapProviderService.route --> map API
   INSERT Ride, FareQuote, FareLineItem, RideEvent
   RideMatchingService.dispatch --> offer
   COMMIT
   publish_passenger_status --> passenger app
   publish_driver_offer ------> driver app
```

## 5. Try it
Not directly runnable (needs database and map provider). Check the rate math in Python:
```bash
python3 -c "km=5.0; print(round(km*1500)+18000)"
```
Expected `25500`.

## 6. Can it be better?
- **Good:** one-active-ride check plus database guard; publishing after commit; money in whole paise (no float money).
- **Weak:**
  - `book` is long and does a lot (`:77-105`). Split into `_create_ride`, `_save_fare`.
  - `estimate` is called inside `book`, then the category is loaded twice (`:52`, `:88`).
  - Lines with `;` (`:96`, `:100`) hurt readability.
  - Rates, catalog and night rules are hard-coded in code; move to settings or the database.
  - `parking_fare = 0` is a dead placeholder.
  - Catalog seeding inside a read method (`locations`) writes to the database on a GET request.
  - `update_saved_place` has an untyped `request`.
  - `estimate` uses the server clock, so the quoted price at estimate time may differ from the booked price.
- **Cleaner way:**
```python
# before: request
# after
def update_saved_place(self, db, passenger, saved_place_id, request: SavedPlaceUpdateRequest) -> PlaceResponse: ...
```
- **Security:** ownership check at `:108` is good. Coordinates come from the client, so the service area check (`:147`) must stay.

## 7. Check yourself
1. Why does `book` call `db.flush()` before `db.commit()`?
2. How is the night charge decided, and in which time zone?
