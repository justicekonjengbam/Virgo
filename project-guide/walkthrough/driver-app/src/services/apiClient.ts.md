# driver-app/src/services/apiClient.ts

## 1. Purpose
This file makes the one HTTP client every Driver API call uses. It adds the login token to each request, and when the server says "401 token expired" it gets a new token and retries once. Feature services (for example the ride and auth services under `driver-app/src/features/`) import `apiClient`. It reads `config/environment.ts` and the saved session.

## 2. Imports, one by one
- `import AsyncStorage from '@react-native-async-storage/async-storage';` (`apiClient.ts:1`). **AsyncStorage** (a small key-value store on the phone that survives app restarts. *Example:* `await AsyncStorage.setItem('a','1')`). Used to keep the login session. It can also `removeItem` and `getItem`.
- `import axios, { AxiosHeaders, type InternalAxiosRequestConfig } from 'axios';` (`:2`). **Axios** (a library for HTTP requests. *Example:* `axios.get(url)` returns the reply). `AxiosHeaders` is a helper class to build headers safely. `InternalAxiosRequestConfig` is a type for the request settings object.
- `import { environment } from '../config/environment';` (`:4`). Project file `driver-app/src/config/environment.ts`. It gives `apiBaseUrl` (server address) and `apiTimeoutMs` (10 000 ms = 10 seconds, `environment.ts:7`).

## 3. Walk through the code

**`DRIVER_SESSION_KEY = '@cabsure/driver-session'`** (`:6`). The storage key name for the saved session. Exported so other files read the same key.

**Types** (`:7-8`). `StoredSession` has `access_token` (short-lived pass), `refresh_token` (long-lived pass used to get a new access token) and any other fields. `RetryConfig` adds a flag `_retriedAfterRefresh` to a request, so we retry only once.

**`let refreshPromise`** (`:9`). A shared variable. While a refresh is running, it holds the **Promise** (a value that will arrive later. *Example:* `fetch()` returns one). If five requests fail at once, all five share one refresh call instead of making five.

**`refreshAccessToken()`** (`:11-29`). Input: none. Output: a new access token string, or `null`.
1. If a refresh is already running, return it (`:12`).
2. Otherwise start one (`:13`): read the saved JSON (`:14`); if empty return `null`.
3. Parse it (`JSON.parse` turns text into an object, `:17`). No refresh token gives `null`.
4. `axios.post(.../api/v1/auth/drivers/refresh, { refresh_token }, { timeout })` (`:19`) asks the backend for new tokens. It uses plain `axios`, not `apiClient`, so no interceptor loops.
5. Merge the reply over the old session (`{ ...session, ...response.data }`, `:20`; the spread `...` copies fields, later ones win), save it (`:21`), return the new token.
6. On any error, delete the session (the driver must log in again) and return `null` (`:23-25`).
7. `.finally(() => { refreshPromise = null; })` (`:27`) clears the shared variable when done, success or fail.

**`export const apiClient = axios.create({ baseURL, timeout })`** (`:31-34`). Makes a client with a default server address and timeout. *Example:* `apiClient.get('/api/v1/drivers/me')` calls `<base>/api/v1/drivers/me`.

**Request interceptor** (`:36-49`). An **interceptor** (a function that runs on every request or response, like a checkpoint). Here, before each request:
- Build headers (`:37`), read the session (`:38`).
- If an access token exists, set `Authorization: Bearer <token>` (`:41`). **Bearer** means "whoever holds this token is allowed in".
- If the stored text is broken JSON, remove it (`:42-44`).
- Set `Accept: application/json` (`:45`) and `X-Request-ID` (`:46`): `driver-<time>-<random>`, an id to find one request in server logs. Example: `driver-1760000000000-k3j9x2ab`.
- Return the changed config.

**Response interceptor** (`:51-69`). Success passes through (`:52`). On error (`:53`): if it is an Axios error with status 401, a config exists, it was not retried yet, and the URL is not the refresh URL (`:54-56`), then mark it retried, call `refreshAccessToken()`, and if a token came back, set the new header and call `apiClient.request(config)` again (`:57-63`). Otherwise `Promise.reject(error)` (`:67`) passes the error to the caller.

## 4. How data flows
```
screen -> apiClient.get(url)
   request interceptor: add Bearer token
   -> backend
   <- 401 (token expired)
   response interceptor -> refreshAccessToken() -> POST /auth/drivers/refresh
   -> save new tokens -> retry original request -> result
   (refresh fails -> session deleted -> error to caller)
```

## 5. Try it
Not directly runnable (needs React Native storage). In the app, log in as a driver, wait for the token to expire (or shorten it in the backend), and open the dashboard. Metro logs show one extra refresh call and the request still succeeds.

## 6. Can it be better?
- Good: shared single refresh, one retry only, no loop on the refresh URL, request ids.
- Weak: when refresh fails the session is deleted but the app is not told to go to Login; the next screen action just fails (I am not sure the screens listen; check). Tokens are in AsyncStorage, which is not encrypted. The file does not handle `error.config.url` being absolute. A mirror file probably exists in passenger-app (duplication, opinion).
- Cleaner: an `onSessionExpired` callback that navigates to Login. Use `react-native-keychain` for tokens.
- Security: AsyncStorage tokens can be read on a rooted phone. Tokens are never logged here (good).

## 7. Check yourself
1. Why do five failed requests cause only one refresh call?
2. Why does `refreshAccessToken` use `axios.post` and not `apiClient.post`?
