# environment.ts

## 1. Purpose
This file reads settings from the `.env` file (server address, timeout, websocket address) and gives the rest of the app one clean object called `environment`. If a setting is missing, it uses a safe default. It sits in `passenger-app/src/config/`. API client and websocket code import `environment` (find them with `rg "config/environment" passenger-app/src`).

## 2. Imports, one by one
- `import Config from 'react-native-config';` (`environment.ts:1`). **react-native-config** is a library that copies values from a `.env` file into the app at build time. *Example:* the line `API_BASE_URL=http://x` in `.env` becomes `Config.API_BASE_URL`. Needed so the server address is not hard-coded. Values are always strings or `undefined`. Note: values are built into the app, so never put real secrets in `.env` (anyone can unpack an app). The repo's `.env` has `API_BASE_URL`, `API_TIMEOUT_MS`, `WS_BASE_URL`; their values are not copied here.

## 3. Walk through the code
- `const DEFAULT_API_BASE_URL = 'http://10.0.2.2:8000';` (`:3`). `10.0.2.2` is the special address the Android emulator uses to reach the computer it runs on. Port 8000 is the FastAPI backend. Used when `API_BASE_URL` is missing.
- `const DEFAULT_API_TIMEOUT_MS = 10_000;` (`:4`). 10 seconds in milliseconds. The `_` is only a reading aid for big numbers.
- `parseTimeout` (`:6-9`): `(value?: string): number`.
  - `Number(value)` turns a string to a number. `Number('5000')` gives `5000`; `Number(undefined)` gives `NaN` (not a number).
  - `Number.isFinite(timeout) && timeout > 0` checks it is a real positive number. If yes, use it; otherwise use the default.
  - Examples: `'5000'` gives 5000; `'abc'` gives 10000; `'-1'` gives 10000.
- `export const environment = {...} as const;` (`:11-15`). `as const` makes the object read-only for TypeScript.
  - `apiBaseUrl` (`:12`): `Config.API_BASE_URL ?? DEFAULT...` (`??` means "use the right side only if the left is null or undefined"), then `.replace(/\/$/, '')` removes one trailing slash. *Example:* `http://a/` becomes `http://a`. This avoids `//` when joining paths.
  - `apiTimeoutMs` (`:13`): result of `parseTimeout`.
  - `wsBaseUrl` (`:14`): use `WS_BASE_URL` if set. Otherwise take the API URL and swap the start `http` to `ws` with `.replace(/^http/, 'ws')`. *Example:* `http://x` becomes `ws://x`, and `https://x` becomes `wss://x` (secure websocket). Then the trailing slash is removed.
  - Gotcha: if `WS_BASE_URL` is set to an empty string, `??` keeps the empty string (only null/undefined fall back).

## 4. How data flows
```
.env --(build time, react-native-config)--> Config.*
Config.* --> environment.ts (defaults, cleanup) --> environment object
API client / websocket code --reads--> environment.apiBaseUrl / wsBaseUrl
```

## 5. Try it
Not directly runnable alone (needs the native module). You can test the idea in node:
```zsh
node -e "const n=Number('abc');console.log(Number.isFinite(n)&&n>0?n:10000)"
```
`node -e` runs the text as code. Expected output: `10000`.
After changing `.env`, rebuild the app (`cd passenger-app && npx react-native run-android`), because values are baked in at build time.

## 6. Can it be better?
- Good: safe defaults, trailing slash cleanup, validated timeout, one place for settings.
- Weak: the `wsBaseUrl` line repeats the default logic and is long; the default is Android-emulator only, so an iPhone simulator or a real phone silently fails; an empty string is not treated as missing; no check that the URL is valid.
- Cleaner way (opinion):
```ts
const apiBaseUrl = (Config.API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '');
wsBaseUrl: (Config.WS_BASE_URL || apiBaseUrl.replace(/^http/, 'ws')).replace(/\/$/, ''),
```
`||` also catches the empty string.
- Security: default is plain `http`. Use `https` in production. Never store secrets in `.env` for a mobile app.

## 7. Check yourself
1. What does `wsBaseUrl` become if only `API_BASE_URL=https://api.example.com/` is set?
2. Why must you rebuild after editing `.env`?
