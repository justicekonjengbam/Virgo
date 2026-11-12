# rideMatchingService.ts

## 1. Purpose
The driver app's HTTP calls for rides: get the current offer, accept or decline, get the active ride, send GPS location, change ride state, cancel, get the fare summary, rate, and list outstation trips. It also defines the data types for these calls. It uses `apiClient` and is used by the ride screens and the location hook.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (line 1). Project file `driver-app/src/services/apiClient`. A configured axios (HTTP library) object that sends requests to the backend. *Example:* `apiClient.get('/x')`.
- `import type { GeolocationPosition } from '@maplibre/maplibre-react-native';` (line 2). MapLibre is the map library. This is a type only: the shape of a GPS reading (`coords.latitude`, `coords.longitude`, `timestamp`...). Used by `updateLocation`.

## 3. Walk through the code

**Types** (lines 4-8). A **type** only describes data shape.
- `DriverRideOffer` (4): an offer with ids, addresses, distance, fare in paise, minutes away, expiry, coordinates.
- `RideOfferResponse` (5): the answer after accept or decline.
- `DriverActiveRide` (6): ride in progress; `route_geojson: GeoJSON.Geometry | null` is the route line in GeoJSON (a standard JSON format for map shapes); `can_cancel`, `can_end` say what the driver may do.
- `RideSummary` (7): distance, duration, total `fare_paise` and `fare_items` (label and amount), and rating flags.
- `DriverOutstationAssignment` (8): a scheduled long trip; `status` is only `'driver_assigned'` or `'completed'`.
**Paise** are 1/100 of a rupee. 12550 paise = Rs 125.50. Money as whole numbers avoids rounding errors.

**`rideMatchingService`** (line 10): an object of arrow functions. `async () => (await call).data` waits for the HTTP answer and returns only its JSON body.
- `getCurrentOffer` (11): GET `/api/v1/drivers/me/ride-offers/current`; returns an offer or `null`.
- `respond(offerId, decision)` (12): POST `.../ride-offers/{offerId}/response` with `{ decision }` (`'accepted'` or `'declined'`). Template string `` `...${offerId}...` `` inserts the value.
- `activeRide` (13): GET `/api/v1/drivers/me/rides/active`.
- `updateLocation(position)` (14): PUT `/api/v1/drivers/me/location` (PUT = replace/save the latest value) with latitude, longitude, heading (rounded; `null` if unknown, `== null` catches null and undefined), accuracy, speed, and `recorded_at` as an ISO time string (`new Date(ts).toISOString()` gives e.g. `2026-10-26T08:00:00.000Z`). It returns the raw axios response.
- `action(rideId, action, startOtp?)` (15): POST `.../rides/{id}/actions` with `{ action, start_otp }` (`arrived`, `start`, `complete`). `startOtp?` is optional.
- `cancel(rideId, reason)` (16): POST `.../cancel` with `{ reason, confirm: true }`.
- `summary(rideId)` (17): GET the fare summary.
- `rate(rideId, score, comment?)` (18): POST a rating.
- `outstationAssignments` (19): GET the outstation list.

Errors: axios throws on 4xx, 5xx or no network; callers handle it.

## 4. How data flows
```
Screen -> rideMatchingService.respond(5,'accepted') -> apiClient POST -> backend
Screen <- {ride_id, ride_status, message} <- response.data <- backend
```

## 5. Try it
Not directly runnable alone (needs login). Test with curl, `-H` adds a header, `-X POST` sets the method, `-d` sets the body:
`curl -X POST -H "Authorization: Bearer <secret>" -H "Content-Type: application/json" -d '{"decision":"accepted"}' http://localhost:8000/api/v1/drivers/me/ride-offers/5/response`

## 6. Can it be better?
- Good: all ride URLs in one place; typed returns for most calls.
- Weak: `action`, `cancel`, `rate` have no return types (they return `any`); types are hand-written and may drift from the backend; very long one-line functions; `cancel` always sends `confirm: true`, so the confirmation is only in the UI.
- Cleaner way: add result types, e.g. `post<RideActionResponse>(...)`, and generate types from OpenAPI.
- Security: the OTP is sent in the body, fine over HTTPS only.

## 7. Check yourself
1. Why are fares stored in paise?
2. What does `getCurrentOffer` return when there is no offer?
