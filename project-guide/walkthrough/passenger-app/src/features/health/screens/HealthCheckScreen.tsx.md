# HealthCheckScreen.tsx

## 1. Purpose
A small debug screen that asks the backend `/health` and shows "Backend Connected" or "Connection Failed", with a Retry button. It uses `healthService.ts`, `ApiError` from `services/apiClient.ts`, and basic components. I did not check which navigator mounts it; search with `rg HealthCheckScreen passenger-app/src`.

## 2. Imports, one by one
Third-party:
- `import { useCallback, useEffect, useState } from 'react';` (line 1). `useState` keeps a value and redraws on change. `useEffect` runs code after the screen appears. `useCallback` keeps the same function between redraws. *Example:* `useCallback(() => ..., [])`.
- `import { SafeAreaView, StyleSheet, View } from 'react-native';` (line 2). `SafeAreaView` avoids notches, `StyleSheet` makes styles, `View` is a box.

Project:
- `AppButton` (line 4), `AppText` (5), `LoadingState` (6): button, text and spinner components under `components/foundation` and `components/feedback`.
- `ApiError` (7) from `services/apiClient.ts:8`: an error class the HTTP client throws, whose `message` is user-readable.
- `colors, radius, spacing` from `theme/tokens` (8): design values.
- `healthService, type HealthStatus` (9) from `../services/healthService`.

## 3. Walk through the code, top to bottom
- Line 11: `ConnectionState` is one of three words: `'loading' | 'connected' | 'failed'`. This is a **union type** (a value that can be only one of the listed options).
- Lines 13-14: `getErrorMessage(error: unknown): string`. `instanceof ApiError` checks whether the error is an `ApiError`. If yes, return its message. Otherwise return `'Connection Failed'`.
- Lines 17-19: three state values: `connectionState`, `health`, `errorMessage`.
- Lines 21-34: `checkHealth` is async. It sets loading, clears the error, then `await healthService.check()` (sends GET /health). On success it stores the data and sets `connected`. In `catch` it clears health, stores a message, sets `failed`. Used by the Retry button.
- Lines 36-61: `useEffect` runs once on appearing. It does the same check but with `isMounted`. **isMounted flag** (a variable that becomes `false` in the cleanup function, which React runs when the screen disappears; it stops setting state on a screen that is gone). `return () => { isMounted = false; }` is that cleanup.
- Lines 63-88: the view. Title; `{cond && <X/>}` draws X only when cond is true. `accessibilityLiveRegion="polite"` makes screen readers announce changes. Retry shows when not loading (85).
- Lines 91-120: styles; success is green, error is red, using `colors.success` and `colors.error`.

Errors: any failure of `check()` becomes the "failed" state.

## 4. How data flows
```
mount -> useEffect -> healthService.check() -> GET /health -> backend
 ok  -> setHealth + 'connected' -> shows version and environment
 err -> getErrorMessage -> 'failed' -> shows message
Retry tap -> checkHealth() -> same, state 'loading' first
```

## 5. Try it
Not directly runnable alone. Start the backend and the app, then open this screen. Expected: "Backend Connected / Version x / Environment: y". Stop the backend and tap Retry to see "Connection Failed".

## 6. Can it be better?
- Good: handles three states, cleans up, is accessible.
- Weak: the effect repeats the logic of `checkHealth` (duplicate code). The `failed` branch does not clear `health` in the effect. Title and `fontSize: 18` are magic values.
- Cleaner way: one `run` function with an `isMounted`/abort check, used by both the effect and Retry.
- Security: shows the environment name (like "production") to anyone who opens this screen; keep it out of release builds.

## 7. Check yourself
1. What is the `isMounted` flag protecting against?
2. Why is Retry hidden while loading?
