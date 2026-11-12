# Passenger authentication API

Base URL: `http://localhost:8000/api/v1/auth/passengers`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/signup` | Creates a password-protected passenger account and issues an OTP. |
| POST | `/otp/request` | Creates a pending passenger for a new valid phone number, then creates a six-digit OTP. |
| POST | `/otp/verify` | Verifies the OTP and returns access and refresh JWTs. |
| POST | `/login` | Password login for a verified passenger. |
| POST | `/refresh` | Rotates an unexpired refresh JWT into a fresh token pair. |

`signup` fields: `full_name`, `phone_number`, `password` (minimum eight characters). OTPs are returned only when `ENVIRONMENT=development`; production must send them through an SMS provider.

Bearer access tokens expire after 15 minutes by default. Refresh tokens expire after 30 days. Configure `JWT_SECRET_KEY`, `ACCESS_TOKEN_MINUTES`, and `REFRESH_TOKEN_DAYS` in `backend/.env` before deployment. Social login is intentionally excluded.
# Firebase phone authentication

The mobile app requests and confirms an SMS OTP through Firebase Authentication, then exchanges the Firebase ID token for CabApp tokens.

- `POST /api/v1/auth/passengers/firebase/signup` accepts `{ "id_token": "...", "full_name": "..." }`, verifies the Firebase phone identity, and creates the Passenger plus Passenger Profile. It returns the CabApp access and refresh token pair.
- `POST /api/v1/auth/passengers/firebase/login/preflight` accepts `{ "phone_number": "..." }`. It permits an OTP request only when an active, verified Passenger exists.
- `POST /api/v1/auth/passengers/firebase/login` accepts `{ "id_token": "..." }`. It verifies the Firebase identity, requires the existing Passenger account, and returns the CabApp access and refresh token pair.

The API never stores Firebase OTPs or raw Firebase tokens.
