# backend/app/services/map_provider_service.py

## 1. Purpose
Talks to **Geoapify** (a paid/free web service for maps, address search and routes) over HTTP. It also checks that a point is within 150 km of the service centre (Dharwad-Hubballi). Called by booking and outstation code (`outstation_service.py:29` calls `route`) and by map routes. Schemas come from `backend/app/schemas/maps.py`.

## 2. Imports, one by one
Standard library:
- `from math import asin, cos, radians, sin, sqrt` (line 1). Maths functions for the **haversine formula** (distance between two points on a sphere). *Example:* `radians(180)` gives 3.14159.
- `from urllib.parse import quote` (line 2). Makes text safe inside a URL. *Example:* `quote('a b')` gives `a%20b`.
Third-party:
- `import httpx` (line 4). An HTTP client library. *Example:* `httpx.get('https://example.com').json()`. Used to call Geoapify.
- `from fastapi import HTTPException, status` (line 5). Errors that become HTTP replies.
Project:
- `from app.core.config import get_settings` (line 7). Reads settings from the environment (`backend/app/core/config.py`). Used for the API key and contact email.
- `from app.schemas.maps import GeocodedPlaceResponse, MapConfigResponse, RouteResponse` (line 8). Output shapes.

## 3. Walk through the code
### Class constants (lines 12-16)
Centre `15.3926, 75.0833`, radius `150.0` km, `bounds` as `[west, south, east, north]`, and `api_base`. **Geocoding** means turning text into coordinates; **reverse geocoding** means coordinates into an address.

### `config()` (18-26)
Gets the key with `_key()` and returns the map style URL, attribution text, area bounds, centre as `[lon, lat]` and radius. `quote(key)` protects the URL. Warning: the key goes to the app inside the URL (normal for map tiles, but then the key is public; restrict it in the Geoapify dashboard).

### `search(query, outstation=False)` (28-43)
Builds `params` (lines 29-37): text, JSON format, English, max 8 results. `filter` is `countrycode:in` for outstation (anywhere in India) or a circle around the centre plus India. `bias` ranks nearer places first. Then `_get('/geocode/autocomplete', params)` calls the API. The list comprehension on line 39 keeps results that have `lat` and `lon` and, if not outstation, pass `contains`. Lines 40-43 remove duplicates by `place_id`: `dict.setdefault(key, value)` only stores the first value for a key. Returns a list.
Example: `search('Hubb')` returns places such as "Hubballi Junction".

### `reverse(lat, lon, outstation=False)` (45-57)
Checks the service area unless outstation. Calls `/geocode/reverse`. Errors: 404 if no address (line 54), 422 if outstation but country is not India (line 56). Returns one place.

### `ensure_in_service_area` (59-61): raises 422 if outside the radius.

### `contains` (63-67): the haversine formula. `map(radians, (...))` converts four degree numbers to radians. `value` is the haversine term. `6371.0 * 2 * asin(sqrt(value))` is the distance in km (6371 is Earth's radius). Returns `True` if within the radius. Example: the centre itself returns `True`.

### `route(origin, destination)` (69-85)
Origin and destination are `(lat, lon)` tuples. Calls `/routing` with `waypoints`. Note: Geoapify routing expects `lat,lon` order here, and this code sends `origin[0],origin[1]` (lat, lon), which matches. Raises 422 if no features. Returns distance in metres (rounded), duration in seconds (at least 1), the GeoJSON line (`geometry`), and `toll_fare_paise=0` (tolls are not calculated).

### `_get(path, params)` (87-99)
`httpx.get(url, params=..., timeout=8.0, headers=...)` sends a GET. `timeout=8.0` waits up to 8 seconds. The User-Agent header names the app and the contact email. `raise_for_status()` raises on 4xx/5xx. `.json()` parses the body. Any `httpx.HTTPError` or `ValueError` becomes a 503 (line 96). `from exc` keeps the original error in the traceback.

### `_place(item)` (101-109, staticmethod)
Picks the best address and name from the API item with `or` fallbacks. If there is no `place_id`, makes `geoapify:lat:lon`. Returns a `GeocodedPlaceResponse`.

### `_key()` (111-119, staticmethod)
Returns the API key from settings or raises 503 if it is empty. The key value is `<secret>`.

## 4. How data flows
```
App -> /maps/search?q=Hubb -> MapProviderService.search
   -> httpx.get https://api.geoapify.com/v1/geocode/autocomplete
   <- JSON results -> filter by distance -> unique list -> App
```

## 5. Try it
```
cd backend && uv run python -c "from app.services.map_provider_service import MapProviderService as M; print(M().contains(15.3926,75.0833), M().contains(28.6,77.2))"
```
`uv run python -c` runs one line of Python inside the project. Expected: `True False`. (It may need settings to load; `contains` itself does not call the network.) The API calls need `GEOAPIFY_API_KEY` set.

## 6. Can it be better?
- Good: clean errors, timeouts, deduplication, a clear 503 when the key is missing.
- Weak: `httpx.get` is blocking and a new connection every time (use a shared `httpx.Client`). The centre `75.0833,15.3926` is repeated as a string in `bias` (line 35); use the constants. Tolls are always 0. `contains` is duplicated in `ride_matching_service._distance_km` (haversine twice). No caching and no retries.
- Security: the key is sent in URL query strings; those can appear in logs. The user query is passed through unchanged (safe, httpx encodes it).

## 7. Check yourself
1. What happens if the Geoapify service is down?
2. Where else in the backend is the haversine formula written?
