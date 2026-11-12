# backend/app/services/auth_service.py

## 1. Purpose
This file holds all passenger login logic. It signs people up, sends and checks one-time codes, checks passwords, checks Firebase phone tokens, and makes JWT tokens (JSON Web Token: a signed text string that proves who you are. *Example:* `eyJhbGci...`). It sits in the "service" layer: the API route files (in `backend/app/api/`) call `AuthService`, and `AuthService` calls `PassengerRepository` (database access), `firebase_service.py` (Firebase start-up), and `config.py` (settings). I am not sure of the exact route file names; check with `rg "AuthService" backend/app -g '*.py'`.

## 2. Imports, one by one

### Standard library
- `import secrets` (`auth_service.py:1`). **secrets** is Python's module for safe random values. *Example:* `secrets.token_urlsafe(32)` gives a long random text. Used here for random OTPs (OTP = One-Time Password, a short code sent by SMS) and for random throw-away passwords. It can also do `secrets.compare_digest(a, b)` for safe string compare.
- `import logging` (`:2`). Python's log writer. *Example:* `logger.warning("hi")` prints a warning line. Used to record Firebase failures.
- `from datetime import UTC, datetime, timedelta` (`:3`). `datetime` is a date and time value, `UTC` is the world time zone with no offset, `timedelta` is a length of time. *Example:* `datetime.now(UTC) + timedelta(minutes=5)` is "five minutes from now". Used for OTP expiry and token expiry.

### Third-party
- `import jwt` (`:5`). This is the **PyJWT** library. It makes and reads JWT tokens. *Example:* `jwt.encode({'sub': '1'}, 'key', algorithm='HS256')` returns a token string.
- `from fastapi import HTTPException, status` (`:6`). **FastAPI** is the web framework. `HTTPException` is an error that FastAPI turns into an HTTP error answer. `status` holds named codes. *Example:* `raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='x')` sends a 404 with a message.
- `from firebase_admin import auth as firebase_auth` (`:7`). **Firebase Admin** is Google's server library. Its `auth` part can check ID tokens made by the phone app. It is renamed `firebase_auth` to avoid confusion with other "auth" names.
- `from pwdlib import PasswordHash` (`:8`). **pwdlib** hashes passwords. A hash is a one-way scramble. *Example:* `h = ph.hash('abc')` then `ph.verify('abc', h)` is `True`.
- `from sqlalchemy.orm import Session` (`:9`). **SQLAlchemy** is the database toolkit (ORM = Object Relational Mapper: it lets you use Python classes instead of SQL text). `Session` is one open conversation with the database. Here it is only used as a type hint.

### Project
- `from app.core.config import get_settings` (`:11`) from `backend/app/core/config.py`. Returns the settings object (token lifetimes, secret key).
- `from app.models.user import Passenger` (`:12`) from `backend/app/models/user.py`. The Passenger database table class.
- `from app.repositories.passenger_repository import PassengerRepository` (`:13`). The class that runs the database queries for passengers.
- `from app.schemas.auth import PassengerSignupRequest, TokenResponse` (`:14`). Pydantic shapes (checked data shapes) for the request body and the token answer.
- `from app.services.firebase_service import initialize_firebase` (`:15`). Starts the Firebase library once (see `firebase_service.py.md`).

## 3. Walk through the code

### Module constants (`:17-18`)
`password_hash = PasswordHash.recommended()` builds one hasher with the library's recommended settings (Argon2 in current pwdlib; I am not fully sure, check the pwdlib docs). `logger = logging.getLogger(__name__)` makes a logger named after this module.

### `class AuthService` (`:21`)
**What it is:** a bundle of methods for passenger login.

**`__init__(self, repository=None)`** (`:22-24`). `repository or PassengerRepository()` means "use the one given, else make a new one". This is **dependency injection** (you pass in what a class needs, so a test can pass a fake). It also stores `self.settings = get_settings()`.

**`signup(db, request)`** (`:26-29`). Input: a database session and a signup request. Output: a new `Passenger`.
1. `self.repository.get_by_phone(db, phone)` looks for a row with this phone. If found, raise 409 (Conflict: "already exists") at `:28`.
2. Otherwise `self.repository.create(db, Passenger(...))` saves a new row. The password is stored as `password_hash.hash(request.password)`, never as plain text.
*Example:* phone `9876543210` twice: first call returns a Passenger, second raises 409.

**`request_otp(db, phone_number)`** (`:31-48`). Makes a 6-digit code.
- If no passenger has this phone, it creates a "pending" one with a random password (`secrets.token_urlsafe(32)`) so the account has a valid hash (`:33-43`).
- `secrets.randbelow(1_000_000)` gives a number 0 to 999999. `f'{n:06d}'` pads it to 6 digits: `42` becomes `000042` (`:44`).
- It stores only the **hash** of the OTP in `otp_hash` and the expiry in `otp_expires_at` (`:45-46`), then `self.repository.save(db, passenger)` commits.
- It returns the plain OTP so the caller can send it by SMS.

**`verify_otp(db, phone_number, otp)`** (`:50-58`). Looks up the passenger with `_get_passenger`. The long `if` at `:52` raises 400 when: no hash, no expiry, expired, or the code does not match (`password_hash.verify(otp, hash)` compares). On success it marks the phone verified, clears the OTP fields, saves, and returns tokens. Clearing makes the code single-use.

