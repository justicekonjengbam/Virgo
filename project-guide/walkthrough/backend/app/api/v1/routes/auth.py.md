# backend/app/api/v1/routes/auth.py

## 1. Purpose
Passenger sign-up and login routes. Used by `passenger-app/`. It supports OTP (One Time Password, a short code sent by SMS), password login, token refresh and Firebase login. Mounted at `router.py:19`. Calls `AuthService` in `app/services/auth_service.py`. URLs start with `/api/v1/auth/passengers`.

## 2. Imports, one by one
- `from fastapi import APIRouter, Depends, status` (`auth.py:1`). `APIRouter` groups routes. `Depends` is dependency injection (FastAPI runs a helper and passes the result in). `status` holds named HTTP codes. *Example:* `status.HTTP_201_CREATED == 201`.
- `from sqlalchemy.orm import Session` (`auth.py:2`). SQLAlchemy ORM session type (one conversation with the database). Type hint only.
- `from app.core.config import get_settings` (`auth.py:4`). Returns the app settings read from environment variables. Used to know if we run in `development`.
- `from app.db import get_db` (`auth.py:5`). Dependency that opens and closes a session per request.
- Schemas from `app/schemas/auth.py` (`auth.py:6`): Pydantic classes describing the JSON in and out (`OtpRequest` is a phone number, `TokenResponse` holds tokens, etc.).
- `AuthService` from `app/services/auth_service.py` (`auth.py:7`). The business logic.

## 3. Walk through the code, top to bottom
- `router = APIRouter(prefix='/auth/passengers', tags=['passenger-auth'])` (`auth.py:9`). Shared URL start.
- `service = AuthService()` (`auth.py:10`). One shared service object.

**`signup`** `POST /signup`, status 201 (`auth.py:13-17`). Body `PassengerSignupRequest`. `service.signup` creates the passenger row. `service.request_otp(db, passenger.phone_number)` makes and sends an OTP and returns it. The response includes the code as `development_otp` only when `get_settings().environment == 'development'`; otherwise `None`. *Example:* dev answer `{"message":"Account created...","development_otp":"123456"}`.

**`request_otp`** `POST /otp/request` (`auth.py:20-23`). Same OTP step for an existing phone number. Message `'OTP sent.'`.

**`verify_otp`** `POST /otp/verify` (`auth.py:26-28`). Sends phone and code; the service checks them and returns `TokenResponse` (access and refresh tokens; a **token** is a signed string the app sends back to prove who it is).

**`login`** `POST /login` (`auth.py:31-33`). Phone plus password to tokens.

**`refresh`** `POST /refresh` (`auth.py:36-38`). Trades a refresh token for new tokens. It has no `db` parameter, so the service must work from the token alone.

**`firebase_login`** `POST /firebase/login` (`auth.py:41-43`). **Firebase** is Google's login service. The app logs in with Firebase, gets an `id_token`, and sends it here. The service verifies it with Google and returns our own tokens.

**`firebase_signup`** `POST /firebase/signup`, 201 (`auth.py:46-48`). Same plus `full_name`.

**`firebase_login_preflight`** `POST /firebase/login/preflight`, 204 (`auth.py:51-53`). 204 means "success, no body". It asks the service whether this phone may log in with Firebase; the service raises an error if not (inferred from the name `ensure_..._allowed`; check the service). Returns `None`.

## 4. How data flows
```
passenger-app --POST /otp/verify {phone, otp}--> verify_otp()
   -> AuthService.verify_otp(db, phone, otp) --SQL--> database
   <- TokenResponse {access, refresh}
```

## 5. Try it
```
curl -s -X POST localhost:8000/api/v1/auth/passengers/otp/request \
  -H 'content-type: application/json' -d '{"phone_number":"+10000000000"}'
```
`-X POST` sets the method, `-H` adds a header, `-d` is the body. Expect `{"message":"OTP sent.","development_otp":"..."}` in development, if the number is valid for the schema.

## 6. Can it be better?
- Good: thin routes; OTP leak limited to development.
- Weak: `development_otp` logic is repeated twice; no visible rate limit on OTP or login (abuse risk, SMS cost); `refresh` takes no db so token revocation may be impossible (unverified).
- Cleaner way: a helper `def _dev_otp(otp): return otp if get_settings().environment == 'development' else None`.
- Security: if `environment` is set wrongly in production, OTPs leak in responses. Keep that default safe.

## 7. Check yourself
1. When is `development_otp` filled in?
2. What does status 204 mean and which route uses it?
