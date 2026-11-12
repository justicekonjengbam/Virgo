# DriverSessionContext.tsx

## 1. Purpose
Holds two small pieces of driver state that many screens share: "is the driver online" and "status of the ride request". It uses React **Context** (a way to share data with all child components without passing props down each level. *Example:* a theme every screen can read). `DriverHomeScreen.tsx` reads it through `useDriverSession`. The provider is mounted higher up in the app (I did not check where; search `rg DriverSessionProvider driver-app/src`).

## 2. Imports, one by one
- `import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';` (`driver-app/src/features/dashboard/state/DriverSessionContext.tsx:1`)
  - `createContext` makes a context. `useContext` reads it. `useState` stores a value. `useMemo` remembers a computed value until its inputs change (*example:* build an object once). `ReactNode` is the type for "anything React can draw", used for `children`.

## 3. Walk through the code
- `RideRequestStatus` (line 3): one of four words: idle, pending, accepted, declined.
- `DriverSession` type (lines 5-10): the shape of the shared object: two values and two setter functions.
- `createContext<DriverSession | null>(null)` (line 12): the context, with default `null` meaning "no provider above".
- **`DriverSessionProvider({ children })`** (line 14): a component that wraps part of the app.
  - Lines 15-16: the two states. Online starts `false`, status starts `'idle'`.
  - Line 17: `useMemo` builds the shared object. It is rebuilt only when `isOnline` or `requestStatus` changes, so consumers do not redraw for nothing. The setters are stable, so they are not in the list.
  - Line 18: `<DriverSessionContext.Provider value={value}>` gives the value to every child.
- **`useDriverSession()`** (line 21): `useContext` reads the value. If it is `null` (used outside the provider) it throws `Error('Driver session is unavailable.')` (line 23). Otherwise it returns the object. *Example:* `const { isOnline, setIsOnline } = useDriverSession();`.

## 4. How data flows
```
DriverSessionProvider (state) --value--> useDriverSession() in DriverHomeScreen
Toggle button -> session.setIsOnline(true) -> provider state changes -> consumers redraw
```

## 5. Try it
Not directly runnable. Remove the provider in the app root and open the home screen; you should see the thrown error message.

## 6. Can it be better?
- Good: safe hook that fails loudly; memoized value.
- Weak: state is lost when the app restarts (it starts offline until the dashboard loads). `requestStatus` may be unused; check with `rg setRequestStatus driver-app/src`.
- Cleaner way: if only `isOnline` is needed, drop `requestStatus`. Backend is the true source of the online flag.
- Security: none.

## 7. Check yourself
1. What happens if a screen calls `useDriverSession` with no provider above it?
2. Why is `useMemo` used for `value`?
