# backend/app/services/passenger_profile_service.py

## 1. Purpose
Reads and updates a passenger's profile (name, email, language). Routes in `backend/app/api/` call `PassengerProfileService.get` and `.update`. It uses the models in `backend/app/models/` and schemas in `backend/app/schemas/profile.py`.

## 2. Imports, one by one
- `from fastapi import HTTPException, status` (line 1). **FastAPI** is the web framework. `HTTPException` is an error that FastAPI turns into an HTTP error reply. `status` holds named codes. *Example:* `raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='x')` sends a 409 with JSON `{"detail":"x"}`.
- `from sqlalchemy import select` (line 2). Builds SQL SELECT queries. *Example:* `select(Passenger)`.
- `from sqlalchemy.orm import Session` (line 3). The database session type, used as a hint.
- `from app.models.ride_hailing import PassengerProfile` (line 5). The profile table class.
- `from app.models.user import Passenger` (line 6). The passenger table class.
- `from app.schemas.profile import PassengerProfileResponse, PassengerProfileUpdateRequest` (line 7). Pydantic classes: the JSON going out, and the JSON coming in.

## 3. Walk through the code, top to bottom
### `get` (lines 11-13)
Input: `db`, `passenger`. Gets the profile with `self._profile(...)` then returns `self._response(...)`. Example out: `{full_name, phone_number, email, preferred_language}`.

### `update` (lines 15-29)
- Line 16: loads (or creates) the profile.
- Lines 17-21: if the request has an email, look for another profile with the same lowercase email and a different `passenger_id` (`!=`). If found, raise 409 (line 20). Else store the lowercase email. Lowercase makes `A@x.com` and `a@x.com` the same.
- Lines 22-23: language is saved in lowercase.
- Lines 24-25: name is saved with `.strip()` (removes spaces at both ends: `" Ann "` becomes `"Ann"`).
- Line 26: `db.add_all([...])` tells the session to track both objects.
- Line 27: `db.commit()` writes the changes permanently.
- Line 28: `db.refresh(x)` reloads the object from the database so values are current.
Note: `is not None` means only fields the client sent are changed (a partial update).

### `_response` (lines 31-33, `@staticmethod`)
A **staticmethod** (a method that does not use `self`; you can call it on the class). Builds the response from two objects.

### `_profile` (lines 35-42, `@staticmethod`)
`db.get(PassengerProfile, passenger.id)` looks up by primary key (line 37) and returns `None` if missing. If missing, it makes a new profile, `db.add` it and `db.flush()` (send the INSERT to the database now but do not commit yet). So a GET can create a row. Whoever commits later keeps it. In `get`, nothing commits, so the new row may be rolled back at the end of the request. I am not sure; check `backend/app/db.py` for how sessions close.

## 4. How data flows
```
App --PATCH /profile {email}--> route --> update()
  _profile -> DB get (or insert) ; duplicate-email SELECT
  set fields -> commit -> refresh -> PassengerProfileResponse --> App
```

## 5. Try it
Not directly runnable. Call the profile route with curl and a token; expect JSON with the four fields. Sending an email that another user has gives HTTP 409.

## 6. Can it be better?
- Good: lowercases email, checks duplicates, partial updates.
- Weak: the duplicate check and the save are not atomic. Two requests at the same time can both pass. Fix with a unique database constraint on `email` and catch `IntegrityError` (as `ride_matching_service.py:285` does). `full_name` is not checked for empty after strip. No email format check here (maybe in the schema; check).
- Security: users can only edit their own profile because `passenger` comes from the login token.

## 7. Check yourself
1. Why is `.lower()` used on the email before the duplicate check?
2. What is the difference between `db.flush()` and `db.commit()`?
