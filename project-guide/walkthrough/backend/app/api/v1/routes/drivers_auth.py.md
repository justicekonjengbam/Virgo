# backend/app/api/v1/routes/drivers_auth.py

## 1. Purpose
Driver login, registration, token refresh, profile read/update and onboarding. Used by `driver-app/`. Mounted at `router.py:20`. Calls `DriverAuthService` (`app/services/driver_auth_service.py`). URLs start with `/api/v1/auth/drivers`.

## 2. Imports, one by one
- `from fastapi import APIRouter, Depends, status` (`drivers_auth.py:1`): router, dependency injection, and named HTTP codes (`status.HTTP_201_CREATED == 201`).
- `from sqlalchemy.orm import Session` (`:2`): session type.
- `get_current_driver` (`:4`, `app/api/dependencies/driver_auth.py`), `get_db` (`:5`), `Driver` (`:6`).
- Schemas from `app/schemas/auth.py` (`:7-15`): `DriverAuthResponse` (tokens plus driver), `DriverFirebaseLoginRequest`, `DriverRegistrationRequest`, `RefreshRequest`, `DriverProfileResponse`, `DriverProfileUpdateRequest`, `DriverOnboardingRequest`.
- `DriverAuthService` (`:16`).

## 3. Walk through the code, top to bottom
- `router` prefix `/auth/drivers` (`:18`), `service` (`:19`).
- **`firebase_login`** `POST /firebase/login` (`:22-26`). The app sends a Firebase `id_token` (a proof from Google that the phone is verified). `service.login(db, request)` checks it and returns our tokens.
- **`register`** `POST /firebase/register`, 201 (`:29-31`). `service.complete_registration` creates the driver row.
- **`refresh`** `POST /refresh` (`:34-36`). `service.refresh(db, request.refresh_token)` swaps a refresh token for new tokens.
- **`get_me`** `GET /me` (`:39-43`). Needs login. `service.profile(db, driver)`.
- **`update_me`** `PATCH /me` (`:46-51`). Partial update of the profile (single quotes here, double elsewhere in the file: style mix).
- **`complete_onboarding`** `POST /onboarding` (`:54-60`). Saves onboarding data such as vehicle and documents (exact content unverified) via `service.complete_onboarding`.

## 4. How data flows
```
driver-app --Firebase phone login--> Google --id_token--> driver-app
driver-app --POST /auth/drivers/firebase/login {id_token}--> login()
   -> DriverAuthService.login: verify with Google, find Driver --> database
   <- DriverAuthResponse {access, refresh, driver}
```

## 5. Try it
`curl -s -H "Authorization: Bearer <secret>" localhost:8000/api/v1/auth/drivers/me`. Expect the profile JSON with a valid token; without one, a 401/403 error.

## 6. Can it be better?
- Good: consistent thin routes; login-only where needed.
- Weak: mixed quote style; the response model names do not tell login from register; no visible rate limit on login or refresh.
- Cleaner way: run `ruff format` for one style.
- Security: security depends on the service verifying the Firebase token properly (signature, expiry, audience). Check that file.

## 7. Check yourself
1. Which routes need a logged-in driver and which do not?
2. What does the app send to `/firebase/login`?
