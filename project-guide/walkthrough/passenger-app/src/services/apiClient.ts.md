# passenger-app/src/services/apiClient.ts

## 1. Purpose
This file builds the one shared HTTP client the passenger app uses to talk to the FastAPI backend. It adds the login token to every request and turns every failure into a clean `ApiError`. Feature files such as `features/booking/data/bookingApi.ts` and `features/auth/services/authService.ts` import it. It reads `config/environment`.

## 2. Imports, one by one
- `import axios, { AxiosError, AxiosHeaders } from 'axios';` (line 1). **axios** (a library that sends HTTP requests. *Example:* `axios.get('/rides')`). `AxiosError` is the error type. `AxiosHeaders` is a helper class for request headers (extra info sent with a request).
- `import AsyncStorage from '@react-native-async-storage/async-storage';` (line 2). **AsyncStorage** (a small key-value store on the phone that survives app restarts. *Example:* `await AsyncStorage.setItem('a','1')`). Used to keep the saved session.
- `import { environment } from '../config/environment';` (line 4). Project config with `apiBaseUrl` and `apiTimeoutMs` (the backend address and the time limit).

## 3. Walk through the code, top to bottom
- Line 6: `PASSENGER_SESSION_KEY = '@cabapp/passenger-session'`. The storage key that holds the session JSON. Exported so `authService` uses the same key.
- Lines 8-16 `class ApiError extends Error`. A custom error with `message` and an optional `status` (HTTP code, like 401). `public readonly status` in the constructor makes it a field automatically. `super(message)` runs the parent `Error` constructor. `this.name = 'ApiError'` labels it. *Example:* `new ApiError('Bad', 400).status` is `400`.
- Lines 18-19 `createRequestId()`: returns text like `passenger-1730000000000-k3j2h1ab`. `Date.now()` is the time in milliseconds. `Math.random().toString(36).slice(2,10)` makes 8 random letters and digits. The backend can log this id to trace a request.
- Lines 21-41 `toApiError(error: unknown): ApiError`:
  1. Not an axios error: "An unexpected connection error occurred."
  2. `code === 'ECONNABORTED'` (the timeout): "The request timed out..."
  3. No `response` (server not reachable): "Unable to reach the backend..."
  4. Otherwise use the server's `detail` (FastAPI's error field), else `message`, else a default text; pass `response.status`.
  `??` means "use the right side if the left is null or undefined".
- Lines 43-46 `apiClient = axios.create({...})`. Makes a client with a base URL and timeout. *Example:* `apiClient.get('/rides')` calls `<apiBaseUrl>/rides`.
- Lines 48-59 **request interceptor** (a function that runs before every request and may change it). It:
  1. Makes `headers` from the current ones (`AxiosHeaders.from`).
  2. Reads the saved session text with `AsyncStorage.getItem`.
  3. In `try`, parses JSON and takes `access_token`. If parsing fails (broken text), `catch` removes the bad saved value.
  4. Sets `Accept: application/json` and `X-Request-ID`.
  5. If a token exists, sets `Authorization: Bearer <token>`. **Bearer token** (a pass the server accepts as proof of login; *Example:* `Authorization: Bearer <secret>`).
  6. Returns the changed `config`.
- Lines 61-68 **response interceptor**. First function passes good responses through. The second handles errors: builds an `ApiError`; if status is 401 (not logged in or token expired) it deletes the saved session; then `Promise.reject(apiError)` throws it to the caller.

## 4. How data flows
```
screen -> bookingApi -> apiClient.get('/x')
  request interceptor: read AsyncStorage -> add Bearer token + X-Request-ID
  -> HTTP -> FastAPI backend
  <- 200: response returned
  <- error: toApiError -> (401: clear session) -> reject ApiError -> screen shows message
```

## 5. Try it
Not directly runnable alone. In a React Native file:
```ts
import { apiClient } from './services/apiClient';
apiClient.get('/health').then(r => console.log(r.status)).catch(e => console.log(e.message, e.status));
```
Expected: `200` if the backend is up; otherwise "Unable to reach the backend..." with `undefined` status. (The `/health` path is an example; check the backend routes.)

## 6. Can it be better?
- Good: one client, clear errors, tracing id, bad stored data is cleaned.
- Weak: it reads storage on every request (small cost). On 401 it deletes the session but does not send the user to Login, so the screen may stay broken. No refresh-token step. `JSON.parse(...).access_token` is not type checked. The request id is not a real UUID. No tests.
- Cleaner way: keep the token in memory after login, and emit an event on 401 so the navigator resets to Login. (Opinion.)
- Security: the token is kept in AsyncStorage, which is not encrypted. A secure store (Keychain or Keystore based) is safer. No secret is written in this file.

## 7. Check yourself
1. Which header carries the login token, and what is the exact format?
2. What happens to the saved session when the server answers 401?
