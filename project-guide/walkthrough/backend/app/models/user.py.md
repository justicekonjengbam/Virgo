# backend/app/models/user.py

## 1. Purpose
This file defines two database tables: `passengers` and `admin_users`. A passenger is a person who books rides. An admin is a staff member who uses the admin web app. The file is used by the auth services, repositories (`passenger_repository.py`) and the admin code. It calls only `app.db` for `Base`.

## 2. Imports, one by one
Standard library:
- `from datetime import datetime` (`user.py:1`). **datetime** (a Python type for a date plus a time. *Example:* `datetime.utcnow()` gives the current UTC time.) It is used for the column types and defaults.

Third party:
- `from sqlalchemy import Boolean, DateTime, Integer, String` (`user.py:3`). **SQLAlchemy** (a Python library that talks to a database. It turns Python classes into tables. *Example:* `String(20)` means a text column of at most 20 characters.) These four are column types. Others exist, such as `Text` and `JSON`.
- `from sqlalchemy.orm import Mapped, mapped_column` (`user.py:4`). **ORM** (Object-Relational Mapper. It maps a table row to a Python object. *Example:* a row in `passengers` becomes a `Passenger` object.) `mapped_column(...)` describes one column. `Mapped[int]` is a type hint that says what Python type the attribute has.

Project:
- `from app.db import Base` (`user.py:6`). It comes from `backend/app/db.py`. `Base` is the parent class of all models. Any class that inherits from it becomes a table.

## 3. Walk through the code, top to bottom
### `class Passenger(Base)` (`user.py:9`)
Creates the table named by `__tablename__ = 'passengers'` (line 10). Columns:
- `id` (12): integer, `primary_key=True`. **Primary key** (the unique number of each row. *Example:* passenger 7).
- `full_name` (13): text up to 120 characters.
- `phone_number` (14): text up to 20. `unique=True` means no two rows may share it. `index=True` builds a fast lookup. **Index** (a sorted helper list so the database can find a row without reading every row. *Example:* a book's index).
- `firebase_uid` (15): the id from Firebase (Google's login service). `str | None` and `nullable=True` mean it may be empty. It is also unique.
- `password_hash` (16): the stored hash of the password. **Hash** (a one-way scrambled value. *Example:* `abc` becomes `$2b$...`). The real password is never stored.
- `is_phone_verified` (17): true or false, default `False`.
- `status` (18): text, default `'active'`, not null. No check constraint limits the allowed values here.
- `last_login_at` (19): optional time. `DateTime(timezone=True)` stores the time zone.
- `updated_at` (20): default `datetime.utcnow`, and `onupdate=datetime.utcnow` refreshes it on every update.
- `deleted_at` (21): optional. It supports "soft delete" (mark a row as deleted without removing it).
- `otp_hash`, `otp_expires_at` (22-23): a hashed one-time code and its expiry. **OTP** (One-Time Password. *Example:* the 6-digit SMS code.)
- `created_at` (24): set when the row is created.

### `class AdminUser(Base)` (`user.py:27`)
Table `admin_users` (line 28). Notable columns:
- `email` (31): up to 320 characters, unique, indexed. 320 is the largest valid email length.
- `role` (34): default `'operations_admin'`.
- `is_active` (35): switch to disable an admin.
- `token_version` (36): a number inside login tokens. If you add 1, all old tokens stop working. This is a trick to log out everywhere.
- `failed_login_attempts`, `locked_until` (37-38): lock the account after too many bad passwords.
- `password_changed_at`, `last_login_at`, `created_at`, `updated_at` (39-42).

Errors: none at import. A database error such as a unique violation happens later when a row is saved.

## 4. How data flows
```
Python: Passenger(full_name='Asha', phone_number='919876543210', ...)
   -> repository db.add() + db.commit()
   -> SQLAlchemy builds INSERT INTO passengers (...) VALUES (...)
   -> database row; db.refresh() reads id back into the object
```

## 5. Try it
```zsh
cd backend
uv run python -c "from app.models.user import Passenger; print([c.name for c in Passenger.__table__.columns])"
```
`Passenger.__table__` is the table SQLAlchemy built. `.columns` lists columns. Expected: `['id', 'full_name', 'phone_number', ...]`.

## 6. Can it be better?
- Good: unique and index on lookup columns; `token_version` and lockout fields are good admin security.
- Weak: `datetime.utcnow` makes a time with no time zone and is deprecated since Python 3.12. The column says `timezone=True`, so the mix is confusing. `Passenger.status` has no CheckConstraint, but `Driver.status` has one. `Passenger.created_at` lacks `nullable=False`. The two tables repeat created/updated code that `TimestampedModel` in `ride_hailing.py` already provides.
- Cleaner way:
```python
# before
default=datetime.utcnow
# after
default=lambda: datetime.now(timezone.utc)
```
- Security: `password_hash` must be a strong hash (bcrypt or argon2); check the auth service. `otp_hash` is hashed, which is good.

## 7. Check yourself
1. What does `unique=True, index=True` give you on `phone_number`?
2. How would you log an admin out on every device with the `token_version` column?
