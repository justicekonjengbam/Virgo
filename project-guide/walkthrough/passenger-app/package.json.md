# passenger-app/package.json

## 1. Purpose
`package.json` is the identity card of a Node project. It lists the app name, the commands you can run (scripts) and the libraries it needs (dependencies). pnpm reads it to install packages. It is part of the pnpm workspace (`pnpm-workspace.yaml:2`).

## 2. Imports, one by one
JSON has no imports. The "imports" of this file are the dependency lists, covered in section 3.

## 3. Walk through the code, top to bottom
**Identity (`package.json:2-4`)**
- `name: "passenger-app"`: the package name. `version: "0.1.0"`. `private: true` stops it from being published to npm by mistake.

**Scripts (`:5-14`)** Run with `pnpm <name>`. (**Script**: a saved terminal command. *Example:* `pnpm lint` runs `eslint .`.)
- `start`: `react-native start` starts Metro, the bundler.
- `android` (`:7`): `set "GRADLE_USER_HOME=C:\tmp\cabsure-gradle"&& react-native run-android --port 8081 --no-packager`. `set` is Windows cmd syntax. It sets where Gradle (Android build tool) keeps its cache. `--port 8081` is the Metro port. `--no-packager` means do not start Metro; you started it yourself. On Linux this script will not work as written, because `set "..."` is not valid zsh usage.
- `ios`: builds and runs on an iOS simulator (macOS only).
- `lint`: `eslint .` checks code style and bugs in all files.
- `format` / `format:check`: Prettier rewrites (`--write`) or only checks (`--check`) formatting.
- `test`: `jest` runs tests (see `jest.config.js`).
- `typecheck`: `tsc --noEmit` runs the TypeScript compiler only to check types, writing no files.

**dependencies (`:15-39`)** Libraries shipped inside the app. The `^` before a version means "this version or any newer compatible minor/patch". No `^` means an exact pin.
- `@babel/runtime` 7.25.0: helper functions for compiled JS (pinned; see `metro.config.js`).
- `@maplibre/maplibre-react-native`: map view using the open MapLibre engine. `react-native-maps`: another map library (Google/Apple maps). Both are present; check which one the screens use.
- `@react-native-async-storage/async-storage`: small key-value storage on the phone. *Example:* save a token.
- `@react-native-community/netinfo`: tells if the phone is online.
- `@react-native-firebase/app` and `/auth`: Firebase (Google's backend service) base and login.
- `@react-native-masked-view/masked-view`: needed by some navigation effects.
- `@react-navigation/bottom-tabs`, `native`, `native-stack`: screen navigation (tabs, stack of screens).
- `@reduxjs/toolkit` and `react-redux`: app-wide state store and its React binding.
- `axios`: HTTP client. *Example:* `axios.get(url)`.
- `react` 19 and `react-native` 0.86.2: the UI library and the mobile framework.
- `react-hook-form`: form state and validation.
- `react-native-config`: reads `.env` values into the app.
- `react-native-gesture-handler`, `react-native-screens`, `react-native-safe-area-context`: native helpers required by React Navigation.
- `react-native-svg`: draw SVG images. `react-native-vector-icons`: icon fonts.

**devDependencies (`:40-64`)** Tools used only while developing.
- `@babel/core`, `@react-native/babel-preset`: convert modern JS/TSX into code phones run.
- `@react-native-community/cli` and `-platform-android` / `-platform-ios`: the `react-native` command.
- `@react-native/codegen`, `gradle-plugin`, `metro-config`, `typescript-config`, `jest-preset`: official RN build helpers and presets (all pinned to 0.86.2 to match `react-native`).
- `@types/jest`, `@types/react`, `@types/react-test-renderer`: TypeScript type descriptions.
- `eslint`, `@eslint/js`, `eslint-config-prettier`, `eslint-plugin-react`, `eslint-plugin-react-hooks`, `typescript-eslint`: linting.
- `jest`, `react-test-renderer`: testing.
- `prettier`: code formatter. `typescript` `~6.0.3`: the type checker (`~` allows only patch updates).

## 4. How data flows
```
pnpm install -> reads package.json -> downloads packages to node_modules
pnpm <script> -> runs the command text of that script
```

## 5. Try it
```sh
cd passenger-app && pnpm install && pnpm typecheck
```
`pnpm install` fetches all packages. `pnpm typecheck` runs `tsc --noEmit`; expected: no output when types are fine.

## 6. Can it be better?
- Good: scripts cover lint, format, test and types. RN packages are version-pinned together.
- Weak: the `android` script only works on Windows. Two map libraries may be duplicate. No `engines` field to state the Node version. Caret ranges can change installs over time (a lockfile reduces this).
- Cleaner way: make `android` portable: `"android": "react-native run-android --port 8081 --no-packager"` and set `GRADLE_USER_HOME` in your shell.
- Security: no secrets here. Run `pnpm audit` now and then.

## 7. Check yourself
1. What is the difference between `dependencies` and `devDependencies`?
2. Why will the `android` script fail in zsh?
