# backend/tests/test_outstation_booking.py

## 1. Purpose
Tests the outstation (long-distance, scheduled) booking flow in `OutstationService` (`backend/app/services/outstation_service.py`): create a request, reject short notice, then support confirms the fare, assigns a verified driver, and completes the trip. It uses an in-memory SQLite database and a fake map provider, so it needs no internet.

## 2. Imports, one by one
Standard library:
- `from datetime import UTC, datetime, timedelta` : `datetime` is a date and time, `UTC` is the zero time zone, `timedelta` is a length of time. *Example:* `datetime.now(UTC) + timedelta(hours=48)` is two days from now.

Third party:
- `pytest` : test tool (`pytest.raises`).
- `HTTPException` from `fastapi` : the error type the service raises for bad input.
- `create_engine` from `sqlalchemy` and `sessionmaker` from `sqlalchemy.orm` : database connection and session factory (a session is a work area for database reads and writes).

Project:
- `import app.models  # noqa: F401` : registers all table classes (`:8`).
- `Base` from `app.db`.
- `Driver, DriverVehicleAssignment, Notification, Vehicle` from `app/models/ride_hailing.py`; `Passenger` from `app/models/user.py`.
- `RouteResponse` from `app/schemas/maps.py` : shape of a route answer.
- `AdminOutstationUpdate, OutstationBookingCreate, OutstationLocation` from `app/schemas/outstation.py` : request shapes.
- `OutstationService` from `app/services/outstation_service.py` : logic under test.

## 3. Walk through the code, top to bottom
**`_session()`** (`:17-20`): makes a fresh in-memory database, creates all tables, returns a new session. The leading underscore means "helper, not a test".

**`_passenger(session)`** (`:23-26`): saves one fake `Passenger` (password is the fake text `hashed`) and returns it. `session.add(...)` queues the row; `session.commit()` saves it. Two statements share one line with `;`, which is legal but hard to read.

**`_MapProvider`** (`:29-31`): a **fake** (also called a stub: a stand-in object that gives fixed answers). Its `route(origin, destination)` always returns 430,000 m, 25,200 s (7 h), and a straight line. This replaces the real map service so tests are fast and stable.

**`_request(hours=48, preference='sedan')`** (`:34-40`): builds an `OutstationBookingCreate` with a pickup in Dharwad and a destination in Bengaluru. `scheduled_at` is now plus `hours`. `str | None` means the argument may be text or `None`.

**`test_request_is_stored_and_notified`** (`:43-47`)
- `OutstationService(_MapProvider())` injects the fake map (dependency injection: pass what the class needs from outside).
- `service.create(session, passenger, request)` validates, estimates, saves, and notifies. Expect status `'requested'`.
- `session.query(Notification).filter_by(...).count() == 1` counts rows in the notifications table matching the passenger and type `outstation_requested`. Exactly one is expected.

**`test_request_rejects_short_notice`** (`:50-54`): `hours=2` is less than the 4-hour minimum (`outstation_service.py:38-39`), so an `HTTPException` with status 422 is expected.

**`test_support_confirms_fare_and_assigns_verified_driver`** (`:57-77`), step by step:
1. Create a booking 72 h away, preference `suv` (`:59`).
2. `service.admin_update(session, booking.id, AdminOutstationUpdate(status='confirmed'), 1)` : the last `1` is the admin id. It sets the status and computes a fare. The test expects `estimated_fare_paise > 330000` (paise = 1/100 of a rupee, so more than Rs 3,300) (`:61`).
3. Create a `Driver` (status `active`) and a `Vehicle` (`verification_status='verified'`, 6 seats), flush so ids exist, link them with `DriverVehicleAssignment`, commit (`:62-64`).
4. `service.eligible_drivers(session, booking.id)` should return exactly one driver, and the phone is shown in local form `9876543211` without the `91` prefix (`:65-67`).
5. `admin_update(... status='driver_assigned', driver_phone_number='9876543211')` assigns the driver. Checks: status, driver name, phone, and one `outstation_driver_assigned` notification (`:68-72`).
6. `admin_update(... status='completed')` completes it (`:73-74`).
7. `service.driver_assignments(session, driver)` returns the driver's history with one completed item (`:75-77`).

## 4. How data flows
```
test -> OutstationService(fake map) -> create() -> OutstationBooking row + Notification row
admin(1) -> admin_update(confirmed) -> fare saved
         -> eligible_drivers -> assigned -> notification -> completed
driver -> driver_assignments -> [completed booking]
```

## 5. Try it
```zsh
cd backend && uv run pytest tests/test_outstation_booking.py -v
```
Expected: `3 passed`. Run one test: add `-k short_notice`.

## 6. Can it be better?
- Good: covers the main happy path and a main rule; the fake map keeps it offline; fake data only.
- Weak: the third test is long and does many things, so a failure is hard to locate. Not tested: cancel within the cutoff, the 12-hour driver conflict rule (`outstation_service.py:91,141`), a driver who is not verified, a booking over 180 days, a wrong status change. Helpers and semicolon-joined lines hurt readability. `_session()` is repeated in other test files.
- Cleaner way (opinion): move `_session`, `_passenger` into `conftest.py` fixtures, and split the third test into confirm, assign, complete tests.
```python
@pytest.fixture
def db(): ...
def test_confirm_sets_fare(db): ...
```
- Security: all values are fake. The `password_hash='hashed'` is not a real hash, which is fine for tests.

## 7. Check yourself
1. Why does the test use `_MapProvider` instead of the real map service?
2. What does the `1` in `admin_update(..., 1)` stand for?
