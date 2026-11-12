# backend/app/schemas/booking.py

## 1. Purpose
This file holds the message shapes for the whole ride flow: places, price estimate, booking, ride status, driver location, driver offers, cancel, start/complete actions, summary and rating. The ride routes use them. The passenger app and the driver app send and read this JSON. It only calls `pydantic`.

## 2. Imports, one by one
- `from datetime import datetime` (`booking.py:1`). A date+time type. *Example:* `requested_at: datetime` accepts `"2026-10-26T10:00:00Z"`.
- `from pydantic import BaseModel, Field, model_validator` (3). **Pydantic** checks data against type hints. `Field(ge=-90, le=90)` limits a number (ge = at least, le = at most, gt = more than). `pattern` is a regular expression the text must match. `model_validator(mode='after')` checks the whole object once all fields passed.

## 3. Walk through the code, top to bottom
Terms: **Request** classes are what a client sends. **Response** classes are what the server returns. **Paise**: 1/100 rupee, so `fare_paise=25000` is Rs 250. **GeoJSON** (a standard JSON format for map shapes and lines. *Example:* `{"type":"LineString","coordinates":[[77.5,12.9],[77.6,13.0]]}`).

- `LocationOptionResponse` (6-12). A place: optional `id` and `place_id`, `name`, address, `latitude`, `longitude` (floats).
- `SelectedPlaceRequest` (15-20). A place chosen from a map search. Latitude -90 to 90, longitude -180 to 180, text lengths limited.
- `RideEstimateRequest` (23-36). Pickup and destination may be given as catalog ids (`pickup_location_id`, `destination_location_id`, each `gt=0`) or as full places (`pickup`, `destination`), plus `category_id`. `validate_location_pair` (30-36) sets two booleans, `catalog_pair` and `live_pair`. If both are equal (both true or both false) it raises. This is an exclusive-or: exactly one style must be used. Example: ids only is fine; ids plus places fails; nothing fails. A mixed case such as a catalog pickup and a live destination also fails.
- `UpdateSavedPlaceRequest` (39-47). Either `location_id` or `location`, never both, never none: `(a is None) == (b is None)` is true in both bad cases.
- `FareItemResponse` (50-52). One fare line: label and paise.
- `RideEstimateResponse` (55-63). Pickup, destination, category name, `distance_km`, `duration_minutes`, `fare_paise`, `fare_items`, optional `route_geojson`.
- `RideBookingResponse` (66-73). After booking: id, status, addresses, fare, `requested_at`, message.
- `PassengerRideStatusResponse` (76-97). What the passenger app polls: status, message, addresses, driver and vehicle info (optional), arrival minutes, pickup/destination coordinates, driver coordinates and heading, route, `can_cancel`, `can_end` (default `False`), `ride_start_otp` (a code the passenger tells the driver to start), `cancellation_reason`.
- `DriverLocationUpdateRequest` (100-106). The driver app sends position: latitude, longitude, `heading_degrees` 0-359, `accuracy_meters` 0-500, `speed_mps` 0-80 (meters per second), optional `recorded_at`.
- `DriverRideOfferResponse` (109-121). An offer shown to a driver: `offer_id`, `ride_id`, addresses, distance, `expected_fare_paise`, minutes away, `expires_at`, coordinates.
- `DriverRideOfferDecisionRequest` (124-125). `decision` must match `^(accepted|declined)$`.
- `DriverRideOfferDecisionResponse` (128-131). Ride id, status, message.
- `RideCancellationRequest` (134-136). `reason` from a fixed list (`changed_plans`, `driver_delay`, ... `other`), and `confirm: bool`. The schema does not force `confirm` to be true; the service must check it.
- `RideActionRequest` (139-141). `action` is `arrived`, `start` or `complete`. `start_otp` is optional, four digits `^[0-9]{4}$`. Nothing here says that `start` needs an OTP; the service decides.
- `DriverActiveRideResponse` (144-156). The driver's current ride, with passenger name and flags.
- `RideMutationResponse` (159-162). A generic "done" result.
- `FareSummaryItemResponse` (165-167). Same shape as `FareItemResponse`.
- `RideSummaryResponse` (170-180). Receipt data plus two flags telling whether each side has rated.
- `RideRatingRequest` (183-185). Score 1-5, optional comment up to 300.
- `RideRatingResponse` (188-191). Ride id, score, message.

Errors: HTTP 422 for any broken rule.

## 4. How data flows
```
passenger-app --POST /rides/estimate {pickup:{...}, destination:{...}, category_id:1}--> FastAPI
  -> RideEstimateRequest.validate_location_pair (live_pair true, catalog_pair false: ok)
  -> service computes price -> RideEstimateResponse JSON -> app shows fare
```

## 5. Try it
```zsh
cd backend
uv run python -c "
from app.schemas.booking import RideEstimateRequest as R
try: R(category_id=1)
except Exception as e: print(e.errors()[0]['msg'])"
```
Expected: `Value error, Provide either two catalog locations or two selected places.`

## 6. Can it be better?
- Good: coordinate ranges, regex limits and the exclusive-or validators stop bad data early.
- Weak: statuses, decisions and reasons are text patterns, repeated as strings; `Literal[...]` types would document them and show in the API docs. `FareItemResponse` and `FareSummaryItemResponse` are duplicates. The validator functions have no return type. Money as `float` for distance is fine, but `confirm: bool` can be false. Coordinates as `float` differ from `Decimal` in the models (rounding at the edge).
- Cleaner way:
```python
# before
decision: str = Field(pattern='^(accepted|declined)$')
# after
decision: Literal['accepted', 'declined']
```
- Security: `start_otp` is a 4-digit code, so it can be guessed in 10,000 tries; the service should limit attempts. `ride_start_otp` is shown to the passenger only; be sure it never goes to the driver response.

## 7. Check yourself
1. Why does `RideEstimateRequest` fail when you send both catalog ids and full places?
2. Which classes are sent by the driver app, and which are shown to the passenger app?
