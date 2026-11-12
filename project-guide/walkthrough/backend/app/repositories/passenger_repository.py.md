# backend/app/repositories/passenger_repository.py

## 1. Purpose
The repository for passengers. It hides the database queries for the `passengers` and `passenger_profiles` tables. The passenger auth service calls it. It calls the model classes from `models/user.py` and `models/ride_hailing.py`. It has the same style as `driver_repository.py`.

## 2. Imports, one by one
Third party:
- `from sqlalchemy import select` (`passenger_repository.py:1`). Builds a query object. *Example:* `select(Passenger).where(Passenger.id == 1)`.
- `from sqlalchemy.orm import Session` (2). One open conversation with the database. Used for type hints.

Project:
- `from app.models.ride_hailing import PassengerProfile` (4). From `models/ride_hailing.py`. The profile table.
- `from app.models.user import Passenger` (5). From `models/user.py`. The passenger table.

## 3. Walk through the code, top to bottom
`class PassengerRepository` (8). No state. Each method takes `db`.
- `get_by_phone(db, phone_number) -> Passenger | None` (9-10). `db.scalar(...)` runs the query and returns the first row or `None`. Example: `get_by_phone(db, '919876543210')`.
- `get_verified_by_phone(db, phone_number)` (12-19). Same, but also needs `is_phone_verified IS TRUE` (`.is_(True)`) and `status == 'active'`. Used to allow login only for verified, active people.
- `get_by_firebase_uid(db, firebase_uid)` (21-22). Lookup by Firebase id.
- `get_profile(db, passenger_id)` (24-25). `db.get(PassengerProfile, passenger_id)` finds by primary key. The profile's primary key is the passenger id, so this works.
- `create_profile(db, passenger_id)` (27-32). Builds `PassengerProfile(passenger_id=...)`, `add`, `commit` (save for good), `refresh` (reload to get default values such as `created_at`), return.
- `create(db, passenger)` (34-38) and `save(db, passenger)` (40-44). Both add, commit, refresh. They are identical.

Errors: `IntegrityError` on a duplicate phone or Firebase id, or a profile that already exists.

## 4. How data flows
```
auth service -> get_verified_by_phone(db, '9198...')
   -> SELECT ... WHERE phone=... AND is_phone_verified AND status='active'
   -> Passenger object or None -> service checks password
```

## 5. Try it
Not directly runnable alone. Use an in-memory database:
```zsh
cd backend
uv run python - <<'PY'
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db import Base
import app.models
from app.models.user import Passenger
from app.repositories.passenger_repository import PassengerRepository
e = create_engine('sqlite://'); Base.metadata.create_all(e)
r = PassengerRepository()
with Session(e) as db:
    p = r.create(db, Passenger(full_name='Asha', phone_number='919876543210', password_hash='x'))
    print(p.id, r.get_verified_by_phone(db, p.phone_number))
PY
```
Expected: `1 None`, because the new passenger is not phone-verified yet.

## 6. Can it be better?
- Good: very readable; `get_verified_by_phone` puts the rules in one place.
- Weak: `create` and `save` duplicate each other. Every method commits, so two steps (create passenger, then create profile) are two transactions; if the second fails, you keep a passenger with no profile. `get_by_phone` ignores `deleted_at`, so soft-deleted users may be found (check the services).
- Cleaner way: one `save` method, and let the service call `db.commit()` once at the end.
- Security: parameters are bound, so no SQL injection.

## 7. Check yourself
1. What three conditions does `get_verified_by_phone` require?
2. Why does `create_profile` call `db.refresh(profile)` after `commit`?
