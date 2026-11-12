# driver-app/package.json

## 1. Purpose
`package.json` is the identity card of a JavaScript project. It lists the name, the commands (`scripts`) and every library (`dependencies`). **pnpm** (a package manager: a tool that downloads libraries. *Example:* `pnpm install`) reads it. The Driver app is the React Native app for drivers. The root `package.json` runs this one through `pnpm --filter driver-app` (see `package.json:6`).

## 2. Imports, one by one
JSON has no imports. The `dependencies` block (below) plays that role.

## 3. Walk through the code, top to bottom
- `"name": "driver-app"`, `"version": "0.1.0"` (`driver-app/package.json:2-3`). Name used by `pnpm --filter driver-app`. `"private": true` (line 4) blocks accidental publishing to the npm registry.
- `scripts` (lines 5-15). Run with `pnpm <name>`. *Example:* `pnpm lint`.
  - `start`: `react-native start` starts Metro, the bundler (see `metro.config.js`).
  - `start:reset`: same with `--reset-cache` (throw away the old bundler cache).
  - `android` (line 8): `set "GRADLE_USER_HOME=C:\tmp\cabsure-gradle"&& react-native run-android --port 8082 --no-packager`. This is a Windows CMD command. `set` makes an environment variable that tells Gradle (the Android build tool) where its cache lives. `--port 8082` means the app looks for Metro on port 8082. `--no-packager` means "do not start Metro, I started it myself". It will not work in zsh on Arch. On Linux you would write `GRADLE_USER_HOME=/tmp/gradle react-native run-android --port 8082 --no-packager`.
  - `ios`: build for iPhone. Needs macOS.
  - `lint`: `eslint .` checks code style and bugs in all files.
  - `format` / `format:check`: Prettier rewrites (`--write`) or only checks (`--check`) formatting.
  - `test`: `jest` runs tests. `typecheck`: `tsc --noEmit` runs the TypeScript checker without writing files.
- `dependencies` (lines 16-40), libraries shipped inside the app. A `^` before a version means "this or any newer version with the same major number". No `^` means exact.
  - `react`, `react-native`: the UI library and the mobile framework.
  - `@react-navigation/*`: moving between screens (tabs, stacks). `react-native-screens`, `react-native-safe-area-context`, `react-native-gesture-handler`, `@react-native-masked-view/masked-view` are helpers it needs.
  - `@reduxjs/toolkit`, `react-redux`: a shared state store for the app.
  - `axios`: sends HTTP requests to the FastAPI backend.
  - `react-hook-form`: form state and validation.
  - `@react-native-firebase/app` and `/auth`: Firebase login (phone OTP).
  - `@react-native-async-storage/async-storage`: small key-value storage on the phone.
  - `@react-native-community/netinfo`: checks if the network is up.
  - `@react-native-documents/picker`: pick files (likely driver documents; I am not sure, check `src`).
  - `@maplibre/maplibre-react-native`, `react-native-maps`: two map libraries. Having both is odd.
  - `react-native-config`: reads `.env` values into the app.
  - `react-native-svg`, `react-native-vector-icons`: vector images and icon fonts.
- `devDependencies` (lines 41-66), tools used only while building: Babel (code translator), ESLint and its plugins, Jest and `react-test-renderer` for tests, Prettier, TypeScript, `@types/*` (type descriptions), and `@react-native/*` build helpers, all at `0.86.2` to match `react-native`.

## 4. How data flows
```
you: pnpm test --> pnpm reads scripts.test --> runs "jest"
root: pnpm --filter driver-app test --> this file
```

## 5. Try it
```zsh
pnpm --filter driver-app typecheck
```
`--filter driver-app` picks this package. `typecheck` runs `tsc --noEmit`. Expect no output when it is fine.

## 6. Can it be better?
- Good: lint, format, test and typecheck scripts exist. Core `@react-native/*` versions are pinned together.
- Weak: the `android` script only works on Windows. Two map libraries. No `engines` field to state the Node version. TypeScript `~6.0.3` is very new; check that all tooling supports it (I am not sure).
- Cleaner way: use `cross-env`-style or a small shell script per OS, or document the Linux command.
- Security: no secrets here. Run `pnpm audit` from time to time.

## 7. Check yourself
1. What does `--no-packager` change?
2. What is the difference between `dependencies` and `devDependencies`?
