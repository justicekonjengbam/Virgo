# backend/app/models/ride_hailing.py

## 1. Purpose
This is the big table map of the ride-hailing business. It defines 25 tables: drivers, vehicles, documents, rides, offers, fares, payments, ratings, sessions, notifications, support, outstation bookings, audit log and outbox. Repositories and services (for example `repositories/driver_repository.py`) import these classes to read and write rows. The file calls only `app.db` (for `Base`). `models/__init__.py` imports all of them so SQLAlchemy knows them.

## 2. Imports, one by one
Standard library:
- `from __future__ import annotations` (`ride_hailing.py:1`). It makes type hints be read as text, not run at once. *Example:* `Mapped[str | None]` is safe on every Python version.
- `from datetime import datetime` (3). A date+time type. Used in `Mapped[datetime]` and `datetime.utcnow`.
- `from decimal import Decimal` (4). **Decimal** (exact decimal numbers without float rounding errors. *Example:* `Decimal('0.10') + Decimal('0.20') == Decimal('0.30')` is true; with floats it is false.) Used for latitude, longitude and rating.

Third party:
- `from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint` (6). **SQLAlchemy** is the library that turns Python classes into database tables. Each name:
  - `JSON`: a column that stores a dict. *Example:* `{"a": 1}`.
  - `Boolean`, `Integer`, `String(n)`, `Text` (long text), `DateTime(timezone=True)`.
  - `Numeric(9, 6)`: a number with 9 digits in total, 6 after the point. *Example:* `12.971599`.
  - `ForeignKey('drivers.id')`: this column holds an id that must exist in another table.
  - `Index`: a fast lookup helper over one or more columns.
  - `UniqueConstraint`: a rule that a value (or a pair) cannot repeat.
  - `CheckConstraint`: a rule written in SQL, like `score BETWEEN 1 AND 5`.
- `from sqlalchemy.orm import Mapped, mapped_column` (7). `mapped_column` describes a column. `Mapped[T]` is its Python type. `Mapped[str | None]` means the value can be empty (NULL).

Project:
- `from app.db import Base` (9). From `backend/app/db.py`. All table classes inherit from `Base`.

## 3. Walk through the code, top to bottom
**Ideas used everywhere**
- `__tablename__` is the real table name in the database.
- `__table_args__` is a tuple of table-level rules (indexes and constraints).
- `nullable=False` means the column must always have a value.
- `default=...` is filled by Python when you insert and give no value.
- **ondelete** on a `ForeignKey` says what happens when the parent row is deleted. `CASCADE` deletes children too. `RESTRICT` blocks the delete. `SET NULL` empties the column.
- **Paise** (1/100 of a rupee. *Example:* 25000 paise = Rs 250). Money is stored as integer `*_paise` columns. This avoids rounding errors.
- Every table has `id` as an integer primary key unless noted.

### `class TimestampedModel` (`ride_hailing.py:12-14`)
A *mixin* (a small class that other classes inherit just to get its columns). It adds `created_at` and `updated_at`. `onupdate=datetime.utcnow` refreshes `updated_at` on each update. Note it does not inherit `Base`, so it is not a table. Classes write `(TimestampedModel, Base)`.

