# backend/app/repositories/driver_repository.py

## 1. Purpose
This file is the only place that talks to the database about drivers, their active vehicle and their documents. A **repository** (a class that hides database queries behind simple method names. *Example:* `repo.get_by_phone(db, '9198...')` instead of writing SQL each time). Services such as the driver auth service call these methods. This file calls `app/models/ride_hailing.py` for the table classes.

## 2. Imports, one by one
Third party:
- `from sqlalchemy import select` (`driver_repository.py:1`). `select(Driver)` builds a "SELECT * FROM drivers" query object. It does not run it. Example: `select(Driver).where(Driver.id == 3)`.
- `from sqlalchemy.orm import Session` (2). **Session** (one open conversation with the database. It tracks objects you added or changed. *Example:* `db.add(x)`, then `db.commit()` saves.) Here it is used as a type hint for the `db` argument.

Project:
- `from app.models.ride_hailing import Driver, DriverDocument, DriverVehicleAssignment, Vehicle` (4). Four table classes from `models/ride_hailing.py`.

## 3. Walk through the code, top to bottom
`class DriverRepository` (7). The docstring (8) says it is the "persistence boundary". **Persistence** (saving data so it survives restarts). Every method takes `db` first, so the class has no state.

Session calls used here:
- `db.scalar(query)` runs the query and returns the first value, or `None` if no row.
- `db.scalars(query)` returns many first-column values (here, many objects).
- `db.get(Model, id)` finds one row by primary key.
- `db.add(obj)` puts the object in the session. `db.flush()` sends the SQL now but does not finish the transaction (so `obj.id` becomes available). `db.commit()` ends the transaction and makes it permanent. `db.refresh(obj)` reloads the object from the database. `db.rollback()` cancels everything since the last commit.

Methods:
- `get_by_firebase_uid(db, firebase_uid) -> Driver | None` (10-11). Finds a driver by the Firebase id. Example: `get_by_firebase_uid(db, 'abc')` returns a `Driver` or `None`.
- `get_by_phone(db, phone_number)` (13-14). Same, by phone.
- `create(db, driver)` (16-20). Adds, commits, refreshes, returns the driver.
- `save(db, driver)` (22-26). The same three steps. It is identical to `create` (see section 6).
- `get_active_assignment(db, driver_id)` (28-33). Finds the assignment whose `ended_at` is empty (`.is_(None)` makes `IS NULL`). `order_by(started_at.desc())` puts the newest first, and `db.scalar` takes the first one.
- `get_document(db, driver_id, document_type)` (35-39). One document of one type, or `None`.
- `get_documents(db, driver_id)` (41-42). All documents as a list.
- `get_active_vehicle(db, driver_id)` (44-46). Calls `get_active_assignment`, then `db.get(Vehicle, assignment.vehicle_id)`. Returns `None` if no assignment. Two queries.
- `create_vehicle_and_assignment(db, driver, vehicle)` (48-55). Adds the vehicle, `flush()` so it gets an id, creates the link row with `driver.id` and `vehicle.id`, commits, returns the link.
- `create_complete_registration(db, driver, vehicle, documents)` (57-72). The whole sign-up in one **transaction** (a group of changes that all succeed or all fail. *Example:* a bank transfer: debit and credit together). Steps: add driver, flush (get id), add vehicle, flush, add assignment, loop to set `document.driver_id` and add each document, commit once, refresh. In `except Exception` (70) it calls `db.rollback()` and `raise`, which re-raises the same error to the caller.

Errors: `IntegrityError` if a phone, Firebase id or registration number already exists.

## 4. How data flows
```
service --create_complete_registration(db, driver, vehicle, docs)--> repository
   add driver -> flush -> add vehicle -> flush -> add assignment -> add docs
   -> commit  (ok: return driver)
   -> error   (rollback, re-raise to service -> API returns an error)
```

## 5. Try it
Not directly runnable without a database session. A tiny check with an in-memory SQLite database:
```zsh
cd backend
uv run python - <<'PY'
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db import Base
import app.models
from app.repositories.driver_repository import DriverRepository
e = create_engine('sqlite://'); Base.metadata.create_all(e)
with Session(e) as db:
    print(DriverRepository().get_by_phone(db, '919876543210'))
PY
```
`create_engine('sqlite://')` makes a temporary database in memory. `create_all` builds the tables. Expected output: `None`.

## 6. Can it be better?
- Good: small methods, clear names, return type hints, one transaction for registration with rollback.
- Weak: `create` and `save` are the same code. `get_active_vehicle` makes two queries (one join would do). `create_vehicle_and_assignment` has no rollback. The methods commit by themselves, so a service cannot group several repository calls in one transaction. `get_active_assignment` has no limit of one, so ordering hides bad data (two active rows).
- Cleaner way:
```python
# before
def get_active_vehicle(self, db, driver_id):
    assignment = self.get_active_assignment(db, driver_id)
    return db.get(Vehicle, assignment.vehicle_id) if assignment else None
# after (one query)
return db.scalar(select(Vehicle).join(DriverVehicleAssignment, DriverVehicleAssignment.vehicle_id == Vehicle.id)
    .where(DriverVehicleAssignment.driver_id == driver_id, DriverVehicleAssignment.ended_at.is_(None)))
```
- Security: queries use bound parameters, so SQL injection is not a risk here.

## 7. Check yourself
1. Why does `create_complete_registration` call `db.flush()` before using `driver.id`?
2. What happens to the driver row if adding a document fails in the middle?
