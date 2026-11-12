# backend/app/api/v1/routes/maps.py

## 1. Purpose
This file gives three map URLs to the passenger app: map settings, place search, and reverse lookup (coordinates to an address). It validates the query values and passes them to `MapProviderService` (`backend/app/services/map_provider_service.py`).

## 2. Imports, one by one
**Third-party**
- `from fastapi import APIRouter, Depends, Query` (`maps.py:1`). `APIRouter` groups routes. `Depends` injects helpers. **Query** declares and checks a URL query value (the part after `?`). *Example:* `q: str = Query(min_length=2)` rejects `?q=a` with a 422 error.

**Project**
- `get_current_passenger` from `app/api/dependencies/auth.py` (`maps.py:3`). Requires a logged-in passenger.
- `Passenger` from `app/models/user.py` (`maps.py:4`). Type hint.
- `GeocodedPlaceResponse, MapConfigResponse` from `app/schemas/maps.py` (`maps.py:5`). **Geocoding** means turning text like "Airport" into latitude and longitude. These classes describe the JSON answers.
- `MapProviderService` from `app/services/map_provider_service.py` (`maps.py:6`). Does the real lookup.

## 3. Walk through the code, top to bottom
- `router = APIRouter(prefix='/maps', tags=['maps'])` (`maps.py:8`) and `service = MapProviderService()` (`maps.py:9`).
- `GET /maps/config` -> `map_config()` (`maps.py:12-14`). No login needed (no auth dependency). It returns `service.config()`, the map settings for the app. Output: `MapConfigResponse`.
- `GET /maps/places` -> `search_places` (`maps.py:17-23`):
  - `q: str = Query(min_length=2, max_length=120)` is the search text, 2 to 120 characters. No default, so it is required.
  - `scope: str = Query(default='local', pattern='^(local|outstation)$')`. A **regex pattern** (a text rule). `^` start, `$` end, `(local|outstation)` means exactly one of those two words. Anything else gives 422.
  - `_: Passenger = Depends(get_current_passenger)`. The name `_` means "I need the check but not the value". It forces login.
  - `service.search(q.strip(), outstation=scope == 'outstation')`. `strip()` removes spaces at both ends. `scope == 'outstation'` is a True/False value. The service returns a list of places.
- `GET /maps/reverse` -> `reverse_geocode` (`maps.py:26-33`): `latitude` must be between -90 and 90 (`ge` = greater or equal, `le` = less or equal). `longitude` between -180 and 180. Then `service.reverse(latitude, longitude, outstation=...)` returns one place.

Example: `GET /maps/places?q=airport&scope=local` returns `[{"name":"...","latitude":...}]`.
Errors: 401 if not logged in (places, reverse). 422 if a value breaks a rule.

## 4. How data flows
```
App --GET /maps/places?q=air--> FastAPI
  validate q, scope  -> get_current_passenger -> Passenger ok
  search_places -> MapProviderService.search("air", outstation=False)
App <-- list of places (JSON)
```

## 5. Try it
```zsh
curl -s -H "Authorization: Bearer <token>" "http://127.0.0.1:8000/maps/places?q=air&scope=local"
```
Quote the URL because zsh treats `?` and `&` specially. Expected: a JSON list. With `q=a` expect a 422 message about minimum length.

## 6. Can it be better?
- Good: input rules sit right in the signature, so bad input never reaches the service.
- Weak: `scope` is a string with a regex. `/config` has no login (maybe on purpose). Same global `service` pattern as other routes.
- Cleaner way: use a Python `Enum` or `Literal['local','outstation']` for `scope`; docs then show the choices. (Opinion.)
  ```python
  scope: Literal['local', 'outstation'] = 'local'
  ```
- Security: place search needs login, which limits abuse of any paid map API. Good.

## 7. Check yourself
1. What happens if the app sends `scope=abroad`?
2. Why is the parameter called `_` in `search_places`?