### Table by table
- `PassengerProfile` (17-23), table `passenger_profiles`. Its primary key is `passenger_id`, a foreign key to `passengers.id` (a one-to-one extra record). Holds email, photo URL, language (default `'en'`), accessibility JSON.
- `Driver` (26-40), `drivers`. Check rule at line 28: `status` must be `pending`, `active`, `suspended` or `deactivated`. Index `ix_drivers_status_city` on `(status, operating_city)`. Columns: `firebase_uid` (unique), name, phone (unique), email, status (default `'pending'`), city, photo, `rating_average` `Numeric(3,2)` (like `4.85`), `completed_rides_count`, `is_online`, `last_online_at`.
- `Vehicle` (43-54), `vehicles`. Unique `registration_number` (45). Check: `verification_status` in `pending/verified/rejected/expired`. Columns: make, model, year, color, `category_code` (car, bike, auto), `seat_count` (default 4).
- `DriverVehicleAssignment` (57-64), `driver_vehicle_assignments`. Links a driver to a vehicle over time. `ended_at` empty means the assignment is still active. `driver_repository.get_active_assignment` filters on `ended_at IS NULL`. Index on `(driver_id, ended_at)` makes that fast. Deleting a vehicle is blocked (`RESTRICT`).
- `DriverDocument` (67-79), `driver_documents`. One document per type per driver (`UniqueConstraint('driver_id','document_type')`, line 69). Has `storage_key` (where the file is stored, not the file), `verification_status`, review note, `reviewed_by`, `reviewed_at`, `expires_at`.
- `SavedPlace` (82-91), `saved_places`. A passenger's labeled place such as "Home". Unique `(passenger_id, label)`. Has Google place id and lat/long.
- `LocationCatalog` (94-100), `location_catalog`. A fixed list of known places (unique name).
- `EmergencyContact` (103-110), `emergency_contacts`. Unique `(passenger_id, phone_number)`. Careful: the column is named `relationship` (line 110). SQLAlchemy also has a function named `relationship`, but this file does not import it, so there is no clash.
- `ServiceArea` (113-120), `service_areas`. A city where service runs. `boundary_geojson` is a JSON shape. Default country `'IN'`.
- `RideCategory` (123-132), `ride_categories`. Code (unique), display name, seats, `base_fare_paise`, arrival minutes, icon key, active flag.
- `Ride` (135-164), `rides`. The central table. Check rule on `status` (line 137) lists the whole life: `requested, searching, driver_assigned, driver_arriving, driver_arrived, in_progress, completed, cancelled`. Two indexes for passenger history and driver history. Foreign keys to passenger, driver, vehicle, category, service area (all `RESTRICT`, so history cannot be lost). Pickup and destination address, place id, lat/long. Time stamps for each step. Cancellation reason and who cancelled. Estimated and final distance/duration. `route_geojson` JSON.
- `RideStop` (167-176), `ride_stops`. Extra stops. Unique `(ride_id, stop_order)`.
- `RideEvent` (179-188), `ride_events`. A log of what happened to a ride. Note: it inherits only `Base` (no timestamps). Has `actor_type`, `actor_id`, `event_type`, `payload` JSON, `occurred_at`.
- `RideDispatchOffer` (191-202), `ride_dispatch_offers`. An offer of a ride to one driver. Unique `(ride_id, driver_id)` so one offer per driver. Has `expires_at` (required) and `responded_at`.
- `FareQuote` (206-214), `fare_quotes`. A price for a ride. `amount_paise`, `is_final`, currency default `'INR'`.
- `FareLineItem` (217-223), `fare_line_items`. A part of a fare (base, distance...). The column is `metadata_json`, not `metadata`, because `metadata` is a reserved name on SQLAlchemy models.
- `Payment` (226-237), `payments`. Unique `(provider, provider_payment_id)` and a unique `idempotency_key`. **Idempotency key** (a unique tag so that repeating the same request cannot charge twice. *Example:* the app sends key `abc`; a retry with `abc` is rejected.)
- `Rating` (240-247), `ratings`. One per `(ride_id, rater_type)`. Check `score BETWEEN 1 AND 5`.
- `DeviceSession` (250-260), `device_sessions`. A logged-in device. Stores `refresh_token_hash` (unique), not the raw token. `revoked_at` marks a logout.
- `DriverCurrentLocation` (263-271), `driver_current_locations`. The driver id is the primary key, so each driver has exactly one row: the latest position. Has heading, accuracy, speed, `recorded_at` (indexed).
- `Notification` (274-283), `notifications`. For a passenger. `read_at` empty means unread. `data_json` extra payload.
- `SupportTicket` (286-298), `support_tickets`. Status default `'open'`. `ride_id` and `assigned_admin_id` use `SET NULL`. `assigned_admin_id` points to `admin_users.id` in `user.py`.
- `OutstationBooking` (301-332), `outstation_bookings`. A booking for a long trip at a future `scheduled_at`. Check rule on status (line 304). Three indexes. Lat/long here are optional.
- `AuditLog` (335-345), `audit_logs`. Who did what to which entity. `metadata_json` again.
- `OutboxEvent` (348-357), `outbox_events`. **Outbox pattern** (write the event into the database in the same transaction as the change, and a worker publishes it later, so no event is lost. *Example:* ride saved + event row saved together). `published_at` empty means not published yet.

Errors: none at import. Violating a rule (for example, `status='bogus'` on a ride) raises an `IntegrityError` from the database when you commit.

## 4. How data flows
```
service code            repository               this file               database
Driver(status='x') --> db.add + commit --> CheckConstraint ck_drivers_status --> IntegrityError
Driver(status='pending') --> INSERT INTO drivers ... --> row with id, created_at
```

## 5. Try it
```zsh
cd backend
uv run python -c "from app.models.ride_hailing import Ride; print(Ride.__table__.c.status.type, [i.name for i in Ride.__table__.indexes])"
```
`.c` is the column collection of the table. Expected: `VARCHAR(24)` and the two index names for rides.

## 6. Can it be better?
- Good: strong database rules (check constraints, unique pairs, indexes), money as integers, careful `ondelete` choices, outbox and audit tables.
- Weak:
  - `datetime.utcnow` returns a time without a zone and is deprecated in Python 3.12 (opinion: use zone-aware times).
  - Status values are text with the allowed list repeated in SQL strings; `Ride.status`, `Payment.status`, `RideDispatchOffer.status`, `Payment.method` and `SupportTicket.status` have no check rule, so bad values are possible.
  - `Ride.driver_id` has a `RESTRICT` rule, so a driver with rides can never be deleted (maybe intended).
  - A ride can have many `Payment` rows but no rule prevents two successful payments.
  - `FareLineItem` has no index on `fare_quote_id`; reading line items of a quote may be slow later (some databases do not index foreign keys on their own).
  - One 357-line file; no relationships defined, so every join is written by hand.
- Cleaner way:
```python
# before
status: Mapped[str] = mapped_column(String(24), default='requested')
# after: add a check, like Driver does
__table_args__ = (CheckConstraint("status IN ('pending','paid','failed')", name='ck_payments_status'),)
```
- Security: `DriverDocument.document_number` (licence, Aadhaar) is sensitive personal data stored as plain text. Consider encryption or storing only a masked value. This is my opinion; check the law that applies to you.

## 7. Check yourself
1. What is the difference between `ondelete='CASCADE'` and `ondelete='RESTRICT'`, and why does `Ride.passenger_id` use `RESTRICT`?
2. How does the app know which vehicle a driver is using now? (Hint: look at `DriverVehicleAssignment.ended_at`.)
