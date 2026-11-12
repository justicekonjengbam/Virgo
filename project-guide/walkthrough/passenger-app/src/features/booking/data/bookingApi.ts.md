# bookingApi.ts

File: `passenger-app/src/features/booking/data/bookingApi.ts` (22 lines)

## 1. Purpose
This file lists every backend call the passenger booking flow makes, and the TypeScript shapes of the data. Screens such as `FareEstimateScreen.tsx`, `BookingStatusScreen.tsx` and `LocationSelectionScreen.tsx` use its types and `bookingApi` object. It calls the backend only through `apiClient`.

## 2. Imports, one by one
```ts
import { apiClient } from '../../../services/apiClient';
```
`apiClient` is an **axios** instance (an HTTP client library. *Example:* `apiClient.get('/x')` returns `{ data, status }`). It lives in `passenger-app/src/services/apiClient.ts:43`. It adds the base URL, the `Authorization: Bearer <token>` header (lines 48-59), and turns failures into `ApiError`. It can also `put`, `patch`, `delete`.

## 3. Walk through the code, top to bottom

### Types (3-7)
A **type** describes the shape of an object. TypeScript checks it while you code; it vanishes at run time.
- `LocationOption` (3): a place: optional `id`, optional `place_id` (map provider id), `name`, `formatted_address`, `latitude`, `longitude`. `number | null` means a number or null; `?` means may be missing.
- `FareEstimate` (4): price estimate: both places, `category_name`, `distance_km`, `duration_minutes`, `fare_paise` and `fare_items`. **Paise** are 1/100 of a rupee, kept as integers to avoid decimal errors. `route_geojson` is a **GeoJSON** line (a standard format for map shapes) for drawing the route. `GeoJSON.Geometry` is a global type, presumably from `@types/geojson` (I am not sure; check with `rg geojson passenger-app/package.json`).
- `RideBooking` (5): reply after booking: `ride_id`, `status`, addresses, fare, `requested_at`, `message`.
- `RideStatus` (6): live ride data: status, driver and vehicle info, coordinates, `can_cancel`, `can_end`, `ride_start_otp` (code the driver needs to start the trip) and `cancellation_reason`.
- `RideSummary` (7): receipt after the trip with rating flags.

### `placePayload` (9)
Turns a `LocationOption` into the body the backend wants. `place.place_id ?? \`catalog:${place.id}\`` uses `place_id`, and if it is `null` or `undefined` uses `catalog:<id>` (`??` is the "if empty" operator). Example: `{id:5,...}` gives `place_id: 'catalog:5'`.

### `ridePayload` (10)
Builds `{ pickup, destination, category_id }`. `category_id` is the vehicle type chosen.

### `bookingApi` (12-22)
Each entry is an `async` arrow function. `(await apiClient.get<T>(url)).data` waits for the HTTP reply, then takes the body. `<T>` tells TypeScript what type the body has.
| Method | HTTP | URL (line) | Purpose |
|---|---|---|---|
| `locations()` | GET | `/api/v1/passengers/me/locations` (13) | saved and catalog places |
| `estimate(p,d,cat)` | POST | `.../ride-estimates` (14) | price before booking |
| `book(p,d,cat)` | POST | `.../rides` (15) | request a driver |
| `status(id)` | GET | `.../rides/{id}/status` (16) | current ride state |
| `activeRide()` | GET | `.../rides/active/current` (17) | ongoing ride or `null` |
| `cancel(id, reason)` | POST | `.../cancel` (18) | cancel; sends `confirm: true` |
| `summary(id)` | GET | `.../summary` (19) | receipt |
| `rate(id, score, comment?)` | POST | `.../rating` (20) | rate the trip |
| `updateSavedPlace(id, loc)` | PATCH | `.../saved-places/{id}` (21) | change Home/Work place |

`me` in the path means "the logged-in passenger", taken from the token.
Errors: each call throws `ApiError` (via the interceptor in apiClient.ts) on network or HTTP failure.

## 4. How data flows
```
FareEstimateScreen --bookingApi.estimate(pickup,dest,3)--> ridePayload/placePayload
   --> apiClient.post --> Backend /ride-estimates --> JSON --> .data (FareEstimate) --> screen
```

## 5. Try it
Not directly runnable alone. A tiny check of the helper logic:
```zsh
node -e "const p={id:5,place_id:null};console.log(p.place_id ?? 'catalog:'+p.id)"
```
Expected output: `catalog:5`.

## 6. Can it be better?
- Good: all URLs in one file; typed replies; payload mapping kept in two small helpers.
- Weak: long one-line types and functions; `cancel` and `rate` return untyped `data`; the types are written by hand and can drift from the backend (the backend is FastAPI, so it could export an OpenAPI schema for generated types); `status` is a plain `string` instead of a union like `'driver_arriving' | 'completed'`; no tests.
- Cleaner way (opinion):
```ts
export type RideState = 'requested' | 'driver_arriving' | 'driver_arrived' | 'in_progress' | 'completed' | 'cancelled';
```
(The exact state names should be checked in the backend. I only saw some of them in BookingStatusScreen.tsx:29-30.)
- Security: `ride_start_otp` is sensitive for the ride, so never log `RideStatus`.

## 7. Check yourself
1. What does `placePayload` send when `place_id` is `null` and `id` is 9?
2. Why is `fare_paise` an integer, and how does the UI show rupees?
