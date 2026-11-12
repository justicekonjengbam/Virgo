# driver-app/src/features/auth/utils/driverAuthError.ts

## 1. Purpose
Many things can fail during driver sign-in: Firebase (the Google phone-OTP service), the network, or the FastAPI backend. Each gives a different error shape. This file turns any error into one plain message the user can read. It is called by `DriverPhoneAuthForm.tsx`, `DriverVehicleVerificationForm.tsx` and `DriverOnboardingScreen.tsx`.

## 2. Imports, one by one
- `import axios from 'axios';` (`driverAuthError.ts:1`) **axios** is an HTTP client library. *Example:* `axios.get(url)` fetches a page. Here only `axios.isAxiosError(error)` is used. It answers "did this error come from an axios request?". It also has `post`, `put`, interceptors, and more.

## 3. Walk through the code
**`readableDetail(value: unknown): string | null`** (lines 3-16)
- Goal: dig a human-readable text out of an unknown value. `unknown` is the TypeScript type for "could be anything, check before use".
- If it is a non-empty string, return it (line 4). *Example:* `"Phone already used"` returns itself.
- If it is an array (line 5), call itself on each item (recursion), keep only real strings (`filter` with a type guard `message is string`), and join with a space. FastAPI validation errors are arrays like `[{msg: "field required"}]`.
- If it is an object (line 9): use `msg` if it is a string (Pydantic style), else follow `detail` recursively, else use `message`.
- Otherwise return `null`.

**`driverAuthError(error: unknown): string`** (lines 19-43)
1. If it is an axios error (line 20):
   - Take `error.response?.data?.detail` or the whole `data`. `?.` means "stop and give undefined if something is missing". If `readableDetail` finds text, show the server's own message (line 21-22).
   - `ECONNABORTED` means the request timed out (line 23).
   - No `response` means the server was never reached (line 24).
   - Then by HTTP status: 401 bad session, 404 no account, 409 duplicate, 500 or more server down (lines 25-28). Else a generic text.
2. Not axios: read `error.code` if the object has one (line 31). Then map Firebase codes such as `auth/invalid-verification-code` to messages (lines 32-40). The `auth/*-timeout` codes are made by `withTimeout` in `driverAuthService.ts:20`.
3. A plain `Error` gives a generic message (line 41, the real message is hidden on purpose). Else "Something went wrong." (line 42).

Example: `driverAuthError({ code: 'auth/session-expired' })` returns `'The OTP has expired. Request a new one.'`.

## 4. How data flows
```
service throws error --> catch in form --> driverAuthError(error)
   axios? -> server detail / status text
   firebase code? -> mapped text
   else generic        --> setMessage(text) --> red text on screen
```

## 5. Try it
Not directly runnable in the app alone. In a TypeScript test or REPL: `driverAuthError({ code: 'auth/too-many-requests' })` returns `'Too many OTP attempts. Please wait and try again.'`.

## 6. Can it be better?
- Good: one place for all messages, handles FastAPI array errors, never shows raw stack text.
- Weak: a long `if` chain for codes (use a lookup table). Line 21 may show raw server text for any status, including 500 pages. Messages are English only. No tests. The same logic probably exists in the passenger app (duplication; I did not check).
- Cleaner way:
```ts
const FIREBASE_MESSAGES: Record<string, string> = { 'auth/invalid-phone-number': 'Enter a valid Indian mobile number.' /* ... */ };
if (code in FIREBASE_MESSAGES) return FIREBASE_MESSAGES[code];
```
- Security: showing the server `detail` is fine only if the backend never leaks internals. Good that unknown `Error` text is hidden.

## 7. Check yourself
1. What message appears if the phone has no internet when calling the backend?
2. Why does `readableDetail` call itself?
