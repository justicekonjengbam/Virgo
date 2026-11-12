# driverDashboardService.ts

## 1. Purpose
This file holds the two web requests for the driver dashboard and the TypeScript shapes of the data. `useDriverDashboard.ts` calls it. It calls `driver-app/src/services/apiClient`. The backend routes live under `/api/v1/drivers/dashboard`.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (`driver-app/src/features/dashboard/services/driverDashboardService.ts:1`): a project file. `apiClient` is most likely an **Axios** instance (an HTTP client library. *Example:* `apiClient.get('/x')` sends a GET request). It is probably set up with the base URL and the login token. I did not read that file; check `driver-app/src/services/apiClient.ts`.

## 3. Walk through the code
- **`DriverVehicleStatus`** (lines 3-11): a **type** (a description of an object's fields; it is checked at build time only). Fields: category, make, model, registration number, seat count, `color` (text or `null`), and `verification_status` which can only be one of four words. *Example:* `{ category:'auto', make:'Bajaj', ..., verification_status:'verified' }`.
- **`DriverDashboard`** (lines 13-24): name, online flag, minutes online, `safety_score` and `rating` (may be `null` for new drivers), earnings in **paise** (1/100 of a rupee; 25000 means Rs 250), completed ride counts, and `vehicle` (or `null`). Field names use snake_case because the Python backend sends them that way.
- **`getDashboard()`** (line 27): `apiClient.get<DriverDashboard>(url)` sends GET and the `<DriverDashboard>` tells TypeScript the answer type. `response.data` is the JSON body. Returns a `Promise` (a value that arrives later).
- **`updateAvailability(isOnline)`** (line 32): `apiClient.put(url, { is_online: isOnline })` sends PUT with a JSON body, e.g. `{"is_online":true}`. Returns the updated dashboard.
- Errors: Axios throws on network failure or 4xx/5xx. This file does not catch them.

## 4. How data flows
```
hook -> getDashboard() -> apiClient GET /api/v1/drivers/dashboard -> backend -> JSON -> response.data -> hook
```

## 5. Try it
Not directly runnable. With the backend running and a driver token:
```
curl -H "Authorization: Bearer <secret>" http://localhost:8000/api/v1/drivers/dashboard
```
`curl` sends a request; `-H` adds a header. Expected: JSON with the fields above.

## 6. Can it be better?
- Good: small, typed, one place for the URLs.
- Weak: the types are written by hand and can drift from the backend. No runtime check of the response.
- Cleaner way: generate the types from the backend OpenAPI file (FastAPI makes one at `/openapi.json`), or validate with Zod.
- Security: the token is handled in `apiClient`, not here.

## 7. Check yourself
1. Why can `rating` be `null`?
2. What does `getDashboard()` return when the server is down?
