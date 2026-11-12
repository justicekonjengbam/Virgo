# backend/app/services/driver_auth_service.py

## 1. Purpose
This file is the driver version of login. Drivers use only Firebase phone verification (no password). It also saves driver onboarding (city, vehicle, documents) and the driver profile. API routes for drivers call `DriverAuthService`. It calls `DriverRepository` (database), `firebase_service.py`, and `config.py`.

## 2. Imports, one by one

### Standard library
- `from datetime import UTC, datetime, timedelta` (`driver_auth_service.py:1`). Time values, UTC zone, and durations. *Example:* `datetime.now(UTC) + timedelta(days=7)`.
- `import logging` (`:2`). Python log writer.

### Third-party
- `import jwt` (`:4`). PyJWT: `jwt.encode` makes tokens, `jwt.decode` reads them.
- `from fastapi import HTTPException, status` (`:5`). HTTP errors with named codes.
- `from firebase_admin import auth as firebase_auth` (`:6`). Google's server library to verify Firebase ID tokens.
- `from sqlalchemy.orm import Session` (`:7`). A database session (type hint here).

### Project
- `from app.core.config import get_settings` (`:9`). Settings (secret key, token lifetimes).
- `from app.models.ride_hailing import Driver, DriverDocument, Vehicle` (`:10`). Table classes.
- `from app.repositories.driver_repository import DriverRepository` (`:11`). The database queries for drivers.
- `from app.schemas.auth import (...)` (`:12-20`). Pydantic shapes: `DriverAuthResponse`, `DriverFirebaseLoginRequest`, `DriverFirebaseSignupRequest`, `DriverOnboardingRequest`, `DriverProfileResponse`, `DriverProfileUpdateRequest`, `DriverRegistrationRequest`.
- `from app.services.firebase_service import initialize_firebase` (`:21`). Starts Firebase once.

## 3. Walk through the code

### `class DriverAuthService` (`:26`)
The docstring (`:27`) says it handles Driver Firebase identity and onboarding.

**`__init__`** (`:29-31`): same pattern as the passenger service: use a given repository or make `DriverRepository()`; store settings.

**`signup(db, request)`** (`:33-52`). Verifies the Firebase token (`:34`) to get `(firebase_uid, phone_number)`. Looks for an existing driver by uid or by phone (`:35-37`); if found, 409. Otherwise creates `Driver(... status="pending")` (`:43-51`). "pending" means admins have not approved the documents yet. Returns `_auth_response`.

**`login(db, request)`** (`:54-66`). Same verification; finds the driver or raises 404. Stores the uid (so a phone-only match becomes linked) and saves. Returns tokens plus profile.

**`refresh(db, refresh_token)`** (`:68-76`). `_decode(..., "refresh")` then `db.get(Driver, int(payload["sub"]))` loads the driver by primary key. If missing, or `status` is `suspended` or `deactivated`, 401. This is the check the passenger service lacks.

**`complete_registration(db, request)`** (`:78-90`). One-shot signup that also saves the vehicle and documents.
- Builds `Driver`, `Vehicle`, and a list of `DriverDocument` (`:83-85`). `driver_id=0` is a placeholder; the repository must fill the real id after the driver is saved (see `driver_repository.py`).
- `self.repository.create_complete_registration(db, driver, vehicle, documents)` saves all in one transaction (`:87`).
- Any exception becomes a 409 with a generic message (`:88-89`).
- `.strip()` removes spaces at the ends: `' Asha '` becomes `'Asha'`.

**`complete_onboarding(db, driver, request)`** (`:92-120`). For an already-logged-in driver. If the driver already has an active vehicle assignment, 409 (`:95-99`). Otherwise sets the city, creates a `Vehicle` with status `pending`, and `create_vehicle_and_assignment` links the driver to it. On error it does `db.rollback()` and raises 409 "registration number already in use" (`:111-118`). Saves the driver and returns the profile.

**`profile(db, driver)`** (`:122-130`). Builds `DriverProfileResponse`. `onboarding_completed` is true when an active assignment exists (`is not None`).

**`update_profile`** (`:132-138`). Changes name and/or city only when the field was sent (`is not None`), so a partial update is possible.

**`_auth_response`** (`:140-149`). Makes the access token (minutes), refresh token (days), and the profile in one answer.

**`_verified_firebase_identity`** (`:151-179`). Calls `initialize_firebase()`, then `firebase_auth.verify_id_token(id_token, clock_skew_seconds=60)` (`:156`). The comment (`:154-155`) explains the 60 seconds: phone clocks drift. Errors map to friendly messages by the exception class name (`:160-167`) and raise 401. Missing `uid` or `phone_number` gives 400 (`:174-178`). Returns the uid and the digits-only phone.

**`_encode`** (`:181-191`). Payload has `sub`, `type`, `actor: "driver"`, `exp`. The `actor` field stops a passenger token from working as a driver token.

**`_decode`** (`:193-204`). Verifies signature, `type`, and `actor == "driver"`; otherwise 401.

## 4. How data flows
```
Driver app --id_token--> route --> DriverAuthService.login
    initialize_firebase -> verify_id_token --> Google
    DriverRepository.get_by_firebase_uid / get_by_phone --> DB
    save -> _auth_response: jwt.encode x2 + profile
Driver app <-- {access_token, refresh_token, driver{...}}
```

## 5. Try it
Not directly runnable (needs Firebase and a database). You can see the token shape:
```bash
cd backend && uv run python -c "import jwt,datetime as d; t=jwt.encode({'sub':'1','actor':'driver','exp':d.datetime.now(d.UTC)+d.timedelta(minutes=5)},'k',algorithm='HS256'); print(jwt.decode(t,'k',algorithms=['HS256']))"
```
Expected: a dict with `sub`, `actor`, and `exp` as a number.

## 6. Can it be better?
- **Good:** `actor` claim separates driver and passenger tokens; refresh checks account status; uses a transaction for registration.
- **Weak:**
  - `_verified_firebase_identity` and the error table are copied from `auth_service.py`. Move to `firebase_service.py` once.
  - `complete_registration` catches `Exception` (`:88`), which hides real bugs (a database outage looks like "duplicate"). Catch `IntegrityError`.
  - `complete_registration` and `complete_onboarding` repeat the `Vehicle(...)` build code. Extract `_new_vehicle(request)`.
  - `DriverDocument(driver_id=0, ...)` is a placeholder trick.
  - `signup` and `complete_registration` duplicate the existence check.
  - Quote style is double quotes here but single quotes in other services; pick one.
- **Cleaner way:**
```python
# before
except Exception as error:
# after
except IntegrityError as error:
    db.rollback()
```
- **Security:** keep `jwt_secret_key` as `<secret>` in `.env`. Log lines include only the error class name (`:159`), which is good; `exc_info=True` may still print token text in a traceback in some cases, so review the logs.

## 7. Check yourself
1. Which claim in the token stops a passenger token from being used on driver routes, and where is it checked?
2. What does `refresh` check in the database that passenger `refresh` does not?
