# driver-app/src/config/environment.ts

## 1. Purpose
This file holds the app settings that change between machines: the backend HTTP address, a request timeout, and the WebSocket address. Other files import `environment` instead of writing URLs themselves (for example `services/apiClient.ts`).

## 2. Imports, one by one
- `import Config from 'react-native-config';` (`environment.ts:1`) **react-native-config** is a library that reads values from a `.env` file at build time and gives them to JavaScript. *Example:* `.env` has `API_BASE_URL=http://192.168.1.5:8000`, then `Config.API_BASE_URL` is that text. It can read any other `.env` key. Values are `undefined` when the key is missing.

## 3. Walk through the code
**`DEFAULT_API_BASE_URL = 'http://10.0.2.2:8000'`** (`environment.ts:3`) The fallback address. On the Android emulator, `10.0.2.2` means "the computer that runs the emulator". Port 8000 is where FastAPI listens.

**`environment`** (`environment.ts:5-9`), an object with three fields:
- `apiBaseUrl` (line 6): `Config.API_BASE_URL ?? DEFAULT_API_BASE_URL` means "use the env value, or the default if it is `undefined` or `null`" (`??` is the nullish operator). `.replace(/\/$/, '')` removes one trailing slash. *Example:* `http://x:8000/` becomes `http://x:8000`. The regex `/\/$/` means "a slash at the end".
- `apiTimeoutMs` (line 7): `10_000` is 10000 (underscore is only for reading). Requests give up after 10 seconds.
- `wsBaseUrl` (line 8): uses `Config.WS_BASE_URL` if set. Otherwise it takes the API URL and changes `http` at the start to `ws` (`/^http/`). *Example:* `http://a` becomes `ws://a`, and `https://a` becomes `wss://a` (secure WebSocket). Then it removes a trailing slash.
- `as const` (line 9) makes the object read-only for TypeScript and keeps exact types.

Errors: none thrown. A bad value just gives a bad URL.

## 4. How data flows
```
.env file --build time--> react-native-config --> Config.API_BASE_URL
                                                      |
                              environment.apiBaseUrl <-+ (trim slash)
                                         |
                                  apiClient (axios) --> backend
```

## 5. Try it
Not directly runnable alone. To change the backend address create `driver-app/.env` with `API_BASE_URL=http://192.168.1.5:8000`, then rebuild the app (`npx react-native run-android`). A rebuild is needed because values are baked in at build time.

## 6. Can it be better?
- Good: safe default for the emulator, trailing slash handled, WebSocket address derived automatically.
- Weak: the default expression `Config.API_BASE_URL ?? DEFAULT_API_BASE_URL` is written twice (lines 6 and 8). A real phone cannot use `10.0.2.2`. No check that the URL is valid.
- Cleaner way:
```ts
const api = (Config.API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, '');
export const environment = { apiBaseUrl: api, wsBaseUrl: (Config.WS_BASE_URL ?? api.replace(/^http/, 'ws')).replace(/\/$/, ''), apiTimeoutMs: 10_000 } as const;
```
- Security: plain `http` is fine for local dev, but production must use `https`. Never put secrets in `.env` for a mobile app, because anyone can read them from the app.

## 7. Check yourself
1. What does `wsBaseUrl` become if only `API_BASE_URL=https://api.cabsure.app/` is set?
2. Why is `10.0.2.2` used instead of `localhost`?
