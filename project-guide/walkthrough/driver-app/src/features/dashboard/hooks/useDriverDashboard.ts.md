# useDriverDashboard.ts

## 1. Purpose
A **hook** (a function whose name starts with `use` that gives a component memory and side effects. *Example:* `useState` remembers a value). This hook loads the driver dashboard from the backend and exposes it to screens. `DriverHomeScreen.tsx` and `DriverEarningsScreen.tsx` call it. It calls `driverDashboardService.ts`.

## 2. Imports, one by one
- `import { useCallback, useEffect, useState } from 'react';` (`driver-app/src/features/dashboard/hooks/useDriverDashboard.ts:1`)
  - **React** is the UI library. `useState` stores a value that redraws the screen when changed (*example:* `const [n, setN] = useState(0)`). `useEffect` runs code after the screen draws (*example:* start a timer). `useCallback` keeps the same function object between draws so effects do not rerun needlessly.
- `import { driverDashboardService, type DriverDashboard } from '../services/driverDashboardService';` (line 3): project file `dashboard/services/driverDashboardService.ts`. The `type` keyword imports only a TypeScript type, which vanishes at run time.

## 3. Walk through the code
**`useDriverDashboard()`** (line 5). No inputs. Returns `{ dashboard, error, isLoading, isRefreshing, refresh, updateAvailability }`.

- Lines 6-9: four pieces of state. `dashboard` starts `null`. `isLoading` starts `true` (first load). `isRefreshing` is for pull-to-refresh. `error` is a message or `null`.
- `refresh(manual = false)` (line 11): wrapped in `useCallback(..., [])` so it never changes.
  - If `manual` is true (user pulled down) set `isRefreshing`, else set `isLoading`.
  - `await driverDashboardService.getDashboard()` (line 15) asks the backend and waits. Returns a `DriverDashboard`.
  - On success: store it and clear the error (lines 16-17).
  - On failure: `catch` sets a friendly message (line 19). The real error is dropped.
  - `finally` always turns both flags off (lines 21-22).
- `useEffect` (line 26): schedules `refresh()` with `setTimeout(..., 0)` (run right after the current work), and the returned function `clearTimeout` cancels it if the screen closes first. `void refresh()` means "start it and ignore the promise".
- `updateAvailability(isOnline)` (line 31): calls `driverDashboardService.updateAvailability(isOnline)` which sends the online/offline choice, stores the new dashboard and returns it. Errors are not caught here; the caller must handle them (see `DriverHomeScreen.tsx:66-75`).

## 4. How data flows
```
Screen mounts -> useEffect -> refresh() -> service GET /api/v1/drivers/dashboard
   -> setDashboard -> screen redraws with data
Toggle button -> updateAvailability(true) -> PUT .../availability -> new dashboard -> setDashboard
```

## 5. Try it
Not directly runnable (hooks only work inside components). Open the driver app home screen and watch the spinner, then the data. Turn off the backend and pull down: the error banner appears.

## 6. Can it be better?
- Good: handles loading, refresh and error separately; cleans up its timer.
- Weak: each screen that calls this hook makes its own request and own copy of the data (`DriverEarningsScreen` fetches again). No cancel for a request that finishes after the screen is gone. The `catch` hides the real error. `updateAvailability` has no error state. The `setTimeout(..., 0)` is an unusual trick, likely used to avoid a lint rule about setting state inside an effect (I am not sure; check git history).
- Cleaner way: share the data via a context or a query library such as TanStack Query.
- Security: none directly.

## 7. Check yourself
1. Why are there two flags, `isLoading` and `isRefreshing`?
2. What happens to `error` after a later successful refresh?
