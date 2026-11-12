# driver-app/jest.config.js

## 1. Purpose
This configures **Jest** (a test runner for JavaScript. *Example:* `npx jest` runs files like `add.test.ts` and prints pass or fail). It tells Jest how to handle React Native code and which files are tests. It is read only when you run tests.

## 2. Imports, one by one
No imports. It uses CommonJS `module.exports` (line 1). It refers to one package by name: `@react-native/jest-preset` (line 2).

## 3. Walk through the code, top to bottom
- `module.exports = { ... }` (line 1) exports the config.
- `preset: '@react-native/jest-preset'` (line 2). A **preset** (a ready group of Jest settings). This one adds React Native mocks (fake versions of native parts) and the Babel transform, so tests can import `react-native`.
- `testMatch: [...]` (line 3). A list of **glob** patterns (file name patterns with `*`) that mark test files. `<rootDir>` means the `driver-app` folder.
  - `<rootDir>/src/**/__tests__/**/*.(ts|tsx)` matches any `.ts`/`.tsx` file in a `__tests__` folder under `src`.
  - `<rootDir>/src/**/*.test.(ts|tsx)` matches files like `src/utils/fare.test.ts`.
  Tests outside `src/` are ignored.

Note: `eslint.config.mjs:26` ignores this file from linting.

## 4. How data flows
```
npx jest -> reads jest.config.js -> finds src/**/*.test.ts(x)
         -> Babel transforms (babel.config.js) -> runs tests -> report
```

## 5. Try it
```zsh
cd driver-app
npx jest --listTests
```
`--listTests` only prints the test files Jest would run and does not run them. Expected: file paths, or nothing if no tests exist yet. Then `npx jest` runs them.

## 6. Can it be better?
- Good: small; restricts tests to `src`.
- Weak: there may be few or no tests (check with the command above). No coverage settings and no setup file for mocks like location or maps.
- Cleaner way: add `collectCoverageFrom: ['src/**/*.{ts,tsx}']` and a `setupFiles` entry when native modules need mocks.
- Security: nothing risky.

## 7. Check yourself
1. Which file names does `testMatch` accept?
2. What does the preset add for React Native?
