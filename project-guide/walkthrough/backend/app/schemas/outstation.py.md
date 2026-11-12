# backend/app/schemas/outstation.py

## 1. Purpose
This file defines all data shapes for **outstation bookings** (long trips to another city, booked in advance for a later date, confirmed by the support team). A **schema** is a class that describes and checks the shape of data. Some schemas here are for requests coming in (passenger booking, cancel, admin update), some are for answers going out (estimate, booking, driver lists). Routes for passengers, drivers and admins use them, along with an outstation service (not read for this file).

## 2. Imports, one by one
Standard library:
- `from datetime import datetime` (`outstation.py:1`). Python's date-and-time type. *Example:* `datetime(2026,11,2,6,0)`. Used for trip times.
- `from typing import Literal` (`outstation.py:2`). `Literal['a','b']` is a type that allows only those exact values. *Example:* `Literal['sedan','suv']` accepts `'suv'` and rejects `'bus'`.

Third party:
- `from pydantic import BaseModel, Field, field_validator` (`outstation.py:4`). **Pydantic** checks data against a class. `BaseModel` is the parent class. `Field(...)` adds rules to a field (like `min_length`). `field_validator` is a **decorator** (a line starting with `@` that wraps a function to change its role) that says "run this function to check or clean one field". Pydantic can also do `model_validator` for rules across many fields (see `profile.py`).

## 3. Walk through the code, top to bottom

### Type names (`outstation.py:7-8`)
- `VehiclePreference = Literal['sedan', 'suv', 'muv']`: only these three vehicle types are allowed. A name for a type, reused below.
- `OutstationStatus = Literal['requested', 'confirmed', 'driver_assigned', 'completed', 'cancelled', 'rejected']`: the life of a booking. This alias is defined but I did not see it used in this file (`status` fields below use plain `str`). Check with `rg OutstationStatus backend`.

### `OutstationLocation` (`outstation.py:11-16`)
A place in a request. Rules:
- `place_id`: 1 to 255 characters. `name`: 1 to 160. `formatted_address`: 5 to 512.
- `latitude`: `ge=-90, le=90` (greater-or-equal -90, less-or-equal 90). `longitude`: -180 to 180.
Example: latitude `95` raises `ValidationError`.

### `OutstationBookingCreate` (`outstation.py:19-23`)
The body the passenger sends to book: `scheduled_at` (datetime), `pickup` and `destination` (each an `OutstationLocation`, so Pydantic checks them inside), and `preferred_vehicle_type` (one of the three, or `None`, default `None`).

### `OutstationEstimateResponse` (`outstation.py:26-31`)
The price estimate: `distance_km`, `duration_minutes`, `estimated_fare_paise`, `route_geojson` (a dict with the route shape), and `disclaimer` with a default text saying support will confirm the final price.

### `OutstationBookingResponse` (`outstation.py:34-56`)
A full booking view. It mixes booking data (`id`, `scheduled_at`, `status`, addresses), estimates (nullable), driver and vehicle info (nullable until assigned: `driver_name`, `driver_phone_number`, `vehicle_name`, `vehicle_registration_number`), `can_cancel: bool` (the app shows the cancel button only if true), passenger info, coordinates (nullable) and `route_geojson`. Admin and passenger apps share it.

### `OutstationCancellationRequest` (`outstation.py:59-60`)
Body to cancel: `reason`, 3 to 255 characters.

### `AdminOutstationUpdate` (`outstation.py:63-79`)
Body an admin sends to change a booking.
- `status: Literal[...]`: only 5 values (no `'requested'`, since an admin cannot move a booking back to it).
- `estimated_distance_km`: optional, `ge=150, le=5000`. So an admin cannot set a distance under 150 km (outstation trips are long).
- `driver_phone_number`: optional text.
- `support_note`: optional, max 1000 characters.
- The validator (`outstation.py:69-79`):
  - `@field_validator('driver_phone_number')` says "run for this field".
  - `@classmethod` makes the first argument `cls` (the class) instead of an object. Pydantic needs this form.
  - If `value is None`, return `None` (nothing to check).
  - `digits = ''.join(character for character in value if character.isdigit())` keeps only digit characters. `"+91 98765-43210"` becomes `"919876543210"`.
  - If it has 12 digits and starts with `91` (India's country code), cut the first two: `digits[2:]` gives `"9876543210"`.
  - If the length is not 10, or the first digit is not in `'6789'` (Indian mobile numbers start with 6 to 9), `raise ValueError(...)`. Pydantic turns this into a validation error (HTTP 422 in FastAPI).
  - Return the clean 10 digits.

### `EligibleOutstationDriverResponse` (`outstation.py:82-91`)
A driver an admin may assign: name, phone, city (nullable), `rating`, `completed_rides`, and vehicle info with `seat_count`.

### `DriverOutstationAssignmentResponse` (`outstation.py:94-105`)
What the driver app shows for an assigned trip: status, time, addresses, passenger name and phone, estimated distance and fare, and vehicle details.

## 4. How data flows
```
Admin web --PATCH {status:"driver_assigned", driver_phone_number:"+91 98765 43210"}-->
  FastAPI builds AdminOutstationUpdate
     -> field_validator cleans phone to "9876543210" (or error 422)
  route -> service -> database
  service -> OutstationBookingResponse -> JSON -> Admin web
```

## 5. Try it
From `backend/`:
```
uv run python -c "from app.schemas.outstation import AdminOutstationUpdate as A; print(A(status='confirmed', driver_phone_number='+91 98765-43210').driver_phone_number)"
```
Expected: `9876543210`. Try `driver_phone_number='12345'` to see the error "Enter a valid 10-digit Indian driver mobile number." Try `estimated_distance_km=10` to see the 150 km rule.

## 6. Can it be better?
- Good: strong limits on text length and coordinates; phone cleaning in one place; `Literal` blocks bad values.
- Weak: `OutstationStatus` is unused here and `OutstationBookingResponse.status` is a plain `str`; `scheduled_at` can be in the past (no check); `OutstationBookingResponse` has 20 fields mixing passenger, admin and driver data, so a passenger may receive more than needed; nullable fields have no defaults.
- Cleaner way:
```python
status: OutstationStatus   # instead of: status: str
@field_validator('scheduled_at')
@classmethod
def future_only(cls, v): 
    if v <= datetime.now(v.tzinfo): raise ValueError('Pick a future time.')
    return v
```
(Opinion: check how the service handles time zones before adding this.)
- Security: driver and passenger phone numbers are personal data. Confirm each route returns only what that role should see.

## 7. Check yourself
1. What does `+91 98765-43210` become after `normalize_driver_phone`, and why must the first digit be 6, 7, 8 or 9?
2. Why does `AdminOutstationUpdate.status` not include `'requested'`?
