# passenger-app/jest.config.js

## 1. Purpose
This file configures Jest, the test runner (a tool that finds and runs your test files). It is read when you run `pnpm test` (`passenger-app/package.json:12`). It sits at the app root.

## 2. Imports, one by one
No `import` or `require` lines. The file uses `module.exports`, the CommonJS way to hand a value to Node. (*Example:* `module.exports = 5` lets another file do `require('./x')` and get 5.)

## 3. Walk through the code, top to bottom
- `module.exports = { ... }` (`jest.config.js:1`): exports one config object.
- `preset: '@react-native/jest-preset'` (`:2`): a preset is a ready-made bundle of settings. This one comes from the React Native team. It teaches Jest to understand React Native code (JSX, TypeScript, native module mocks). It is listed in `devDependencies` (`package.json:49`).
- `testMatch: [...]` (`:3`): patterns for which files count as tests. `<rootDir>` means the app folder.
  - `<rootDir>/src/**/__tests__/**/*.(ts|tsx)`: any `.ts`/`.tsx` file inside a `__tests__` folder under `src`. (`**` = any number of folders.)
  - `<rootDir>/src/**/*.test.(ts|tsx)`: any file like `Login.test.tsx`.
  - Tests outside `src` are ignored.

## 4. How data flows
```
pnpm test -> jest -> reads jest.config.js -> preset + testMatch
  -> finds src/**/*.test.tsx -> runs them -> prints pass/fail
```

## 5. Try it
```sh
cd passenger-app && pnpm test
```
`pnpm test` runs the `test` script, which is `jest`. Expected: a list of PASS/FAIL lines, or "No tests found" if none exist yet. Add `--listTests` to only print which files match.

## 6. Can it be better?
- Good: very small, uses the official preset.
- Weak: no `setupFiles` for mocking native modules (AsyncStorage, Firebase), which many apps need. No coverage settings.
- Cleaner way (opinion): when tests fail with "native module is null", add `setupFiles: ['<rootDir>/jest.setup.js']`.
- Security: none.

## 7. Check yourself
1. What does `testMatch` decide?
2. Which package supplies the `preset`?
