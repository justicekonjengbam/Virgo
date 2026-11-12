# driver-app/src/types/react-native-config.d.ts

## 1. Purpose
A **declaration file** (`.d.ts`, only describes types, has no running code). The library `react-native-config` ships without types, so this file tells TypeScript what it exports. `config/environment.ts` imports `Config` and relies on this.

## 2. Imports, one by one
None. It uses `declare module`.

## 3. Walk through the code
`declare module 'react-native-config' { ... }` (`react-native-config.d.ts:1-9`) says "a module with this name exists, and it looks like this".
- `const Config: { API_BASE_URL?: string; API_TIMEOUT_MS?: string; WS_BASE_URL?: string; };` (`:2-6`). `Config` holds values read from the app's `.env` file. The `?` means optional (may be `undefined`). All values are strings, even numbers. *Example:* `Config.API_BASE_URL` is `'http://10.0.2.2:8000'` or `undefined`.
- `export default Config;` (`:8`) matches `import Config from 'react-native-config'`.

## 4. How data flows
```
driver-app/.env --(native build)--> react-native-config --types from this file--> environment.ts
```

## 5. Try it
Run `pnpm typecheck` in `driver-app`. Remove this file and the typecheck should complain about the untyped module (I did not run it).

## 6. Can it be better?
- Good: small and accurate for the three keys used.
- Weak: if a new key is added to `.env`, it must be added here by hand.
- Security: `.env` values get compiled into the app, so never put secrets in them.

## 7. Check yourself
1. Why are the three keys marked with `?`
2. What is a `.d.ts` file for?
