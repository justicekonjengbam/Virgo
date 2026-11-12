# passenger-app/src/types/react-native-config.d.ts

## 1. Purpose
This file gives TypeScript types for the `react-native-config` library. That library reads values from the `.env` file (settings such as the server address) and exposes them in JavaScript. The file lists the three setting names the passenger app expects. It has no runtime code.

## 2. Imports, one by one
None. It is a global declaration file.

## 3. Walk through the code
`passenger-app/src/types/react-native-config.d.ts:1-9`
```ts
declare module 'react-native-config' {
  const Config: { API_BASE_URL?: string; API_TIMEOUT_MS?: string; WS_BASE_URL?: string; };
  export default Config;
}
```
- **`declare module 'react-native-config'`** (describes the shape of a library that has no types of its own. *Example:* after this, `import Config from 'react-native-config'` is typed.)
- **`API_BASE_URL?`** the REST server address, for example `http://10.0.2.2:8000`. The `?` means optional: it may be `undefined` if `.env` lacks it.
- **`API_TIMEOUT_MS?`** the request time limit. It is a `string`, because every `.env` value is text. Code must convert it with `Number(...)`.
- **`WS_BASE_URL?`** the WebSocket address (a long-lived two-way connection used for realtime updates).
- **`export default Config`** the library's default export is this object.

Errors: because the fields are optional, code that uses them must handle `undefined`, or TypeScript complains.

## 4. How data flows
```
.env file --(build time)--> react-native-config (native code)
                                  |
                      Config.API_BASE_URL in JS
                                  |
              passenger-app code builds HTTP / WebSocket URLs
```

## 5. Try it
Not directly runnable. Check types with `npx tsc --noEmit` inside `passenger-app/`. Use `rg -n "Config\." passenger-app/src` to see where the values are read.

## 6. Can it be better?
- Good: simple and honest that values may be missing.
- Weak: the list must be edited by hand when a new `.env` key is added. A typo in a key name is only caught if it is listed here.
- Cleaner way: keep it, but add a startup check that throws a clear error when `API_BASE_URL` is empty.
- Security: `.env` values go inside the app bundle. Never put secrets there. Anyone can unpack an app.

## 7. Check yourself
1. Why is `API_TIMEOUT_MS` a string and not a number?
2. Why are all three fields marked optional?
