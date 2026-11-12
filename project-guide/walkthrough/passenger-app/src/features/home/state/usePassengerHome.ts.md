# usePassengerHome.ts

## 1. Purpose
A **custom hook** (your own function whose name starts with `use` and which uses other hooks inside; it lets many screens share logic). It loads the Home data from the backend and keeps `data`, `loading` and `error` for the screen. It is used by `features/home/screens/PassengerHomeScreen.tsx`. It calls `homeApi.getHome()` in `../data/homeApi`.

## 2. Imports, one by one
- `import { useCallback, useEffect, useState } from 'react';` React hooks.
  - `useState`: memory in a component. *Example:* `const [x, setX] = useState(0)`.
  - `useEffect`: run code after the screen draws. *Example:* `useEffect(() => { log('shown') }, [])` runs once.
  - `useCallback`: keeps the same function object between draws unless its inputs change. Needed here so `useEffect` does not re-run forever.
- `import { ApiError } from '../../../services/apiClient';` (project, line 3) An error class thrown by the app's HTTP client. Used to tell a known API error from other errors.
- `import { homeApi } from '../data/homeApi';` (line 4) Object with `getHome()`.
- `import type { PassengerHome } from '../domain/homeTypes';` (line 5) The type of the home response.

## 3. Walk through the code, top to bottom
**`usePassengerHome()`** (lines 7-22). Input: nothing. Output: `{ data, error, loading, refresh }`.
- Line 8: `data` starts `null`.
- Line 9: `loading` starts `true`, so the first draw shows the spinner.
- Line 10: `error` is `string | null`.
- Lines 11-16 `refresh`: an async function wrapped in `useCallback(..., [])`. The empty list `[]` means "never recreate".
  - Line 12: set loading true and clear error.
  - Line 13: `await homeApi.getHome()` waits for the HTTP call, then `setData` stores the result.
  - Line 14: `catch`: if the error is an `ApiError`, show its message; else show a general text. `instanceof` checks if a value was made by a class.
  - Line 15: `finally` always runs, so loading becomes false in success and failure.
- Lines 17-20 `useEffect`: waits with `setTimeout(..., 0)` (run on the next tick), then calls `refresh()`. The returned function `() => clearTimeout(task)` is the **cleanup** (it runs when the screen goes away, so a stale call is cancelled). The dependency list `[refresh]` is stable thanks to `useCallback`.
- Line 21: returns the four values.

## 4. How data flows
```
Screen draws -> useEffect -> refresh() -> setLoading(true)
   -> homeApi.getHome() --HTTP GET--> backend
   <- JSON -> setData -> setLoading(false) -> Screen redraws with data
(on failure: setError(message) -> Screen shows DsEmptyState "Try again" -> refresh())
```

## 5. Try it
Not directly runnable. Use it inside a component:
```tsx
const { data, loading } = usePassengerHome();
if (loading) return null;
console.log(data?.ride_categories.length);
```
Expected: a number after the data loads.

## 6. Can it be better?
- Good: small, clear, handles error and cleanup.
- Weak: the `setTimeout(0)` is odd; a plain `void refresh()` in the effect is normal. If the screen unmounts while the request is running, `setData` still runs (a warning in older React). An `AbortController` (a browser tool that cancels a request) or a "mounted" flag fixes that. Lines 12 and 13 put several statements on one line; split them for reading. No tests.
- Cleaner way: use a data library such as TanStack Query for loading, errors and caching. This is an opinion.
- Security: none directly. Error messages from the API are shown to the user.

## 7. Check yourself
1. Why is `refresh` wrapped in `useCallback` and what happens to `useEffect` without it?
2. What does the `finally` block guarantee?
