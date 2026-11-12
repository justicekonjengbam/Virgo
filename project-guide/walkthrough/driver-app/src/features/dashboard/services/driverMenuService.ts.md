# driverMenuService.ts

## 1. Purpose
Three read-only requests used by the driver menu pages: ride request preview, trip history, and help articles. Callers are the menu screens (for example the request, history and help screens in the driver app; I did not check which exact files). It calls `apiClient`.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (`driver-app/src/features/dashboard/services/driverMenuService.ts:1`): the shared HTTP client (Axios-style; *example:* `apiClient.get('/x')`). It sends the request to the backend.

## 3. Walk through the code
- **Types** (lines 3-5)
  - `DriverRideRequest`: pickup and destination text, distance in km, expected fare in paise, minutes away.
  - `DriverTrip`: id, addresses, category, `completed_at` (date text or `null`), fare in paise.
  - `DriverSupportArticle`: id, title, body.
- **`driverMenuService`** (line 7): an object with three **async** functions (functions that wait for the network using `await`).
  - `getRideRequest()` (line 8): GET `/api/v1/drivers/menu/ride-request`, returns `.data`. The extra parentheses `(await ...).data` first wait, then read `.data`.
  - `getTripHistory()` (line 9): GET `/api/v1/drivers/menu/trip-history`, returns a list.
  - `getSupport()` (line 10): GET `/api/v1/drivers/menu/support`, returns a list of articles.
- Errors: Axios throws on failure; callers must catch.

## 4. How data flows
```
menu screen -> driverMenuService.getTripHistory() -> apiClient GET -> backend -> DriverTrip[] -> screen list
```

## 5. Try it
Not directly runnable. Use `curl -H "Authorization: Bearer <secret>" http://localhost:8000/api/v1/drivers/menu/trip-history` and expect a JSON list.

## 6. Can it be better?
- Good: tiny and typed.
- Weak: one-line functions are dense. `getRideRequest` may overlap with the newer realtime offer flow (`rideMatchingService.getCurrentOffer`, used in `DriverHomeScreen.tsx:54`); I am not sure it is still used, check with `rg getRideRequest driver-app/src`.
- Cleaner way: remove it if unused.
- Security: none here.

## 7. Check yourself
1. Which unit is `fare_paise` in?
2. Why does `getSupport` return an array type?
