# docs/authentication-api.md

## 1. Purpose
This is a plain Markdown document. It tells a developer how the passenger login API works: which URLs exist, what to send, and how long tokens live. It sits in `docs/` and is read by humans only. No code imports it. The real code is in the backend auth routes (see `backend/app`).

## 2. Imports, one by one
None. A Markdown file has no imports. **Markdown** (a simple text format where `#` makes a heading and `|` makes a table. *Example:* `# Title` becomes a big title).

## 3. Walk through the document, top to bottom

**Base URL** (`docs/authentication-api.md:3`). `http://localhost:8000/api/v1/auth/passengers`. **localhost** (your own computer). Port `8000` is where the FastAPI server listens. Every path in the table is added after this URL. *Example:* `/login` means `http://localhost:8000/api/v1/auth/passengers/login`.

**Endpoint table** (lines 7-13). **Endpoint** (one URL the server answers. *Example:* `POST /login`). **POST** (an HTTP method that sends data to the server).
- `/signup` (line 9): makes an account with a password and issues an **OTP** (One-Time Password, a short code sent by SMS. *Example:* `482913`).
- `/otp/request` (line 10): for a new valid phone number, makes a "pending" passenger and a six-digit OTP.
- `/otp/verify` (line 11): checks the OTP. Returns an access token and a refresh token. **JWT** (JSON Web Token, a signed text string that proves who you are. *Example:* `eyJhbGciOi...`).
- `/login` (line 12): password login. Only for a verified passenger.
- `/refresh` (line 13): swaps an unexpired refresh token for a fresh pair of tokens. "Rotates" means the old one is replaced.

**Fields and OTP rule** (line 15). `signup` needs `full_name`, `phone_number`, `password` (at least eight characters). The OTP is returned in the response only when `ENVIRONMENT=development`. In production the OTP must go by an **SMS provider** (a paid service that sends text messages).

**Token lifetime** (line 17). The access token lives 15 minutes by default. The refresh token lives 30 days. You set `JWT_SECRET_KEY` (the key that signs tokens), `ACCESS_TOKEN_MINUTES`, `REFRESH_TOKEN_DAYS` in `backend/.env`. Never commit the real secret: write `<secret>`. "Social login is intentionally excluded" means no Google or Facebook login.

**Firebase section** (lines 18-26). Note: the `# Firebase phone authentication` heading at line 18 sits directly after line 17 with no blank line. Markdown still renders it. **Firebase Authentication** (Google's service that sends the SMS and checks the code. *Example:* the phone app asks Firebase for an SMS, the user types the code).
Flow: the app gets a Firebase **ID token** (proof from Firebase that the phone number is real), then sends it to our API, which gives back our own access and refresh tokens.
- `firebase/signup` (line 22): body `{ "id_token": "...", "full_name": "..." }`. Creates Passenger plus Passenger Profile.
- `firebase/login/preflight` (line 23): body `{ "phone_number": "..." }`. Allows an OTP request only if an active, verified passenger exists.
- `firebase/login` (line 24): body `{ "id_token": "..." }`. Requires an existing account.
- Line 26: the API never stores Firebase OTPs or raw Firebase tokens.

## 4. How data flows
```
Phone app --phone number--> Firebase --SMS code--> user
Phone app --code--> Firebase --id_token--> Phone app
Phone app --POST /firebase/login {id_token}--> CabSure API
CabSure API --verify token with Firebase--> account lookup
CabSure API --access JWT + refresh JWT--> Phone app
```

## 5. Try it
Not directly runnable. To test the password flow with the backend running:
```zsh
curl -s -X POST http://localhost:8000/api/v1/auth/passengers/login -H 'Content-Type: application/json' -d '{"phone_number":"+911234567890","password":"<secret>"}'
```
`curl -s` sends an HTTP request quietly. `-X POST` picks the method. `-H` adds a header saying the body is JSON. `-d` is the body. Expected: JSON with access and refresh tokens, or an error message. The exact body field names for `/login` are not given here; check the backend schema.

## 6. Can it be better?
- Good: short, has a table, states token lifetimes, says no OTPs are stored.
- Weak: no example request or response bodies. `/login` and `/otp/*` fields are not listed. Missing blank line before line 18 heading. It looks like two documents joined together. No error codes listed.
- Cleaner way: split into "Password auth" and "Firebase auth" files, or add a blank line and a request/response example per endpoint. FastAPI already serves live docs at `/docs`, which is the better source of truth.
- Security: good that secrets are only named, not shown. Make sure `ENVIRONMENT=development` is never set in production, or OTPs leak in responses.

## 7. Check yourself
1. Why does the Firebase flow need two steps (Firebase, then our API)?
2. When is an OTP returned in the API response, and why must that not happen in production?
