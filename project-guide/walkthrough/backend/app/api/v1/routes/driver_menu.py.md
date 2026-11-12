# backend/app/api/v1/routes/driver_menu.py

## 1. Purpose
Routes for the driver app's menu pages: a ride request screen, trip history and support articles. Mounted at `router.py:23`. Calls `DriverMenuService` (`app/services/driver_menu_service.py`). URLs start with `/api/v1/drivers/menu`.

## 2. Imports, one by one
- `from fastapi import APIRouter, Depends` (`driver_menu.py:1`): router and dependency injection.
- `from sqlalchemy.orm import Session` (`:2`): session type.
- `get_current_driver` (`:4`), `get_db` (`:5`), `Driver` (`:6`): same as the other driver routes.
- `DriverRideRequestResponse, DriverSupportArticleResponse, DriverTripHistoryItemResponse` from `app/schemas/driver_menu.py` (`:7`): response shapes.
- `DriverMenuService` (`:8`).

## 3. Walk through the code, top to bottom
- `router` prefix `/drivers/menu` (`:10`), `service` (`:11`).
- **`get_ride_request`** `GET /ride-request` (`:14-16`). Uses `_: Driver = Depends(get_current_driver)`: the driver must be logged in but the value is not used. `service.current_ride_request()` takes no arguments, so it likely returns fixed or demo data (I am not sure; read the service).
- **`get_trip_history`** `GET /trip-history` (`:19-21`). `service.trip_history(db, driver.id)` returns a list of past trips for this driver.
- **`get_support`** `GET /support` (`:24-26`). `service.support()` returns help articles, same for every driver.

## 4. How data flows
```
driver-app --GET /drivers/menu/trip-history--> get_current_driver -> Driver
   -> service.trip_history(db, driver.id) --SELECT--> database
   <- list[DriverTripHistoryItemResponse]
```

## 5. Try it
`curl -s -H "Authorization: Bearer <secret>" localhost:8000/api/v1/drivers/menu/support` (`-s` quiet, `-H` header). Expect a JSON list of articles.

## 6. Can it be better?
- Good: small; no logic in routes.
- Weak: `/ride-request` may overlap with the real offer route `/drivers/me/ride-offers/current` in `driver_matching.py:22` (possible duplicate or leftover; check). Trip history has no paging, so a long history returns everything.
- Cleaner way: add `limit` and `offset` query params to `trip_history`.
- Security: all routes are login-only.

## 7. Check yourself
1. Why is the parameter named `_` in `get_support`?
2. Which route reads the database and which do not seem to?
