# authService.ts

File: `passenger-app/src/features/auth/services/authService.ts` (90 lines)

## 1. Purpose
This is the one place that does phone login. It asks Firebase to send an SMS code (OTP), checks the code, then trades Firebase's proof for the CabSure backend's own tokens and stores them on the phone. Callers: `LoginScreen.tsx`, `SignupScreen.tsx`, and (not read here) other app code that calls `hasSession`, `clearSession`, `getProfileName`. It calls Firebase, the backend through `apiClient`, and local storage.

## 2. Imports, one by one
```ts
import AsyncStorage from '@react-native-async-storage/async-storage';
```
**AsyncStorage** (a small key-value store on the phone that survives app restarts. *Example:* `await AsyncStorage.setItem('a', '1')` then `await AsyncStorage.getItem('a')` gives `'1'`.) Used here to keep the login session. It can also `removeItem`.
```ts
import auth, { FirebaseAuthTypes } from '@react-native-firebase/auth';
```
**Firebase Auth** (Google's login service. *Example:* `auth().signInWithPhoneNumber('+919876543210')` sends an SMS.) `auth` is the function that gives the auth object. `FirebaseAuthTypes` holds TypeScript types, such as `ConfirmationResult` (an object that remembers a pending SMS check and has `.confirm(code)`).
```ts
import { apiClient } from '../../../services/apiClient';
```
Project file `passenger-app/src/services/apiClient.ts:43`. It is an **axios** instance (an HTTP client library. *Example:* `apiClient.get('/x')`). It has the backend base URL and adds the saved token to each request (apiClient.ts:48-59).

## 3. Walk through the code, top to bottom

### Constants (lines 6-7)
`SESSION_KEY = '@cabapp/passenger-session'` is the storage key for tokens. It equals `PASSENGER_SESSION_KEY` in apiClient.ts:6, so the HTTP client and the realtime service can find the same token. (Duplicated text: see section 6.) `PROFILE_NAME_KEY` stores the name typed at signup.

### Dev-only bypass (lines 12-14)
```ts
if (__DEV__) { auth().settings.appVerificationDisabledForTesting = true; }
```
`__DEV__` is a React Native global that is `true` only in development builds. The setting turns off Android app checks (reCAPTCHA / Play Integrity) so Firebase test numbers work. Release builds skip it.

### Types (lines 16-17)
`AuthSession` is the shape of the backend reply: `access_token`, `refresh_token`, `token_type`. `PhoneAuthIntent` is `'login'` or `'signup'`.

### `withFirebaseTimeout` (lines 19-32)
- **What:** wraps a **Promise** (a value that arrives later. *Example:* `fetch()` returns one) and fails if it takes more than 30 000 ms (`FIREBASE_TIMEOUT_MS`; `30_000` is just 30000 with a readable separator).
- **How:** `new Promise((resolve, reject) => ...)` makes a new promise. `setTimeout` starts a 30 s timer that rejects with an Error that also has a `code`. `operation.then(ok, fail)` clears the timer when the real operation finishes first, then passes the result on.
- **Why:** Firebase on Android can hang without an answer (see comment lines 39-40).
- `<T>` is a generic: the result has the same type as the input promise.
- Example: `withFirebaseTimeout(auth().signOut(), 'auth/x', 'msg')`.

### `authService.requestOtp(phoneNumber, intent)` (lines 35-53)
1. If `intent` is login, `apiClient.post('/api/v1/auth/passengers/firebase/login/preflight', { phone_number })` asks the backend if this number is registered (HTTP POST sends data). If the backend says no, an `ApiError` is thrown and no SMS is sent.
2. If a Firebase user is still signed in (`auth().currentUser`), sign out first (lines 41-47).
3. `auth().signInWithPhoneNumber('+91' + phone)` asks Firebase to send the SMS. It returns a `ConfirmationResult`. The `+91` is the India country code.
- Output example: a confirmation object you pass to `verifyOtp`.
- Errors: Firebase errors (`auth/invalid-phone-number`...), `ApiError`, or timeout errors with codes `auth/session-reset-timeout` and `auth/otp-request-timeout`.

### `authService.verifyOtp(confirmation, otp, intent, fullName?)` (lines 54-77)
1. `confirmation.confirm(otp)` checks the code with Firebase (30 s limit). It returns a credential with `.user`.
2. If there is no user, throw an Error (line 60-62).
3. `user.getIdToken(true)` asks Firebase for an **ID token** (a signed proof of who the user is, a JWT = JSON Web Token). `true` forces a fresh one.
4. Pick the route: signup or login (line 69). POST `{ id_token, full_name }` to the backend. The backend checks the token and returns CabSure tokens.
5. Save the reply with `AsyncStorage.setItem(SESSION_KEY, JSON.stringify(response.data))`. `JSON.stringify` turns an object into text because storage keeps only strings.
6. If the backend call fails, `catch` signs out of Firebase and rethrows the error (lines 73-76), so the user is not half logged in.

### `clearSession` (78-81), `hasSession` (82-87)
`clearSession` deletes the token and signs out of Firebase. `hasSession` reads the saved text, parses it, and returns `true` when `access_token` is set. If the text is broken JSON, it removes it and returns `false`. `Boolean(x)` turns a value into true/false.

### `saveProfileName` / `getProfileName` (88-89)
Save or read the trimmed name under `PROFILE_NAME_KEY`.

## 4. How data flows
```
LoginScreen --requestOtp--> authService --POST preflight--> Backend
                                  \--signInWithPhoneNumber--> Firebase --SMS--> phone
user types code --> verifyOtp --confirm--> Firebase --> ID token
                        --POST firebase/login--> Backend --> {access_token, refresh_token}
                        --> AsyncStorage (SESSION_KEY) --> later requests add "Authorization: Bearer ..."
```

## 5. Try it
Not directly runnable (needs the phone app, Firebase and the backend). To see it work: start the backend, run the app with a Firebase test number, then in app code log `await authService.hasSession()` after login. It should print `true`.

## 6. Can it be better?
- Good: timeouts on every Firebase step; Firebase sign-out on failure; dev bypass limited to `__DEV__`.
- Weak: `SESSION_KEY` repeats `PASSENGER_SESSION_KEY` from apiClient.ts:6 (import it instead). The refresh token is stored in plain AsyncStorage. `fullName` is `undefined` on login and sent anyway. No tests.
- Cleaner way:
```ts
// before
const SESSION_KEY = '@cabapp/passenger-session';
// after
import { PASSENGER_SESSION_KEY as SESSION_KEY } from '../../../services/apiClient';
```
- Security: AsyncStorage is not encrypted. Opinion: for tokens, use Keychain/Keystore storage (for example `react-native-keychain`). Never log the ID token.

## 7. Check yourself
1. Why does `verifyOtp` sign out of Firebase when the backend call fails?
2. What does `withFirebaseTimeout` do when the operation finishes in 2 seconds?
