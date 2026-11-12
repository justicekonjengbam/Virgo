# `backend/app/api/dependencies/admin_auth.py`

## 1. Purpose
This file protects admin routes. `get_current_admin` finds the admin from the token. `require_admin_permission("x")` goes one step further and also checks that the admin's role is allowed to do action `x`. Admin routes (for example `api/v1/routes/admin.py`) use these. Passenger and driver twins: `auth.py`, `driver_auth.py`.

## 2. Imports, one by one
Third party:
- `import jwt` (`admin_auth.py:1`). **PyJWT** reads and checks JWTs (JSON Web Token: signed text with claims). *Example:* `jwt.decode(token, key, algorithms=['HS256'])` returns a dictionary or raises `jwt.PyJWTError`.
- `from fastapi import Depends, HTTPException, status` (`:2`). `Depends` = a **dependency** (function FastAPI runs and passes into your route). `HTTPException` ends a request with an error. `status.HTTP_403_FORBIDDEN` is `403`.
- `from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer` (`:3`). Reads `Authorization: Bearer <token>`.
- `from sqlalchemy.orm import Session` (`:4`). Session type hint.

Project:
- `from app.core.config import get_settings` (`:6`), `core/config.py`.
- `from app.db import get_db` (`:7`), `db.py`.
- `from app.models.user import AdminUser` (`:8`), `models/user.py`: admin table class.
- `from app.services.admin_auth_service import ROLE_PERMISSIONS` (`:9`), `services/admin_auth_service.py`: a dictionary mapping a role to the set of actions it may do. *Example (shape, simplified):* `{'super_admin': {'a','b'}, 'support': {'a'}}`.

## 3. Walk through the code, top to bottom

**`admin_bearer_scheme = HTTPBearer(auto_error=False)`** (`:11`) header reader; missing header gives `None`.

**`def get_current_admin(credentials, db) -> AdminUser`** (`:14-31`)
- Lines 18-19: no token gives 401 "Admin authentication is required."
- Line 21: `jwt.decode(...)` verifies signature and expiry.
- Line 22: must be `type == 'access'` and `actor == 'admin'`, else `raise ValueError`.
- Line 24: `db.get(AdminUser, int(payload['sub']))` loads the admin or `None`.
- Line 25: if the admin exists and the token's `ver` differs from `admin.token_version`, raise `ValueError`. **Token version** (a number stored on the admin; raising it kills all older tokens. *Example:* after a password reset, version goes 2 to 3, and tokens with `ver: 2` stop working).
- Lines 27-28: errors become 401 "Invalid Admin session."
- Lines 29-30: admin missing or `is_active` false gives 401 "Your Admin account is unavailable."
- Line 31: return the admin.

**`def require_admin_permission(permission: str)`** (`:34-39`)
- A **factory** (a function that builds and returns another function). Call it while writing a route: `Depends(require_admin_permission('drivers.review'))` (the permission name here is an invented example).
- Inner `dependency` (lines 35-38) depends on `get_current_admin`, then looks up `ROLE_PERMISSIONS.get(admin.role, set())`. `.get(key, default)` returns the default (empty set) for an unknown role. If `permission` is not in that set, 403 "Your Admin role does not permit this action." Else it returns the admin.
- 401 means "who are you?" and 403 means "I know you, but no."

## 4. How data flows
```
Admin web page --Bearer <token>--> route with Depends(require_admin_permission("p"))
   -> get_current_admin: decode -> AdminUser row -> checks (type, actor, ver, active)
   -> dependency: "p" in ROLE_PERMISSIONS[admin.role] ?
        yes -> route runs with admin
        no  -> 403
```

## 5. Try it
```bash
curl -i -H "Authorization: Bearer abc" http://127.0.0.1:8000/api/v1/<an-admin-route>
```
- Use a real path from `api/v1/routes/admin.py`.
- Expected: `401 {"detail":"Invalid Admin session."}`.

## 6. Can it be better?
- Good: strongest of the three checks (actor, token version, active flag, role permission).
- Weak:
  - If `admin` is `None` and the token was fine, line 25 skips the version check and line 29 catches it; correct, but the flow is hard to read.
  - `get_settings()` is called twice on line 21.
  - Same decode logic is copied in three files.
- Cleaner way (opinion): shared `decode_access_token(token, actor)` helper, and look up the admin once with a clear early exit.
- Security: permission names are plain strings; a typo in a route (for example `'drivers.reveiw'`) silently denies everyone. A constants list or test that every route permission exists in `ROLE_PERMISSIONS` would catch that. The signing key is `<secret>`.

## 7. Check yourself
1. What is the difference between returning 401 and 403 in this file?
2. What does the `ver` claim protect against?
