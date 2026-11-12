# backend/app/services/home_seed_service.py

## 1. Purpose
This file puts demo content in the database so the passenger home screen is not empty: ride categories (Car, Bike, Auto), saved places (Home, Work), and three past rides. "Idempotent" (the docstring, `home_seed_service.py:11`) means you can run it many times and get the same result. The home route calls `HomeSeedService.ensure` for a logged-in passenger.

## 2. Imports, one by one

### Standard library
- `from datetime import UTC, datetime, timedelta` (`:1`). Time values and durations. *Example:* `datetime.now(UTC) - timedelta(days=2)` is two days ago.

### Third-party
- `from sqlalchemy import delete, select` (`:3`). `delete` builds a DELETE statement, `select` a SELECT. *Example:* `delete(SavedPlace).where(SavedPlace.label == 'Shop')`.
- `from sqlalchemy.orm import Session` (`:4`). Session type.

### Project
- `from app.models.ride_hailing import FareQuote, Ride, RideCategory, SavedPlace` (`:6`). Table classes.
- `from app.models.user import Passenger` (`:7`). Passenger class.

## 3. Walk through the code

### `categories` (`:13-17`)
Tuples `(code, display name, seats, base fare paise, ETA minutes, icon key)`. Example: Car, 4 seats, 18000 paise (Rs 180), 4 minutes.

### `places` (`:18-21`)
`(label, address, latitude, longitude)` for Home and Work.

### `ensure(db, passenger)` (`:23-41`)
1. `categories = self._ensure_categories(db)` returns a dict code to row (`:24`).
2. `db.execute(delete(SavedPlace).where(passenger_id == ..., label == 'Shop'))` removes an old temporary "Shop" place (`:25-26`).
3. `existing_places` is a set of labels this passenger already has (`:27`).
4. `db.add_all(generator)` adds Home/Work rows only `if label not in existing_places` (`:28-38`). This is the idempotent part.
5. If the passenger has no ride at all (`select(Ride.id)...limit(1)` is `None`), `_add_recent_rides` adds three fake rides (`:39-40`).
6. `db.commit()` saves everything (`:41`).

### `_ensure_categories(db)` (`:43-58`)
Builds `existing`, a dict from `code` to row, with a dict comprehension (`:44`). For each wanted category not present, creates a `RideCategory`, `db.add(item)`, and `db.flush()` so it gets an id; stores it in the dict. Returns the dict.

### `_add_recent_rides(db, passenger_id, categories)` (`:60-84`)
`rides` has three tuples `(pickup name, destination name, duration seconds, fare paise, completed_at)`: 2, 14 and 30 days ago. For each, builds a completed `Ride` using the `car` category (`:68-81`). `requested_at = completed_at - timedelta(minutes=duration // 60)` (`//` is whole-number division). Coordinates are the same fixed numbers for all rides. After `db.flush()` to get `ride.id`, adds a final `FareQuote` (`:82-84`). The commit happens later in `ensure`.

## 4. How data flows
```
Passenger app --GET home--> route --> HomeSeedService.ensure
    _ensure_categories --> SELECT/INSERT categories
    DELETE 'Shop' place; INSERT Home/Work if missing
    no rides? INSERT 3 rides + 3 final fares
    COMMIT
route then reads and returns home data
```

## 5. Try it
Not directly runnable (needs database). Check the time maths:
```bash
python3 -c "from datetime import *; n=datetime.now(UTC); c=n-timedelta(days=2); print(c-timedelta(minutes=2400//60))"
```
Expected: a time 40 minutes before two days ago.

## 6. Can it be better?
- **Good:** safe to repeat; uses `flush` to get ids; checks before inserting.
- **Weak:**
  - Fake rides are added for every real new passenger. These rides appear in history, driver earnings do not count them (no driver), but they are still fake data in a real account.
  - `ensure` runs on each home request and does about three queries plus a commit.
  - The same fixed coordinates are used for every fake ride.
  - Category base fares are duplicated in this file and compared to price rules in `booking_service.py`.
  - Deleting `Shop` labels is a one-time cleanup that stays forever in code.
- **Cleaner way:** run seeding once at app start or in a script (`uv run python -m app.seed`), and create only categories there. Do not make fake rides for real users.
- **Security:** the delete is limited to this passenger and the `Shop` label, so it is safe.

## 7. Check yourself
1. Which line makes `ensure` safe to run twice?
2. Why does `_ensure_categories` call `db.flush()` after `db.add(item)`?
