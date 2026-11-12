# docs/driver-app-foundation.md

## 1. Purpose
A note about the first phase ("Phase 0") of the driver mobile app in `driver-app/`. It says what was set up, how to check it, and what comes next. It is read by humans only.

## 2. Imports, one by one
None. It is Markdown.

## 3. Walk through the document

**Phase 0 baseline** (`docs/driver-app-foundation.md:3-9`).
- Line 5: **React Native 0.86** (a framework that builds Android and iOS apps from JavaScript. *Example:* `<Text>` becomes a native label), **TypeScript** (JavaScript with types), **React Navigation** (screen switching library), **pnpm workspace** (pnpm is a package manager; a workspace shares one install between several apps). The driver app copies the passenger app's setup.
- Line 6: the visual style. **Poppins** (a font), primary blue `#2563EB`, outlined fields, targets at least 44px (big enough to tap).
- Line 7: Firebase config and the Driver API client exist. Login logic is left for Phase 1.
- Line 8: old `DriverAuthScreen` was removed. Entry route: `Splash -> Login -> Sign Up -> Help`.
- Line 9: **Metro** (the dev server that bundles JavaScript for React Native) resolves packages from the real workspace folder, so it works on a Windows mapped drive. The author seems to develop on Windows (see also `C:/tmp/...` in `driver-app/android/app/build.gradle:59`).

**Development checks** (lines 11-25). Run in `driver-app`:
- `pnpm typecheck`: runs the TypeScript checker and reports type errors.
- `pnpm lint`: runs the linter (a style and bug checker).
- `pnpm start:reset --port 8082`: starts Metro, clearing its cache (`:reset`), on port `8082`.
- In a second CMD window (Windows command prompt): `pnpm android --port 8082` builds and installs the app on the emulator, using the same port.

**Next phase boundary** (lines 27-29). Phase 1: Firebase OTP and Driver tokens. Phase 2: an **atomic** (all-or-nothing) two-step Driver registration plus document storage.

## 4. How data flows
```
Terminal 1: pnpm start:reset --port 8082 --> Metro serves JS bundle
Terminal 2: pnpm android --port 8082 --> Gradle builds APK --> emulator --> app asks Metro for JS
```

## 5. Try it
On Arch with zsh, the same commands work (ignore "CMD"):
```zsh
cd driver-app && pnpm typecheck
```
Expected: no output and exit code 0 when types are fine. The scripts are defined in `driver-app/package.json`; check them with `jq .scripts driver-app/package.json`.

## 6. Can it be better?
- Good: clear phases and exact commands.
- Weak: assumes Windows CMD; the reader is on Linux. Says nothing about the `.env` file (see `driver-app/.env.example`). Needs a date or version so it does not go stale.
- Cleaner way: show commands in a `sh` block and note both OS options.
- Security: none here.

## 7. Check yourself
1. What does Metro do, and why are two terminals needed?
2. Which phase adds the real login, and which adds registration?
