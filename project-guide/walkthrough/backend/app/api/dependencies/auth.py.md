# `backend/app/api/dependencies/auth.py`

## 1. Purpose
This file gives routes a way to know **which passenger** is calling. A route adds `Depends(get_current_passenger)` and FastAPI runs this check first. If the token is bad, the request stops with HTTP 401. The driver and admin versions are `driver_auth.py` and `admin_auth.py` in the same folder. Passenger routes in `api/v1/routes/` call it.

## 2. Imports, one by one
Third party:
- `import jwt` (`auth.py:1`). **PyJWT**: reads and checks JWTs (JSON Web Token: a signed text such as `header.payload.signature` that carries claims like user id). *Example:* `jwt.decode(token, key, algorithms=['HS256'])` returns the payload dictionary or raises an error. It can also create tokens with `jwt.encode`.
- `from fastapi import Depends, HTTPException, status` (`auth.py:2`). `Depends` marks a **dependency** (a function FastAPI runs for you and passes the result in. *Example:* `db: Session = Depends(get_db)`). `HTTPException` stops a request with an error reply. `status` has named codes. *Example:* `status.HTTP_401_UNAUTHORIZED` is `401`.
- `from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer` (`auth.py:3`). `HTTPBearer` reads the header `Authorization: Bearer <token>`. `HTTPAuthorizationCredentials` is the object it returns (`.scheme` = "Bearer", `.credentials` = the token text).
- `from sqlalchemy.orm import Session` (`auth.py:4`). The type of a database session. Used here only as a type hint (a label for readers and tools).

Project:
- `from app.core.config import get_settings` (`auth.py:6`), from `core/config.py`: secret key and algorithm.
- `from app.db import get_db` (`auth.py:7`), from `db.py`: gives a database session.
- `from app.models.user import Passenger` (`auth.py:8`), from `models/user.py`: the passenger table class.

## 3. Walk through the code, top to bottom

**`bearer_scheme = HTTPBearer(auto_error=False)`** (`auth.py:10`)
Creates the header reader. `auto_error=False` means: if the header is missing, return `None` instead of FastAPI's own error. This file then sends its own message.

**`def get_current_passenger(credentials=Depends(bearer_scheme), db=Depends(get_db)) -> Passenger`** (`auth.py:13-33`)
- Inputs (filled by FastAPI, not by you): `credentials` (token or `None`), `db` (session).
- Output: the `Passenger` row. Example: a route `def me(p: Passenger = Depends(get_current_passenger))` receives passenger 7.
- Lines 17-18: no token gives 401 "Authentication is required."
- Line 19: read settings.
- Lines 20-25: `jwt.decode(token, secret, algorithms=[...])` checks the signature and the expiry time. It returns the payload. Passing `algorithms` explicitly is important: it blocks tokens signed with a weaker method.
- Lines 26-27: the payload must say `type == 'access'` (so a refresh token cannot be used as an access token). Otherwise `raise ValueError`, caught below.
- Line 28: `db.get(Passenger, int(payload['sub']))` asks the database for the Passenger with that id (`sub` = "subject", the user id). It returns `None` if no row exists.
- Lines 29-30: any of `jwt.PyJWTError` (bad or expired token), `KeyError` (no `sub`), `TypeError`, `ValueError` becomes 401 "Invalid access token." `from error` keeps the original error for debugging.
- Lines 31-32: passenger must exist, have a verified phone, and have `status == 'active'`; otherwise 401 "Your account is not available."
- Line 33: return the passenger.

## 4. How data flows
```
Passenger app --GET /... Authorization: Bearer <token>--> FastAPI
   FastAPI runs: bearer_scheme (reads header) + get_db (opens session)
        -> get_current_passenger
             jwt.decode -> payload {sub:"7", type:"access"}
             db.get(Passenger, 7) -> row
             checks (phone verified, active)
        -> route function receives Passenger
   any failure -> 401 JSON {"detail": "..."}
```

## 5. Try it
```bash
curl -i http://127.0.0.1:8000/api/v1/<a-passenger-route>
curl -i -H "Authorization: Bearer abc" http://127.0.0.1:8000/api/v1/<a-passenger-route>
```
- `curl -i` prints headers too. `-H` adds a header. Replace the placeholder with a real passenger route from `api/v1/routes/`.
- Expected: first `401 {"detail":"Authentication is required."}`, second `401 {"detail":"Invalid access token."}`.

## 6. Can it be better?
- Good: pins the algorithm, checks token type, checks account status, hides the cause from the client.
- Weak:
  - It does not check an `actor` claim, but the driver and admin files do (`driver_auth.py:21`, `admin_auth.py:22`). A driver's access token has `actor: driver`; whether it could pass here depends on what `sub` ids exist. Same secret, same `type`. This looks like a gap (I am not sure; check how tokens are made in the auth service).
  - No `token_version` check like admin has, so old tokens live until expiry.
  - Reads `get_settings()` once here but twice in the other files (inconsistent style).
  - Same logic is copied in three files.
- Cleaner way (opinion): one helper `decode_access_token(token, actor)` used by all three files, and require `actor == 'passenger'` here.
- Security: JWT signing key comes from settings (`<secret>`), never print it.

## 7. Check yourself
1. Why does the code reject a token whose `type` is not `access`?
2. What are the four reasons this function can return 401, and which line raises each?
