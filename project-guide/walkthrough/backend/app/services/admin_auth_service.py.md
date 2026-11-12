# backend/app/services/admin_auth_service.py

## 1. Purpose
This file holds the admin login logic. A **service** is a class that holds business rules, so route files stay thin. It creates the first admin from settings, checks the password, locks the account after too many wrong tries, makes a **JWT** (JSON Web Token: a signed text the admin sends with each request to prove who they are. *Example:* `eyJhbGci...`), and changes passwords. Admin routes call it. It reads settings (`app/core/config.py`), models (`app/models/user.py`, `app/models/ride_hailing.py`) and schemas (`app/schemas/admin.py`).

## 2. Imports, one by one
Standard library:
- `from datetime import UTC, datetime, timedelta` (`admin_auth_service.py:1`). `datetime` is date plus time. `UTC` is the world-standard time zone object. `timedelta` is a length of time. *Example:* `datetime.now(UTC) + timedelta(minutes=15)` is 15 minutes from now.

Third party:
- `import jwt` (`:3`). This is the PyJWT library. It makes and reads JWTs. *Example:* `jwt.encode({'a':1}, '<secret>', algorithm='HS256')` gives a token string. It can also `jwt.decode` and check expiry.
- `from fastapi import HTTPException, status` (`:4`). **FastAPI** is the web framework. `HTTPException` is an error that becomes an HTTP error answer. `status` holds named codes. *Example:* `status.HTTP_404_NOT_FOUND` is `404`.
- `from pwdlib import PasswordHash` (`:5`). A library for safe password hashing. A **hash** is a one-way scramble: you can check a password against it but cannot get the password back. *Example:* `h.hash("abc")` gives a long string; `h.verify("abc", that_string)` gives `True`.
- `from sqlalchemy import select` (`:6`). **SQLAlchemy** is the database toolkit (an ORM = Object-Relational Mapper, which lets you use Python classes for tables). `select(AdminUser)` builds a "get admin rows" query.
- `from sqlalchemy.orm import Session` (`:7`). A `Session` is one conversation with the database. Here it is used as a type for the `db` argument.

Project:
- `from app.core.config import get_settings` (`:9`): returns the app settings (secrets, times).
- `from app.models.ride_hailing import AuditLog` (`:10`): the table that records who did what.
- `from app.models.user import AdminUser` (`:11`): the admin table class.
- `from app.schemas.admin import AdminAuthResponse, AdminLoginRequest, AdminPasswordChangeRequest, AdminProfileResponse` (`:12`): shapes for login input, token answer, password change input, and profile answer.

## 3. Walk through the code, top to bottom

### `password_hash = PasswordHash.recommended()` (`:14`)
Makes one shared hasher with the library's recommended setting (argon2, as I understand it; check the pwdlib docs). Made once when the file loads.

### `ROLE_PERMISSIONS` (`:15-20`)
A dict from role name to a **set** of permission words (a set is a group with no repeats). *Example:* `'document_reviewer'` may only `drivers:read` and `documents:review`. `super_admin` is the only role with `admins:manage`.

### `class AdminAuthService` (`:23`)
**`__init__`** (`:24-25`): runs when you write `AdminAuthService()`. Saves `get_settings()` in `self.settings`.

**`bootstrap(db)`** (`:27-40`): makes sure the first admin exists.
- Reads email and password from settings (`:28`). If either is empty, `return` (do nothing).
- `normalized = email.strip().lower()` cleans the email.
- `db.scalar(select(AdminUser).where(AdminUser.email == normalized))` runs the query and returns the first match or `None`.
- If the admin exists and the role differs from settings, the role is updated and saved (`:33-38`). `db.add(x)` marks it for saving; `db.commit()` writes to the database for real.
- Otherwise a new `AdminUser` is added with `password_hash.hash(password)` so the plain password is never stored (`:39-40`).
- Note: it does not update the password if settings change.

**`login(db, request)`** (`:42-62`): returns `AdminAuthResponse` or raises an error.
1. Look up the admin by `request.email` (`:43`). Note: it does not lower-case here; I am not sure if `AdminLoginRequest` does (check `schemas/admin.py`).
2. `now = datetime.now(UTC)`.
3. If the admin has `locked_until` in the future (via `_aware`), raise HTTP 423 Locked (`:45-46`).
4. If no admin, or not active, or password wrong (`:47`): if the admin exists and is active, add 1 to `failed_login_attempts`; at 5, set `locked_until` to 15 minutes ahead and reset the counter (`:48-54`); then raise 401 "Incorrect email or password." (same message for all cases, so attackers learn nothing).
   `password_hash.verify(request.password, admin.password_hash)` compares the typed password with the stored hash.
5. On success (`:56-62`): store `last_login_at`, reset counters, clear lock, write an `AuditLog` row (who, what, which entity), commit, and return the token and profile.

**`change_password(db, admin, request)`** (`:64-72`): checks the current password (else 400), saves a new hash, sets `password_changed_at`, and adds 1 to `token_version` (this makes older tokens invalid if the token check compares `ver`; check the auth dependency). Writes an audit row and commits.

**`_encode(admin)`** (`:74-75`): makes the JWT. The payload has `sub` (subject = admin id as text), `type: 'access'`, `actor: 'admin'`, `role`, `ver` (token version), and `exp` (expiry time). It is signed with `settings.jwt_secret_key` (`<secret>`) and the chosen algorithm.

**`_profile(admin)`** (`:77-79`): `@staticmethod` means no `self` needed. Builds the profile answer; `sorted(ROLE_PERMISSIONS.get(admin.role, set()))` gives the permission list in order, or empty for an unknown role.

**`_aware(value)`** (`:81-83`): databases may return times without a zone (naive). If `tzinfo is None`, it attaches UTC so comparing with `now` does not crash.

## 4. How data flows
```
Admin web --POST /admin/login {email,password}--> route
route --> AdminAuthService.login(db, request)
   db: SELECT admin WHERE email   <-- AdminUser row
   verify(password, hash)
   wrong? failed_attempts+1 (5 -> lock 15 min) -> 401
   right? update admin + AuditLog -> commit
   _encode -> JWT
route <-- AdminAuthResponse(access_token, admin profile) --> Admin web
```

## 5. Try it
Not directly runnable without a database. A small piece you can run, from `backend/`:
```
uv run python -c "from pwdlib import PasswordHash as P; h=P.recommended(); x=h.hash('abc'); print(h.verify('abc', x), h.verify('no', x))"
```
Expected: `True False`.

## 6. Can it be better?
- Good: hashed passwords; lock after 5 tries; same error text for wrong email and wrong password; audit log; token version; role permissions in one place.
- Weak: failed-login and lock updates are in one long method; magic numbers `5` and `15` are repeated (also in the message text); wrong password for a missing admin takes less time than for a real one (timing leak); `change_password` raises 400 with a bare number instead of `status.`; `bootstrap` never updates the password; `ROLE_PERMISSIONS` unknown role gives no error; no tests seen.
- Cleaner way:
```python
MAX_ATTEMPTS, LOCK_MINUTES = 5, 15   # instead of literals in two places
```
and run a dummy `password_hash.verify` when the admin is missing to equalize timing (opinion).
- Security: `jwt_secret_key` must be strong and from settings only, never in git. The lock message reveals that an Admin ID exists (423 vs 401). Consider a rate limit by IP too.

## 7. Check yourself
1. What happens on the 5th wrong password, and what does the admin see on the 6th try within 15 minutes?
2. Why does `change_password` add 1 to `token_version`?
