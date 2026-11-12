# backend/tests/test_ride_matching.py

## 1. Purpose
These tests check **ride matching**: when a passenger asks for a ride, the server must pick a nearby, verified, online driver and send that driver an offer. The code under test is `RideMatchingService` in `backend/app/services/ride_matching_service.py`. The tests use a throw-away database in memory, so no real data is touched. Only `pytest` calls this file.

## 2. Imports, one by one
Standard library:
- `from datetime import UTC, datetime, timedelta` (`:1`). `datetime` is a date and time value. `UTC` is the world-standard time zone. `timedelta` is a length of time. *Example:* `datetime.now(UTC) + timedelta(minutes=5)` is "five minutes from now". Used to set times on the ride, fare quote and GPS record.

Third-party:
- `from sqlalchemy import create_engine` (`:3`). **SQLAlchemy** is a library that lets Python code talk to a database through classes instead of raw SQL. An **engine** is the connection to one database. *Example:* `create_engine('sqlite://')` makes a database that lives only in memory.
- `from sqlalchemy.orm import sessionmaker` (`:4`). A **session** (a work area where you add, change and read rows, then `commit` to save). `sessionmaker` builds a factory for sessions. *Example:* `sessionmaker(bind=engine)()` gives one new session.

Project:
- `import app.models  # noqa: F401` (`:6`). Importing the package loads every model class so SQLAlchemy knows all the tables. `noqa: F401` tells the linter "yes, this import looks unused, keep it". Without it `create_all` would create no tables.
- `from app.db import Base` (`:7`). `Base` (the parent class of all table classes) from `backend/app/db`. `Base.metadata` lists all tables.
- `from app.models.ride_hailing import Driver, DriverCurrentLocation, DriverVehicleAssignment, FareQuote, Ride, RideCategory, Vehicle` (`:8`). Table classes: a driver, the driver's latest GPS point, the link between driver and vehicle, the price offered for a ride, the ride, a vehicle type (car), and the vehicle.
- `from app.models.user import Passenger` (`:9`). The passenger table class.
- `from app.services.ride_matching_service import RideMatchingService` (`:10`). The class being tested.

## 3. Walk through the code
### `_session()` (`:13-16`)
Makes an empty SQLite database in memory, creates every table (`Base.metadata.create_all(engine)`), and returns a new session. Each test calls it, so each test starts clean. The leading underscore means "private helper, not a test".

### `_ride(session, driver_ready=True)` (`:19-30`)
A **fixture-like helper** (it builds the starting data for tests).
1. Creates a `Passenger` and a `RideCategory` (`:20-21`) and `session.add_all([...])` queues them. `session.flush()` (send the queued rows to the database now, without final save) so they get ids (`:22`).
2. If `driver_ready`, creates an online, active `Driver`, a verified `Vehicle`, then a `DriverVehicleAssignment` and a `DriverCurrentLocation` at lat 15.3643, lon 75.1195 (`:23-27`).
3. Creates a `Ride` with status `'searching'`, pickup near Vidyanagar and a destination at the railway station (`:28`), plus a `FareQuote` of 18000 paise (100 paise = 1 rupee, so Rs 180) valid 5 minutes (`:29`). `session.commit()` saves it all.
4. Returns `(ride, driver)`; the driver is `None` when `driver_ready=False` (`:30`).

### Test 1 `test_matching_assigns_nearby_verified_online_driver_after_acceptance` (`:33-44`)
- `service.dispatch(session, ride)` picks the nearest eligible driver and creates a `RideDispatchOffer` row (`ride_matching_service.py:40-54`). `session.commit()` saves it.
- `service.current_offer(session, driver)` is what the driver app asks: "do I have an offer?" The test checks it points to this ride (`:38-39`).
- `service.respond(session, driver, current.offer_id, 'accepted')` is the driver pressing Accept (`:40`). `session.refresh(ride)` reloads the ride from the database so we see the new values.
- Asserts: ride status becomes `'driver_arriving'`, `ride.driver_id` is the driver, and `passenger_status(...).driver_name` is `'Driver'` (`:42-44`).

### Test 2 `test_matching_cancels_when_no_eligible_driver_exists` (`:47-52`)
No driver exists. `dispatch` must return `None`, set the ride to `'cancelled'` with reason `'no_eligible_driver'` (see `ride_matching_service.py:44-49`).

### Test 3 `...uses_dharwad_city_when_driver_has_no_gps_fix` (`:55-67`)
Sets the driver's `operating_city` to `'Dharwad'`, deletes the GPS row, and moves the pickup to Dharwad's coordinates. With no GPS, the service falls back to a fixed city centre (`_driver_coordinates`, `ride_matching_service.py:281-285`). The offer must go to this driver.

### Test 4 `...uses_operating_city_when_gps_fix_is_stale` (`:70-80`)
The GPS record is 6 minutes old. The service treats GPS older than 5 minutes as stale (`ride_matching_service.py:270`), so it uses the city `'Hubballi'` instead. The offer must still go to this driver.

Note: on lines `:34`, `:48` and others, `; ` joins two statements on one line. It works, but is not usual style.

## 4. How data flows
```
test --> _ride() --> in-memory DB (passenger, driver, vehicle, GPS, ride)
test --> service.dispatch(ride) --> finds nearest driver --> adds Offer row
test --> service.current_offer(driver) --> offer info (as driver app sees it)
test --> service.respond(..., 'accepted') --> ride.status = driver_arriving
test --> assert on ride and passenger_status
```

## 5. Try it
```zsh
cd backend
uv run pytest tests/test_ride_matching.py -v
```
`uv run` uses the project environment; `-v` lists each test. Expected: `4 passed`.

## 6. Can it be better?
- Good: real service code runs against a real (in-memory) database, so the tests catch real bugs. Edge cases (no GPS, stale GPS, no driver) are covered.
- Weak: `_session()` never closes the session. `;` on one line hurts readability. No test for: driver too far away, driver rejecting an offer, expired offer, driver already on another ride. Test 3 and 4 do not check the pickup is near city centre (they rely on coordinates written by hand).
- Cleaner way (opinion): use a pytest fixture.
```python
@pytest.fixture
def session():
    s = _session()
    yield s
    s.close()
```
- Security: test data uses fake phone numbers and `password_hash='hashed'`; nothing real.

## 7. Check yourself
1. Why does `_ride` call `session.flush()` before using `passenger.id`?
2. After how many minutes does the service ignore a driver's GPS point, and what does it use instead?
