# backend/tests/test_booking_policy.py

## 1. Purpose
Three small tests (automatic checks) for booking rules: the service area (150 km around Dharwad-Hubballi) and the night-charge hours. They call `MapProviderService` (`backend/app/services/map_provider_service.py`) and `BookingService` (`backend/app/services/booking_service.py`). Run them with pytest. They need no database.

## 2. Imports, one by one
Standard library:
- `from datetime import datetime` : Python's date-time type. *Example:* `datetime(2026, 8, 13, 4, 0)` is 13 Aug 2026, 04:00. Used to build a test time (`:28`).

Third party:
- `import pytest` : the test tool. *Example:* `pytest.raises(X)` passes only if code raises X. Used at `:20` and `:26`.
- `from fastapi import HTTPException` : the error FastAPI turns into an HTTP error reply. *Example:* `raise HTTPException(status_code=404)`. Used to check the error type (`:20`).

Project:
- `BookingService` from `app/services/booking_service.py`: booking logic. Here only its private helper `_is_night` is tested.
- `MapProviderService` from `app/services/map_provider_service.py`: map and service-area logic.

## 3. Walk through the code, top to bottom
**Test function** (a function whose name starts with `test_`; pytest finds and runs it. It passes if no error is raised.)

`test_service_area_accepts_dharwad_and_hubballi_locations` (`:10-14`)
- `MapProviderService()` makes an object with no arguments.
- `service.contains(lat, lng)` returns `True` when the point is inside the service radius (`service_radius_km = 150.0`, `map_provider_service.py:14`).
- `assert x` : if `x` is false the test fails. The two points are near Dharwad (15.4589, 75.0078) and Hubballi (15.3518, 75.1379). Both must be `True`.

`test_service_area_rejects_locations_beyond_150_km` (`:17-23`)
- The point (12.9716, 77.5946) is Bengaluru, far away.
- `with pytest.raises(HTTPException) as error:` runs the block and expects an `HTTPException`. If none is raised, the test fails. `error` holds it afterwards.
- `service.ensure_in_service_area(...)` raises `HTTPException(422, 'Choose a location within 150 km...')` (`map_provider_service.py:59-61`).
- `error.value.status_code == 422` checks the HTTP code. 422 means "I understood the request but the data is not acceptable".

`test_night_charge_window` (`:26-28`)
- `@pytest.mark.parametrize(('hour','expected'), [...])` is a **decorator** (a line starting with `@` that wraps the function below it). It runs the same test once per pair: (0,True), (4,True), (5,False), (21,False), (22,True).
- `BookingService._is_night(datetime(2026,8,13,hour,0))` is a static method. Its rule is `hour >= 22 or hour < 5` (`booking_service.py:152-153`). So night is 22:00 to 04:59.
- `is expected` compares to `True`/`False` exactly. The edge hours 4, 5, 21, 22 are what make this test useful.

## 4. How data flows
```
pytest -> test_night_charge_window(hour=22, expected=True)
       -> datetime(2026,8,13,22,0) -> BookingService._is_night -> True
       -> assert True is True -> pass
```

## 5. Try it
```zsh
cd backend && uv run pytest tests/test_booking_policy.py -v
```
`-v` lists each test. Expected: 7 passed (1 + 1 + 5 parameter cases).

## 6. Can it be better?
- Good: clear names; edge hours are tested; no database needed.
- Weak: the test calls a private method `_is_night` (the underscore means "internal"), so renaming it breaks the test. Only 2 inside points and 1 outside; no point exactly near 150 km. Dates use a fixed day, no time-zone case.
- Cleaner way (opinion): make `is_night` public, and add boundary tests at about 149 km and 151 km.
- Security: none.

## 7. Check yourself
1. Which hours does the night window include, and which test cases prove the edges?
2. What does `pytest.raises` do when no error happens?
