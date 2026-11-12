# driver-app/src/features/auth/services/driverAuthService.ts

## 1. Purpose
This is the one place where the driver app talks to Firebase (phone OTP = one-time password sent by SMS) and to the CabSure backend for sign-in, sign-up and session saving. Screens and forms never call Firebase or axios directly for auth. They call `driverAuthService`. Callers: `DriverPhoneAuthForm.tsx`, `DriverVehicleVerificationForm.tsx`, `DriverOnboardingScreen.tsx`, and probably the app start code and navigator. It calls `services/apiClient.ts`.

## 2. Imports, one by one
**Third-party**
- `import AsyncStorage from '@react-native-async-storage/async-storage';` (line 1) **AsyncStorage** is a simple key-value store on the phone that survives app restarts. *Example:* `await AsyncStorage.setItem('k','v')`, later `getItem('k')` returns `'v'`. Used here to keep the login session. It stores text only.
- `import auth, { type FirebaseAuthTypes } from '@react-native-firebase/auth';` (line 2) **Firebase Auth** is Google's login service. `auth()` returns the auth object. *Example:* `auth().currentUser` is the signed-in user or `null`. `FirebaseAuthTypes` gives TypeScript types (the `type` keyword means it is removed at build time). It also supports email login, Google login and more.

**Project**
- `import { apiClient, DRIVER_SESSION_KEY } from '../../../services/apiClient';` (line 4) `apiClient` is a pre-configured axios instance (base URL, token header). `DRIVER_SESSION_KEY` is the storage key `'@cabsure/driver-session'` (`apiClient.ts:6`).

## 3. Walk through the code
**Types** (lines 6-10). `DriverProfile` is the driver data from the backend. `DriverSession` is access token + refresh token + driver. (A **token** is a text pass that proves who you are. *Example:* `Authorization: Bearer abc`.) `DriverAuthIntent` is `'login'` or `'signup'`. `DriverRegistrationIdentity` is what we keep after the phone is verified but before the vehicle form is done. `DriverRegistrationPayload` is the vehicle and document fields sent to the backend (snake_case because the backend uses it).

**`OTP_REQUEST_TIMEOUT_MS = 30_000`** (line 12): 30 seconds.

**Dev-only block** (lines 16-18): `__DEV__` is a React Native global that is `true` only in debug builds. It sets `appVerificationDisabledForTesting = true`, which lets Firebase test phone numbers work on an emulator. Release builds skip it.

**`withTimeout(operation, code, message)`** (lines 20-25). Wraps a promise (a value that arrives later) so it fails after 30 seconds. It makes a `new Promise`, starts `setTimeout` to reject with an Error that has a custom `code`, and when the real operation ends it cancels the timer (`clearTimeout`) and passes the result on. *Example:* `await withTimeout(fetchSomething())` rejects with `code: 'auth/otp-request-timeout'` if slow. Used to produce the codes that `driverAuthError.ts` maps.

**`isDriverSession(value)`** (lines 27-31). A **type guard**: it checks at runtime that stored JSON really looks like a session (has string tokens and a driver object). Returns `true` or `false`.

**`saveSession(session)`** (lines 33-36). `JSON.stringify` turns the object into text, `AsyncStorage.setItem` saves it, then it returns the session.

**`driverAuthService`** (lines 39-118), an object of methods:
- `resetPhoneChallenge()` (40-44): if a Firebase user exists, `signOut()` so the next OTP is fresh.
- `requestOtp(phoneNumber)` (46-51): signs out any old user (with timeout), then `auth().signInWithPhoneNumber('+91'+number)` asks Firebase to SMS an OTP. Returns a `ConfirmationResult` that is later used to confirm the code. The `+91` is the India country code.
- `verifyOtp(confirmation, otp, intent, fullName?)` (53-67): `confirmation.confirm(otp)` checks the code with Firebase. Then `getIdToken(true)` asks for a fresh Firebase ID token (`true` forces refresh). It posts the token to `/api/v1/auth/drivers/firebase/login` or `/signup` (line 61), saves the returned session, and on backend failure signs out of Firebase and rethrows (lines 63-66). Throws plain `Error`s if Firebase returns no user or token.
- `verifySignupPhone(...)` (69-77): same confirm and token steps, but it does NOT call the backend. It returns `{ idToken, fullName, phoneNumber }` so the vehicle form can finish later.
- `getSession()` (79-88): reads storage, parses JSON, validates with `isDriverSession`. If missing returns `null`. If broken, removes it and returns `null`. The empty `catch` has a comment explaining that cleanup happens below.
- `refreshSession()` (90-100): posts the saved `refresh_token` to `/api/v1/auth/drivers/refresh`, saves the new session. On any error it clears the session and returns `null`. `this` is the service object.
- `completeRegistration(identity, payload)` (102-105): posts the Firebase token, name and all vehicle/document fields to `/firebase/register`, saves the session.
- `completeOnboarding(payload)` (107-112): posts vehicle fields to `/onboarding` (needs login token, added by `apiClient`), then merges the new `driver` into the saved session. Throws if no session.
- `clearSession()` (114-117): removes the saved session and signs out of Firebase. This is the logout.

## 4. How data flows
```
Form --phone--> requestOtp --> Firebase --SMS--> phone
Form --otp----> verifyOtp --> Firebase confirm --> idToken
     idToken --POST--> apiClient --> FastAPI /auth/drivers/firebase/login
     <-- DriverSession --> AsyncStorage (saveSession) --> screen
```

## 5. Try it
Not directly runnable alone (needs a device with Firebase). With the app running on an emulator, enter a Firebase console test number and its fixed code. Check saved session in a debugger: `AsyncStorage.getItem('@cabsure/driver-session')`.

## 6. Can it be better?
- Good: single boundary, timeouts, validated storage, clean-up on failure, clear doc comment.
- Weak: `verifyOtp` and `verifySignupPhone` repeat the same confirm/token code (lines 54-57 and 70-73). Payload type is copied in `completeOnboarding` (line 107) instead of reusing a type. Tokens are in AsyncStorage, which is not encrypted. `withTimeout` leaves the original operation running after timeout. Only `'bearer'` type is assumed. No tests.
- Cleaner way:
```ts
async function confirmAndGetToken(c: FirebaseAuthTypes.ConfirmationResult, otp: string) { /* shared steps */ }
```
- Security: store tokens in a secure keystore (for example `react-native-keychain`) instead of AsyncStorage (opinion, standard advice). The dev flag at line 16 is guarded by `__DEV__`, which is good. Never log `idToken`.

## 7. Check yourself
1. What is the difference between `verifyOtp` and `verifySignupPhone`?
2. Why does `verifyOtp` sign out of Firebase when the backend call fails?
