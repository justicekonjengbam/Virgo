# `backend/app/api/dependencies/driver_auth.py`

## 1. Purpose
This file tells routes **which driver** is calling. Add `Depends(get_current_driver)` to a driver route and FastAPI checks the token first. Its twins are `auth.py` (passenger) and `admin_auth.py` (admin). Driver routes in `api/v1/routes/` (for example `driver_dashboard.py`) use it.

## 2. Imports, one by one
Third party:
- `import jwt` (`driver_auth.py:1`). **PyJWT** reads and checks JWTs (JSON Web Token: signed text carrying claims like user id). *Example:* `jwt.decode(token, key, algorithms=['HS256'])` returns a dictionary or raises. It can also `jwt.encode`.
- `from fastapi import Depends, HTTPException, status` (`:2`). `Depends` marks a **dependency** (a function FastAPI runs and feeds into your route). `HTTPException` ends the request with an error reply. `status.HTTP_401_UNAUTHORIZED` is the number `401`.
- `from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer` (`:3`). `HTTPBearer` reads `Authorization: Bearer <token>`; `HTTPAuthorizationCredentials` is the result with `.credentials` = token text.
- `from sqlalchemy.orm import Session` (`:4`). Database session type, used as a type hint.

Project:
- `from app.core.config import get_settings` (`:6`), from `core/config.py`.
- `from app.db import get_db` (`:7`), from `db.py`.
- `from app.models.ride_hailing import Driver` (`:8`), from `models/ride_hailing.py`: the driver table class.

## 3. Walk through the code, top to bottom

**`bearer_scheme = HTTPBearer(auto_error=False)`** (`:10`)
Header reader. With `auto_error=False` a missing header gives `None`, so this file writes its own message. Note: the name `bearer_scheme` is the same as in `auth.py:10`, but they are separate objects in separate modules.

**`def get_current_driver(credentials=Depends(bearer_scheme), db=Depends(get_db)) -> Driver`** (`:13-28`)
- Inputs come from FastAPI. Output: the `Driver` row.
- Lines 17-18: no token gives 401 "Authentication is required."
- Line 20: `jwt.decode(...)` checks signature and expiry using the secret and algorithm from settings (`get_settings()` called twice, harmless because it is cached).
- Line 21: payload must have `type == 'access'` and `actor == 'driver'`. **Actor** (a claim naming what kind of user the token was made for). This blocks a passenger or admin token. Otherwise `raise ValueError`.
- Line 23: `db.get(Driver, int(payload['sub']))` fetches the driver row by id, or `None`.
- Lines 24-25: bad token, missing `sub`, wrong types become 401 "Invalid Driver access token."
- Lines 26-27: if no driver, or `driver.status` is `'suspended'` or `'deactivated'` (a **set**, `{...}`, a collection with fast membership test), 401 "Your Driver account is not available."
- Line 28: return the driver.
- Note: unlike `auth.py`, a driver in status such as `pending` or `rejected` still passes; only suspended and deactivated are blocked. This looks deliberate (new drivers must upload documents), but I am not sure.

## 4. How data flows
```
Driver app --Authorization: Bearer <token>--> FastAPI
   -> get_current_driver
        jwt.decode -> {sub:"3", type:"access", actor:"driver"}
        db.get(Driver, 3) -> row
        status check
   -> route receives Driver
   failure -> 401 {"detail": "..."}
```

## 5. Try it
```bash
curl -i -H "Authorization: Bearer abc" http://127.0.0.1:8000/api/v1/<a-driver-route>
```
- `-i` shows headers, `-H` adds the header. Use a real driver route path from `api/v1/routes/driver_dashboard.py`.
- Expected: `401` with `{"detail":"Invalid Driver access token."}`.

## 6. Can it be better?
- Good: checks `actor`, token type and account status; consistent 401 message.
- Weak:
  - Copy of `auth.py` and `admin_auth.py` with small changes.
  - No `token_version` check like admin has (`admin_auth.py:25`), so a suspended-then-restored driver keeps old tokens.
  - Allowed statuses are an inverse list (block-list). A new status added later would be allowed by default. An allow-list is safer (opinion).
- Cleaner way:
```python
BLOCKED = {'suspended', 'deactivated'}
if not driver or driver.status in BLOCKED: ...
```
  and share one `decode_access_token(token, actor)` helper.
- Security: signing key is `<secret>` from settings; keep it out of git.

## 7. Check yourself
1. Which claim stops a passenger token from working on a driver route?
2. Which driver statuses are blocked here, and which are let through?
