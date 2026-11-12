# backend/app/schemas/driver_menu.py

## 1. Purpose
This file holds three **schemas** (a schema is a class that describes the shape of data sent in an API answer. *Example:* "a trip has an id, a pickup address and a fare"). They describe what the driver app's menu screens receive: a ride request card, a trip history row, and a support article. Route files (in `backend/app/api/`) and services return these shapes, and FastAPI turns them into JSON. This file calls nothing in the project.

## 2. Imports, one by one
Standard library:
- `from datetime import datetime` (`driver_menu.py:1`). `datetime` is Python's type for a date plus a time. *Example:* `datetime(2026, 10, 26, 9, 30)`. Used for `completed_at`. It can also do math like `now - timedelta(hours=1)`.

Third party:
- `from pydantic import BaseModel, Field` (`driver_menu.py:3`). **Pydantic** is a library that checks data against a class definition. *Example:* `Item(price="5")` becomes `price=5` if the field is `int`, and `Item(price="abc")` raises an error. `BaseModel` is the parent class that gives a class this checking power. `Field` adds extra rules to one field, such as "must be 0 or more". Pydantic can also read data from database objects and convert models to JSON.

## 3. Walk through the code, top to bottom

### `DriverRideRequestResponse` (`driver_menu.py:6-11`)
Describes one incoming ride request shown to a driver.
- `pickup_address: str` and `destination_address: str`: text. *Example:* `"MG Road, Pune"`.
- `estimated_distance_km: float = Field(ge=0)`: a decimal number. `ge=0` means "greater than or equal to 0". A value of `-1` raises a validation error.
- `expected_fare_paise: int = Field(ge=0)`: a whole number. **Paise** are 1/100 of a rupee, so `15000` means Rs 150. Money is stored as integers to avoid decimal rounding bugs.
- `pickup_minutes_away: int = Field(ge=0)`: how many minutes until the driver reaches the passenger.

Tiny example: `DriverRideRequestResponse(pickup_address="A", destination_address="B", estimated_distance_km=4.2, expected_fare_paise=9000, pickup_minutes_away=3)` works. With `pickup_minutes_away=-2` it raises `ValidationError`.

### `DriverTripHistoryItemResponse` (`driver_menu.py:14-20`)
One row in the driver's past trips list.
- `id: int`: the ride's database id.
- `category: str`: the ride category code, for example `"sedan"`.
- `completed_at: datetime | None`: the time the trip ended. `| None` means the value may also be missing (null in JSON). Note there is no `= None` default, so the field must still be given, but it may be `None`. This is how Pydantic v2 treats it (I am fairly sure; check the Pydantic docs on "required but nullable").
- `fare_paise: int`: the fare in paise.

### `DriverSupportArticleResponse` (`driver_menu.py:23-26`)
A help article. `id` is a `str` (a slug like `"payments"`, not a database number), plus `title` and `body` text.

## 4. How data flows
```
Driver app  --GET /driver/trips-->  route function
route function --asks--> service/repository --> database rows
route function builds DriverTripHistoryItemResponse(...)  <- Pydantic checks types here
FastAPI converts it to JSON  -->  Driver app
```

## 5. Try it
Run from `backend/`:
```
uv run python -c "from app.schemas.driver_menu import DriverRideRequestResponse as R; print(R(pickup_address='A', destination_address='B', estimated_distance_km=-1, expected_fare_paise=1, pickup_minutes_away=1))"
```
- `uv run python -c "..."` runs one line of Python inside the project's environment.
- Expected: a `ValidationError` saying `estimated_distance_km` must be greater than or equal to 0. Change `-1` to `1` to see it print the object.

## 6. Can it be better?
- Good: small, clear, money in integers, non-negative checks on numbers.
- Weak: `category` and ids are plain `str`; `completed_at` and `fare_paise` have no checks. Support article text is probably hard-coded elsewhere (not verified here).
- Cleaner way: give `completed_at: datetime | None = None` so it is optional to create. Use `Literal` for category if the set is fixed.
- Security: none here. These are output shapes only.

## 7. Check yourself
1. What does `Field(ge=0)` do, and what happens with `-5`?
2. Why is the fare stored as `int` paise and not a `float` in rupees?
