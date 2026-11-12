# driverMapService.ts

## 1. Purpose
Fetches the map settings from the backend once and remembers them. `DriverRideMap.tsx` calls it. It calls `apiClient` for `/api/v1/maps/config`. The backend keeps the map provider key secret and gives the app only a style URL.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (`driver-app/src/features/maps/services/driverMapService.ts:1`): shared HTTP client (*example:* `apiClient.get('/x')`).

## 3. Walk through the code
- **`MapConfiguration`** (line 3): `style_url` (address of the map style JSON), `attribution` (credit text), `service_area` and `service_center` (number lists, probably bounding box and centre coordinates; I am not sure of the order, check the backend maps route), `service_radius_km`.
- `let cachedConfig` (line 4): a module-level variable. It lives as long as the app runs. Starts `null`.
- **`getMapConfiguration()`** (line 6): if the cache is empty, it GETs the config and stores `.data` (line 7). Then returns the cache (line 8). First call hits the network; later calls return instantly. *Example:* call twice, one request.
- Errors: the Axios error is thrown on the first call and nothing is cached, so the next call retries.

## 4. How data flows
```
DriverRideMap -> getMapConfiguration() -> (cache empty) -> GET /api/v1/maps/config -> cache -> style_url
```

## 5. Try it
Not directly runnable. `curl http://localhost:8000/api/v1/maps/config` (add a token header if the route needs login) should return the JSON.

## 6. Can it be better?
- Good: tiny cache, avoids repeat requests.
- Weak: two simultaneous first calls make two requests. The cache never expires and is not cleared on logout.
- Cleaner way: cache the promise instead of the value: `cached ??= apiClient.get(...).then(r => r.data)` (and reset it on error).
- Security: the style URL may contain a key (I did not check). Treat it as visible to the app user.

## 7. Check yourself
1. How many network requests do three calls make?
2. Why does a failed call not poison the cache?
