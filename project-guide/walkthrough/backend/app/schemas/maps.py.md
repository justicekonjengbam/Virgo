# backend/app/schemas/maps.py

## 1. Purpose
This file defines the shapes for map data: the map configuration, a geocoded place, and a route. **Geocoding** means turning an address text into map coordinates. *Example:* "Pune Station" becomes `18.528, 73.874`. The maps routes and services build these objects and the apps use them to draw the map and the route line.

## 2. Imports, one by one
- `from pydantic import BaseModel` (`maps.py:1`). **Pydantic** checks data against a class. *Example:* a `float` field rejects `"abc"`. `BaseModel` is the parent class giving that behavior.

## 3. Walk through the code, top to bottom

### `MapConfigResponse` (`maps.py:4-9`)
Settings the app needs to show the map.
- `style_url: str`: web address of the map style (how the map looks).
- `attribution: str`: credit text the map provider requires on screen.
- `service_area: list[float]`: a list of numbers. It is probably a bounding box like `[west, south, east, north]` (I am not sure of the order; check the maps service that fills it).
- `service_center: list[float]`: the center point of the area where CabSure works.
- `service_radius_km: float`: radius of that area in kilometers.

### `GeocodedPlaceResponse` (`maps.py:12-17`)
`place_id`, `name`, `formatted_address`, `latitude`, `longitude`. One address result.

### `RouteResponse` (`maps.py:20-24`)
- `distance_meters: int`, `duration_seconds: int`: the trip size and time.
- `geometry: dict`: a dict (key-value object) holding the route line, likely **GeoJSON** (a standard JSON format for map shapes. *Example:* `{"type":"LineString","coordinates":[[73.8,18.5],[73.9,18.6]]}`). It is a loose `dict`, so Pydantic does not check what is inside.
- `toll_fare_paise: int = 0`: the `= 0` is a **default value**, used if the caller gives nothing.

## 4. How data flows
```
App --GET route(from,to)--> maps route --> maps service --> map provider (outside web service)
service builds RouteResponse(distance, duration, geometry, toll)
        --> JSON --> app draws the line
```

## 5. Try it
From `backend/`:
```
uv run python -c "from app.schemas.maps import RouteResponse as R; print(R(distance_meters=1000, duration_seconds=120, geometry={}))"
```
Expected: `distance_meters=1000 duration_seconds=120 geometry={} toll_fare_paise=0` (the default fills in).

## 6. Can it be better?
- Good: small, with a default for tolls.
- Weak: `list[float]` and `dict` are vague. A reader cannot tell the order in `service_area`.
- Cleaner way: `geometry: dict` could become a `LineString` schema with `type: Literal['LineString']` and `coordinates: list[tuple[float, float]]`. Name the area fields (`west`, `south`, ...).
- Security: none here.

## 7. Check yourself
1. What is geocoding?
2. What value does `toll_fare_paise` get if the code does not set it?
