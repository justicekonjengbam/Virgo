# backend/app/api/v1/routes/passenger_profile.py

## 1. Purpose
This file lets a passenger read (`GET`) and change (`PATCH`) their own profile at `/passengers/me/profile`. It hands the work to `PassengerProfileService` (`backend/app/services/passenger_profile_service.py`).

## 2. Imports, one by one
**Third-party**
- `from fastapi import APIRouter, Depends` (`passenger_profile.py:1`). Router and dependency injection (FastAPI calls a helper and passes the result in).
- `from sqlalchemy.orm import Session` (`:2`). A database session, used as a type hint.

**Project**
- `get_current_passenger` from `app/api/dependencies/auth.py` (`:4`): returns the logged-in `Passenger`.
- `get_db` from `app/db.py` (`:5`): gives a session per request.
- `Passenger` from `app/models/user.py` (`:6`).
- `PassengerProfileResponse, PassengerProfileUpdateRequest` from `app/schemas/profile.py` (`:7`): output shape and input shape.
- `PassengerProfileService` from `app/services/passenger_profile_service.py` (`:8`).

## 3. Walk through the code, top to bottom
- `router = APIRouter(prefix='/passengers/me/profile', tags=['passenger-profile'])` (`:10`); `service = PassengerProfileService()` (`:11`).
- `@router.get('', ...)` -> `get_profile` (`:14-16`). Path `''` is the prefix itself. Returns `service.get(db, passenger)`.
- `@router.patch('', ...)` -> `update_profile` (`:19-21`). `request: PassengerProfileUpdateRequest` is the JSON body, checked by Pydantic (the library that validates data against a class). Returns `service.update(db, passenger, request)`.

Example: `PATCH` with body `{"name":"Asha"}` returns the full profile with the new name (field names are in `schemas/profile.py`).
Errors: 401 bad token, 422 body fails validation.

## 4. How data flows
```
App --PATCH /passengers/me/profile {json}--> FastAPI
  body -> PassengerProfileUpdateRequest ; token -> Passenger ; Session
  PassengerProfileService.update(db, passenger, request) -> saves
App <-- PassengerProfileResponse
```

## 5. Try it
```zsh
curl -s -H "Authorization: Bearer <token>" http://127.0.0.1:8000/passengers/me/profile
```
Expected: the profile JSON. PATCH needs `-X PATCH -H "Content-Type: application/json" -d '{...}'`.

## 6. Can it be better?
- Good: tiny, consistent with other routes, no logic in the route.
- Weak: global `service`; no visible tests here.
- Cleaner way: provide the service through `Depends` so tests can swap it. (Opinion.)
- Security: the user id comes from the token, not the URL, so a passenger can only edit their own profile. Good.

## 7. Check yourself
1. Why is the path `''` and not `'/'`?
2. Where does the passenger identity come from, since the URL has no id?
