# backend/app/services/home_service.py

## 1. Purpose
This file builds the data for the passenger home screen. It collects saved places, ride categories (like Sedan or SUV) and the last three finished rides. A route file in `backend/app/api/` calls `HomeService.get_home` and sends the result to the passenger app. It calls `HomeSeedService` (`backend/app/services/home_seed_service.py`) first so a new passenger has starter data.

## 2. Imports, one by one
Third-party:
- `from sqlalchemy import select` (line 1). **SQLAlchemy** is a Python library that talks to a database. `select(...)` builds a SQL SELECT query as a Python object. *Example:* `select(Ride).where(Ride.id == 5)` means `SELECT * FROM rides WHERE id = 5`. It is needed to read rows. It can also build `select(func.count())`.
- `from sqlalchemy.orm import Session` (line 2). A **Session** (one open conversation with the database; it remembers loaded rows and sends changes). Here it is only used as a type hint for the `db` argument. *Example:* `db.get(Ride, 5)`.

Project:
- `from app.models.ride_hailing import FareQuote, Ride, RideCategory, SavedPlace` (line 4). These are **ORM models** (Python classes where each class is a database table and each object is a row). Source: `backend/app/models/ride_hailing.py`.
- `from app.models.user import Passenger` (line 5). The passenger table class, in `backend/app/models/user.py`.
- `from app.schemas.home import HomeResponse, PlaceResponse, RecentRideResponse, RideCategoryResponse` (line 6). **Schemas** (Pydantic classes that describe the JSON a route returns and check its shape). Source: `backend/app/schemas/home.py`.
- `from app.services.home_seed_service import HomeSeedService` (line 7). A helper that inserts default places and categories when missing.

## 3. Walk through the code, top to bottom
### `class HomeService` and `__init__` (lines 10-12)
`__init__` runs when you write `HomeService()`. It makes one `HomeSeedService` and keeps it in `self.seed_service`. Output: nothing (`-> None`).

### `get_home(self, db, passenger)` (lines 14-26)
**What it does:** returns a `HomeResponse` for one passenger. **Input:** an open `db` session and the logged-in `passenger`. **Output:** a `HomeResponse` object.
- Line 15: `self.seed_service.ensure(db, passenger)` makes sure starter data exists. I am not sure if it commits; check `home_seed_service.py`.
- Line 16: `db.scalars(select(SavedPlace).where(...).order_by(SavedPlace.label)).all()`. `select(...)` builds the query. `.where(SavedPlace.passenger_id == passenger.id)` keeps only this passenger's places. `.order_by(SavedPlace.label)` sorts A to Z. `db.scalars(query)` runs it and gives one model object per row. `.all()` turns the result into a list.
- Line 17: same idea for `RideCategory`. `.is_(True)` produces SQL `IS TRUE`, so only active categories come back, sorted by id.
- Lines 18-20: the last 3 rides with status `'completed'`, newest first (`Ride.completed_at.desc()`), cut with `.limit(3)`.
- Lines 21-26: builds the response. A **list comprehension** (a one-line loop that builds a list, e.g. `[x*2 for x in [1,2]]` gives `[2,4]`) turns each model into a schema object. `float(item.latitude)` converts a database `Decimal` (exact number type) to a normal float so JSON works.
- Line 25 calls `self._recent_ride` for each ride.

### `_recent_ride(self, db, ride)` (lines 28-30)
Finds the final fare of one ride. `db.scalar(select(FareQuote.amount_paise).where(FareQuote.ride_id == ride.id, FareQuote.is_final.is_(True)))` runs the query and returns the first single value, or `None`. `or 0` turns `None` into 0. **Paise** means 1/100 of a rupee, so 25000 paise is Rs 250. It then builds a `RecentRideResponse`.
Errors: none raised here. If the database is down, SQLAlchemy raises its own error.

## 4. How data flows
```
Passenger app --GET /home--> route --> HomeService.get_home
   HomeSeedService.ensure -> DB (insert defaults if missing)
   DB <- 3 SELECTs (places, categories, rides) + 1 SELECT per ride (fare)
   HomeResponse (JSON) --> Passenger app
```
Note: 3 recent rides means 3 extra queries (the "N+1" pattern, simplified: one query plus N more).

## 5. Try it
Not directly runnable alone. Start the backend and call the route with a passenger token:
`curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/...` (check the real path with `rg -n "HomeService" backend/app/api`). Expected: JSON with `passenger_name`, `saved_places`, `ride_categories`, `recent_rides`.

## 6. Can it be better?
- Good: small, readable, one job.
- Weak: the 3 fare lookups cause extra queries (line 25 and 29). Long single lines (23, 24) are hard to read. No tests seen here.
- Cleaner way: fetch the fares in one query with `FareQuote.ride_id.in_([r.id for r in rides])`, and add a `from_attributes` config on the schemas to avoid hand copying. (Opinion.)
- Security: filters by `passenger.id` so one passenger cannot see another's data. Good.

## 7. Check yourself
1. Why does `or 0` appear on line 29?
2. What does `.limit(3)` do and where would you change "last 3 rides" to "last 5"?
