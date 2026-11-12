# backend/app/schemas/driver_dashboard.py

## 1. Purpose
This file holds the message shapes for the driver's home screen: the online switch, the vehicle card and the dashboard numbers (earnings, rides, rating). The driver routes use them and the driver app shows the data. It only calls `pydantic`.

## 2. Imports, one by one
- `from pydantic import BaseModel, Field` (`driver_dashboard.py:1`). **Pydantic** checks data against type hints. `BaseModel` is the base class. `Field(ge=0)` means "at least 0". *Example:* `online_minutes=-5` is rejected.

## 3. Walk through the code, top to bottom
- `DriverAvailabilityRequest` (4-5). One field, `is_online: bool`. The driver app sends `{"is_online": true}` to go online. It is also a good example of a minimal schema.
- `DriverVehicleStatusResponse` (8-15). `category`, `make`, `model`, `registration_number`, `seat_count`, optional `color`, `verification_status`. Optional fields without `= None` must still be passed by the code (as `None`).
- `DriverDashboardResponse` (18-28).
  - `full_name`, `is_online`.
  - `online_minutes: int = Field(ge=0)`: cannot be negative.
  - `safety_score`: optional, 0-100.
  - `rating`: optional float, 1-5 (a new driver has none, so `None`).
  - `today_earnings_paise`, `month_earnings_paise`: money in paise (1/100 rupee), at least 0.
  - `today_completed_rides`, `month_completed_rides`: at least 0.
  - `vehicle`: optional nested `DriverVehicleStatusResponse`, default `None`.
Response models also check data on the way out. If the service builds `rating=0.0`, the response fails because `ge=1`. That would be an error 500, not a 422.

## 4. How data flows
```
driver-app --GET /driver/dashboard--> route -> service reads rides/payments
  -> DriverDashboardResponse(full_name='Ravi', online_minutes=95, ..., vehicle=...)
  -> JSON -> driver-app shows cards
```

## 5. Try it
```zsh
cd backend
uv run python -c "
from app.schemas.driver_dashboard import DriverDashboardResponse as D
print(D(full_name='Ravi', is_online=True, online_minutes=95, today_earnings_paise=45000, month_earnings_paise=900000, today_completed_rides=4, month_completed_rides=80))"
```
Expected: one line with all fields, `rating=None`, `vehicle=None`.

## 6. Can it be better?
- Good: tiny, clear, with sane limits on the numbers.
- Weak: `rating` must be at least 1, so a driver whose average is `0.00` (the model default in `Driver.rating_average`) would crash the response if the service passes `0.0` instead of `None`. Check the service. `online_minutes` has no upper limit. `category` is free text.
- Cleaner way: allow `ge=0, le=5` for rating, or make the service always map 0 to `None`.
- Security: it exposes only the driver's own data; the route must use the logged-in driver's id.

## 7. Check yourself
1. Which fields of `DriverDashboardResponse` may be `None`?
2. What could go wrong when a new driver's `rating_average` is `0.00`?
