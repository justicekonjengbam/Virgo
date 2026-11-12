# backend/app/api/v1/routes/outstation.py

## 1. Purpose
**Outstation** means a long trip to another city (not a short city ride). This file has all the URLs for these bookings, for three kinds of caller: the passenger, the admin, and the driver. All logic is in `OutstationService` (`backend/app/services/outstation_service.py`).

## 2. Imports, one by one
**Third-party**
- `from fastapi import APIRouter, Depends` (`outstation.py:1`). Router and dependency injection (FastAPI runs a helper function first and passes the result in).
- `from sqlalchemy.orm import Session` (`outstation.py:2`). Database session type.

**Project**
- `require_admin_permission` from `app/api/dependencies/admin_auth.py` (`:4`). A function that makes a dependency checking an admin has a named permission.
- `get_current_passenger` from `app/api/dependencies/auth.py` (`:5`); `get_current_driver` from `app/api/dependencies/driver_auth.py` (`:6`). Each reads the token and returns that kind of user.
- `get_db` from `app/db.py` (`:7`).
- `Driver` from `app/models/ride_hailing.py` (`:8`); `AdminUser, Passenger` from `app/models/user.py` (`:9`). Type hints.
- Schemas from `app/schemas/outstation.py` (`:10`): `OutstationBookingCreate` (input to book), `OutstationEstimateResponse` (price guess), `OutstationBookingResponse`, `OutstationCancellationRequest` (has `reason`), `AdminOutstationUpdate` (admin changes), `EligibleOutstationDriverResponse`, `DriverOutstationAssignmentResponse`.
- `OutstationService` from `app/services/outstation_service.py` (`:11`).

## 3. Walk through the code, top to bottom
`router = APIRouter(tags=['outstation'])` has no prefix, so each route writes its full path (`:13`). `service = OutstationService()` (`:14`).

Each function is a thin wrapper. A **request body** (JSON sent inside a POST/PATCH) is read by FastAPI into a schema object when the argument type is a schema class.

| Line | Route | Who | Calls | Note |
|---|---|---|---|---|
| `:17-19` | `POST /passengers/me/outstation-estimates` | passenger | `service.estimate(request)` | No database. Price only. |
| `:22-24` | `POST /passengers/me/outstation-bookings` | passenger | `service.create(db, passenger, request)` | `status_code=201` means "Created". |
| `:27-29` | `GET /passengers/me/outstation-bookings` | passenger | `service.passenger_list(db, passenger)` | My bookings. |
| `:32-34` | `POST /passengers/me/outstation-bookings/{booking_id}/cancel` | passenger | `service.cancel(db, passenger, booking_id, request.reason)` | `booking_id` comes from the URL. |
| `:37-39` | `GET /admin/outstation-bookings` | admin | `service.admin_list(db, status_filter)` | `status_filter: str \| None = None` is an optional query value, `?status_filter=pending`. |
| `:42-44` | `PATCH /admin/outstation-bookings/{booking_id}` | admin | `service.admin_update(db, booking_id, request, admin.id)` | Passes `admin.id` so the change can be recorded. |
| `:47-49` | `GET /admin/outstation-bookings/{booking_id}/eligible-drivers` | admin | `service.eligible_drivers(db, booking_id)` | Drivers who can take the trip. |
| `:52-54` | `GET /drivers/me/outstation-assignments` | driver | `service.driver_assignments(db, driver)` | Trips given to me. |

`Depends(require_admin_permission('outstation:manage'))` (`:38`, `:43`, `:48`): `require_admin_permission` is called once at import time with the text `'outstation:manage'`. It returns a new function. FastAPI calls that function per request. It returns the `AdminUser` or raises 401/403.

Errors: 401/403 from auth, 422 for bad input, and 404/409-style errors from the service (not visible here).

## 4. How data flows
```
Passenger app --POST /passengers/me/outstation-bookings {json}--> FastAPI
  validate body -> OutstationBookingCreate
  get_current_passenger -> Passenger ; get_db -> Session
  create_booking -> OutstationService.create(db, passenger, request)
Passenger app <-- 201 + OutstationBookingResponse
Admin web --PATCH /admin/outstation-bookings/7--> permission check 'outstation:manage' -> admin_update
Driver app --GET /drivers/me/outstation-assignments--> get_current_driver -> driver_assignments
```

## 5. Try it
```zsh
curl -s -H "Authorization: Bearer <token>" http://127.0.0.1:8000/passengers/me/outstation-bookings
```
Expected: `[]` for a new passenger. The booking body fields are in `app/schemas/outstation.py`; read it before you POST.

## 6. Can it be better?
- Good: three roles in one place for one feature; permissions are explicit; routes stay thin.
- Weak: very long lines (`:10`, `:23`, `:33`, `:43`). Mixed passenger, admin and driver paths in one file. `status_filter` is a free string. Global `service`.
- Cleaner way: wrap the long import in parentheses, one name per line. Use an `Enum` for `status_filter`. Split into `passenger`, `admin`, `driver` routers if it grows. (Opinion.)
- Security: admin routes need the `outstation:manage` permission. Passenger and driver routes rely on the service to check ownership of `booking_id`; check `outstation_service.py` for that.

## 7. Check yourself
1. What is the difference between `get_current_passenger` and `require_admin_permission('outstation:manage')`?
2. Why does `create_booking` return status 201 and not 200?
