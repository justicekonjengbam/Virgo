# backend/app/schemas/home.py

## 1. Purpose
This file defines the shapes used by the passenger app's Home screen: saved places, ride categories, recent rides, the whole home answer, and a place search suggestion. A **schema** is a class that describes the shape of data in an API answer. The home route and service build these objects and FastAPI sends them as JSON to the passenger app.

## 2. Imports, one by one
- `from datetime import datetime` (`home.py:1`). The Python type for date plus time. *Example:* `datetime(2026,10,26,9,0)`. Used for `completed_at`.
- `from pydantic import BaseModel` (`home.py:3`). **Pydantic** checks data against a class. *Example:* it turns `"5"` into `5` for an `int` field. `BaseModel` is the parent class that gives this behavior.

## 3. Walk through the code, top to bottom

### `PlaceResponse` (`home.py:6-11`)
A saved place such as "Home" or "Office". Fields: `id` (int), `label` (the name the user gave), `formatted_address` (full address text), `latitude` and `longitude` (floats; map coordinates, *example:* `18.52`, `73.85`).

### `RideCategoryResponse` (`home.py:14-21`)
One choice of vehicle type. `code` (a short id like `"sedan"`), `display_name` (text for the screen), `seat_count`, `base_fare_paise` (starting price in paise, 1/100 rupee), `estimated_arrival_minutes`, `icon_key` (a name the app maps to a picture).

### `RecentRideResponse` (`home.py:24-30`)
A past ride. `completed_at: datetime | None` and `final_duration_seconds: int | None` may be null (for example if the ride is not finished). `fare_paise` is an int.

### `HomeResponse` (`home.py:33-37`)
The whole home screen in one answer. `passenger_name` is text. The other three fields are **lists of other schemas**: `list[PlaceResponse]` means "a list where every item must be a valid `PlaceResponse`". Pydantic checks each item.

### `PlaceSuggestionResponse` (`home.py:40-42`)
One search suggestion while the user types an address: `place_id` (id from the map provider) and `description` (text).

Example: `HomeResponse(passenger_name="Asha", saved_places=[], ride_categories=[], recent_rides=[])` is valid.

## 4. How data flows
```
Passenger app --GET home--> route --> service --> database (places, categories, rides)
service builds PlaceResponse / RideCategoryResponse / RecentRideResponse
        --> HomeResponse --> JSON --> Passenger app Home screen
```

## 5. Try it
From `backend/`:
```
uv run python -c "from app.schemas.home import HomeResponse as H; print(H(passenger_name='Asha', saved_places=[], ride_categories=[], recent_rides=[]).model_dump_json())"
```
`model_dump_json()` turns the object into a JSON string. Expected: `{"passenger_name":"Asha","saved_places":[],"ride_categories":[],"recent_rides":[]}`.

## 6. Can it be better?
- Good: nesting schemas keeps one request for the whole screen.
- Weak: no range checks on latitude (-90..90) or longitude (-180..180); `outstation.py` does have them. Nullable fields have no `= None` default.
- Cleaner way: `latitude: float = Field(ge=-90, le=90)`.
- Security: none; these are output only.

## 7. Check yourself
1. What does `list[PlaceResponse]` mean?
2. Which fields in this file may be null, and how can you tell?
