# backend/app/api/v1/routes/driver_dashboard.py

## 1. Purpose
Two routes for the driver home screen: read the dashboard, and go online or offline. Used by `driver-app/`. Mounted at `router.py:21`. Calls `DriverDashboardService` (`app/services/driver_dashboard_service.py`). URLs start with `/api/v1/drivers/dashboard`.

## 2. Imports, one by one
- `from fastapi import APIRouter, Depends` (`driver_dashboard.py:1`): `APIRouter` groups routes; `Depends` is dependency injection (FastAPI runs a helper and gives you the result).
- `from sqlalchemy.orm import Session` (`:2`): database session type (hint only).
- `get_current_driver` from `app/api/dependencies/driver_auth.py` (`:4`): reads the bearer token, returns the `Driver` row, or 401.
- `get_db` from `app/db` (`:5`): opens and closes a session per request.
- `Driver` from `app/models/ride_hailing.py` (`:6`): table class, used as a hint.
- `DriverAvailabilityRequest, DriverDashboardResponse` from `app/schemas/driver_dashboard.py` (`:7`): JSON shapes. The request has a boolean `is_online`.
- `DriverDashboardService` (`:8`): the logic.

## 3. Walk through the code, top to bottom
- `router = APIRouter(prefix="/drivers/dashboard", tags=["driver-dashboard"])` (`:10`), `service = DriverDashboardService()` (`:11`).
- **`get_dashboard`** `GET /drivers/dashboard` (`:14-16`). The path is `""` (empty), so the URL is exactly the prefix. `service.dashboard(db, driver)` builds earnings/status data for this driver. Returns `DriverDashboardResponse`.
- **`update_availability`** `PUT /drivers/dashboard/availability` (`:19-25`). Body `{"is_online": true}`. `service.set_availability(db, driver, request.is_online)` saves the flag and returns the fresh dashboard. PUT means "replace this state". Errors come from the service (for example a driver who is not yet approved; unverified).

## 4. How data flows
```
driver-app --PUT .../availability {"is_online":true}--> get_current_driver -> Driver
   -> DriverDashboardService.set_availability -> UPDATE driver --> database
   <- DriverDashboardResponse
```

## 5. Try it
`curl -s -X PUT -H "Authorization: Bearer <secret>" -H 'content-type: application/json' -d '{"is_online":true}' localhost:8000/api/v1/drivers/dashboard/availability` (`-X` method, `-H` header, `-d` body). Expect a dashboard JSON.

## 6. Can it be better?
- Good: tiny and clear.
- Weak: this file uses double quotes and multi-line signatures while others use single quotes and one long line. Style is not consistent across route files (minor; a formatter like `ruff format` would fix it).
- Security: login-only; the data is tied to the token's driver, so no id can be spoofed.

## 7. Check yourself
1. Why is the path of `get_dashboard` an empty string?
2. Where does the `driver` value come from?