**`login(db, phone_number, password)`** (`:60-66`). Checks password (401 if wrong), then checks phone is verified (403 Forbidden if not), then returns tokens.

**`refresh(refresh_token)`** (`:68-71`). `_decode(token, 'refresh')` checks the token. Then it builds a fake `Passenger(id=..., ...)` with empty strings only to reuse `_tokens`. It does not touch the database, so a deleted passenger can still refresh. (See "Weak" below.)

**`firebase_login(db, id_token, full_name=None)`** (`:73-82`). **Firebase ID token** (a signed proof from Google that the phone number was verified by SMS). `_verified_firebase_identity` returns `(uid, phone)`. It finds the passenger by Firebase uid or by verified phone. If none: 404. Else it saves the uid, sets `is_phone_verified`, sets `last_login_at`, and returns tokens. The `full_name` argument is unused.

**`firebase_signup(db, id_token, full_name)`** (`:84-99`). Same identity check, but if an account exists it raises 409. Else it creates a passenger with name (`full_name.strip()` or `'Passenger'`), a random password hash, verified phone. Then `self.repository.create_profile(db, passenger.id)` makes the profile row. Returns tokens.

**`ensure_firebase_login_allowed(db, phone_number)`** (`:101-103`). Raises 404 if no verified account has this phone. Used before the app asks Firebase to send an SMS, so unknown numbers are stopped early.

**`_verified_firebase_identity(id_token)`** (`:105-126`). Private helper (the leading `_` means "internal").
- `initialize_firebase()` makes sure Firebase is ready.
- `firebase_auth.verify_id_token(id_token, clock_skew_seconds=60)` checks the signature and expiry with Google. `clock_skew_seconds=60` allows a 60-second clock difference between phone and server.
- Any error is caught with `except Exception as error`. The class name is used to pick a friendly message (`:112-119`) and a 401 is raised `from error` (keeps the original cause).
- `decoded.get('uid')` and `decoded.get('phone_number')` read the token content. If either is missing, 400 (`:124-125`).
- The phone is cleaned to digits only: `''.join(c for c in phone if c.isdigit())`. `+91 98765 43210` becomes `919876543210`.

**`_tokens(passenger)`** (`:128-129`). Builds a `TokenResponse` with an access token (short life, minutes) and a refresh token (long life, days).

**`_encode(passenger_id, token_type, expires_in)`** (`:131-132`). `jwt.encode(payload, secret, algorithm=...)` makes the token. The payload has `sub` (subject: whose token), `type` ('access' or 'refresh'), `exp` (expiry). The secret is `<secret>` from settings.

**`_decode(token, token_type)`** (`:134-141`). `jwt.decode(..., algorithms=[...])` checks the signature and expiry. If `type` is not the one expected, `raise ValueError`. Both `jwt.PyJWTError` and `ValueError` become a 401. Always passing `algorithms=[...]` is correct and prevents algorithm tricks.

**`_get_passenger(db, phone_number)`** (`:143-147`). Gets a passenger or raises 404.

## 4. How data flows
```
Phone app --(id_token)--> API route --> AuthService.firebase_login
                                          |-> initialize_firebase()
                                          |-> firebase_auth.verify_id_token --> Google
                                          |-> PassengerRepository.get_by_firebase_uid --> DB
                                          |-> save(passenger)
                                          '-> _tokens -> jwt.encode
API route <-- TokenResponse(access, refresh) <--'
```

## 5. Try it
Not directly runnable (needs a database and settings). A small piece you can run:
```bash
cd backend && uv run python -c "from pwdlib import PasswordHash; p=PasswordHash.recommended(); h=p.hash('123456'); print(p.verify('123456', h), p.verify('000000', h))"
```
Expected: `True False`. `uv run python -c` runs one line of Python. `p.hash` scrambles, `p.verify` checks.

## 6. Can it be better?
- **Good:** OTP and passwords are hashed. Tokens carry a type, so a refresh token cannot be used as an access token. Firebase errors are mapped to clear messages.
- **Weak:**
  - The firebase error handling block is copied in `driver_auth_service.py` (see that file). One shared function would remove duplication.
  - `refresh` (`:68-71`) never checks the database, so a banned or deleted passenger keeps getting tokens. The driver version does check.
  - `_decode` always says "Invalid refresh token." (`:141`) even for other uses.
  - OTP has no attempt limit, so a 6-digit code (1 million values) can be guessed in 5 minutes by a fast script. Add a counter.
  - `datetime.now(UTC) > passenger.otp_expires_at` can fail if the database returns a naive datetime (no time zone). Check by running a test.
  - `firebase_login` has an unused `full_name` parameter.
  - Big one-line statements (`:29`, `:52`, `:129`) are hard to read.
- **Cleaner way:**
```python
# before (:52): one long if
# after
def _otp_ok(p, otp):
    return bool(p.otp_hash and p.otp_expires_at and p.otp_expires_at >= datetime.now(UTC) and password_hash.verify(otp, p.otp_hash))
```
- **Security:** `request_otp` returns the OTP to the caller; make sure the route never returns it to the client in production. Keep `jwt_secret_key` out of git (`<secret>`).

## 7. Check yourself
1. Why does `request_otp` store `password_hash.hash(otp)` and not the OTP itself?
2. What is the difference between the access token and the refresh token in `_tokens`, and which check in `_decode` keeps them apart?
