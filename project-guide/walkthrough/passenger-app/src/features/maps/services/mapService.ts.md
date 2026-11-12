# mapService.ts

## 1. Purpose
Three backend calls for maps: get map configuration, search places, and turn a coordinate into an address (reverse geocode). It sits in `features/maps/services/`. `CabSureMap.tsx` calls `configuration()`. Search screens call `search` and `reverse`. It calls the shared `apiClient` in `src/services/apiClient`.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (line 1) The app's HTTP client (probably an axios instance; I am not sure, check `apiClient.ts`). *Example:* `apiClient.get('/x')` returns `{ data }`.
- `import type { LocationOption } from '../../booking/data/bookingApi';` (line 2) Type of a place: address, latitude, longitude, optional `place_id`.

## 3. Walk through the code, top to bottom
**`MapConfiguration`** (line 4): type of the config reply: `style_url`, `attribution`, `service_area`, `service_center`, `service_radius_km`.

**`cachedConfig`** (line 6): a module-level variable. It stores the config after the first load, so later calls skip the network. It lives until the app closes.

**`uniquePlaces`** (lines 8-17). Input: a list of places. Output: the list without duplicates.
- A **Set** is a collection with no repeats; `seen` remembers ids.
- `identity` is the `place_id`, or if missing, `lat:lng:address` with 6 decimals and lowercase address. `??` uses the right side only if the left is null or undefined.
- `.filter` keeps an item if the callback returns true. If `seen` already has the id, drop it (false). Else add and keep.
- *Example:* two results with the same `place_id` become one.

**`mapService`** (lines 19-31), an object with three async methods (async = returns a promise, a value that arrives later; `await` waits for it).
- `configuration()` (20-23): if not cached, GET `/api/v1/maps/config`, read `.data`, store it, return it.
- `search(query, scope='local')` (24-27): GET `/api/v1/maps/places` with query string `?q=...&scope=...` (`params` builds the query string). `scope` is `'local'` or `'outstation'`. Returns deduplicated places.
- `reverse(latitude, longitude, scope)` (28-30): GET `/api/v1/maps/reverse?latitude=..&longitude=..&scope=..`. Returns one place.
Errors: network or HTTP errors are thrown by `apiClient`; callers must catch them.

## 4. How data flows
```
Screen --search("airport")--> mapService.search --GET /api/v1/maps/places?q=airport&scope=local--> backend
   <-- [place, place, dup] -- uniquePlaces --> [place, place] --> Screen
```

## 5. Try it
Not directly runnable alone. In app code:
```ts
const places = await mapService.search('railway', 'outstation');
console.log(places.length);
```
Expected: a number of unique places. You can also test the backend with `curl 'http://localhost:8000/api/v1/maps/places?q=railway&scope=local'` (it may need a login token; I am not sure).

## 6. Can it be better?
- Good: small; caching; dedupe is sensible.
- Weak: config cache never expires and is never cleared on error or logout. Concurrent first calls fire two requests (cache the promise instead). `search` has no debounce here (callers must do it) and no cancel for old requests. No tests for `uniquePlaces`.
- Cleaner way: `let pending: Promise<MapConfiguration> | null = null;` and cache the promise.
- Security: query text goes to the backend as parameters, which are URL-encoded by the client. No secrets here.

## 7. Check yourself
1. What key does `uniquePlaces` use when `place_id` is missing?
2. Why can two quick calls to `configuration()` still make two requests?
