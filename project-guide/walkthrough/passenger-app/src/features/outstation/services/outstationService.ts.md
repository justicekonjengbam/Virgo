# outstationService.ts

## 1. Purpose
The API layer for outstation (long distance, over 150 km) bookings. It lists, estimates, creates and cancels requests. `OutstationBookingScreen.tsx` is its caller. It calls the backend through `apiClient`.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (line 1) HTTP client. *Example:* `apiClient.post('/x', {a:1})`.
- `import type { LocationOption } from '../../booking/data/bookingApi';` (line 2) Type of a place with address, latitude, longitude, `id`, optional `place_id`.

## 3. Walk through the code, top to bottom
**`OutstationBooking`** (line 4): a booking as the backend returns it: id, `scheduled_at`, addresses, vehicle preference, `status`, distance, `estimated_fare_paise` (paise = 1/100 rupee), support note, driver and vehicle details (null until assigned), `can_cancel`, `created_at`.

**`OutstationBookingInput`** (line 5): what the app sends: time, pickup, destination, preferred type `'sedan' | 'suv' | 'muv' | null`.

**`OutstationEstimate`** (line 6): `distance_km`, `duration_minutes`, `estimated_fare_paise`, `route_geojson` (a line shape), `disclaimer`.

**`payload`** (line 7). Input: an input object. Output: the same object but pickup and destination always have a `place_id`. If a place has none, it makes `catalog:<id>` (a place from the app's own catalog, not from the search service). `{ ...input.pickup, place_id: ... }` copies all fields then sets one. *Example:* pickup `{id: 5}` becomes `{id: 5, place_id: 'catalog:5'}`.

**`outstationService`** (lines 9-14), four async arrow functions. Each does `(await apiClient.xxx(...)).data` to return only the body.
- `list` (10): GET `/api/v1/passengers/me/outstation-bookings`.
- `create` (11): POST the same path with `payload(input)`.
- `estimate` (12): POST `/api/v1/passengers/me/outstation-estimates`.
- `cancel(id, reason)` (13): POST `.../outstation-bookings/${id}/cancel` with `{ reason }`. The backtick string inserts `id`.
Errors thrown by `apiClient` pass up to the caller.

## 4. How data flows
```
Screen -> estimate(input) -> payload() adds place_id -> POST /outstation-estimates -> backend
      <- {distance_km, fare, route_geojson} <-
Screen -> create(input) -> POST /outstation-bookings -> backend saves, support is notified
```

## 5. Try it
Not directly runnable alone. In app code: `const est = await outstationService.estimate(input); console.log(est.distance_km);`. Expected: a number of kilometres.

## 6. Can it be better?
- Good: thin and typed; the `place_id` helper keeps the backend happy.
- Weak: `place_id` is made from the `catalog:` prefix, a hidden rule shared with the backend (check the backend schema). Line 4 is one very long line. `GeoJSON.Geometry` needs a global type package. `preferred_vehicle_type` in the booking type is `string | null` but is a strict union in the input; keep them aligned. No tests.
- Security: the cancel reason is a plain string from the client; the backend must validate. No secrets.

## 7. Check yourself
1. What does `payload` change and why?
2. Which HTTP method does `cancel` use and what body does it send?
