# DriverOutstationScreen.tsx

## 1. Purpose
Shows the driver's outstation trips (long-distance trips booked in advance and assigned by support): "Scheduled trips" and "Completed trips". It reloads when a live event about outstation trips arrives and supports pull-to-refresh. It calls `rideMatchingService.outstationAssignments()` and `driverRealtimeService.subscribe()`.

## 2. Imports, one by one
- `import { useCallback, useEffect, useState } from 'react';` (line 1). `useCallback(fn, deps)` keeps the same function between redraws unless `deps` change. *Example:* so an effect that depends on `load` does not rerun every time.
- `import { ActivityIndicator, RefreshControl, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 2). `RefreshControl` is the pull-down-to-refresh spinner for a `ScrollView`.
- `import axios from 'axios';` (line 3). HTTP library. Used only for `axios.isAxiosError(x)`, which checks if an error came from an HTTP call.
- `MaterialCommunityIcons` (line 4): icons.
- `DriverCard`, `DriverPageHeader`, `DriverText` (lines 6-8); `colors, spacing` (line 9).
- `rideMatchingService`, type `DriverOutstationAssignment` (line 10); `driverRealtimeService` (line 11).

## 3. Walk through the code

**`DriverOutstationScreen({ onBack })`** (line 13).

**State** (line 14): `items` (list or `null` = not loaded yet), `error` (text), `refreshing` (pull-to-refresh spinner).

**`load`** (line 15). `useCallback(async (manual=false) => {...}, [])`.
- If `manual` (user pulled), `setRefreshing(true)`.
- `setError('')`, then `setItems(await rideMatchingService.outstationAssignments())` (GET the list).
- `catch` stores `messageFor(cause)`. `finally` stops the spinner.

**Effect** (line 16). On open it calls `load()`. It returns the result of `driverRealtimeService.subscribe(...)`, which is the unsubscribe function (cleanup). The listener reloads when `event.type` starts with `outstation.` (`outstation.assigned`, `outstation.updated`).

**Lists** (line 17). `items?.filter(...) ?? []`: if `items` is null use `[]`. `upcoming` = status `driver_assigned`; `completed` = status `completed`. `filter` keeps items where the test is true.

**Render** (line 18):
- Header, then `ScrollView` with `refreshControl`. `colors={[colors.primary]}` is the spinner colour (Android).
- Error card when `error` is set.
- If `items === null` show spinner; else if there are upcoming trips show an `AssignmentCard` for each (`key={item.id}` for React); else an empty-state card.
- If any completed trips, show their heading and cards.

**`AssignmentCard`** (line 20). Builds `date` from `item.scheduled_at` (an ISO date string like `2026-11-01T09:30:00Z`). `done` is true for completed trips. It shows trip id, `toLocaleDateString('en-IN')` (for example `01/11/2026`) and time, a status badge (icon and word change when done), pickup, destination, passenger name and phone, vehicle, distance and fare. Fare: `Math.round(paise / 100).toLocaleString('en-IN')` gives for example `12,500` (Indian digit grouping).
`style={done ? {...styles.card, ...styles.completed} : styles.card}` merges two style objects (spread `...` copies keys).

**`messageFor(cause: unknown)`** (line 21). Returns text for an error: 401 means session expired; no `response` means the server is unreachable; if the server's `detail` is a string, show it; otherwise a generic message. `unknown` forces the code to check the type first.

**`styles`** (line 22).

## 4. How data flows
```
open screen -> load() -> GET /api/v1/drivers/me/outstation-assignments -> setItems -> redraw
support assigns trip -> backend -> WebSocket 'outstation.assigned' -> subscribe handler -> load()
pull down -> onRefresh -> load(true)
```

## 5. Try it
Not directly runnable alone. In the driver app open "Outstation schedule". Assign a trip from the admin app: the card should appear without a manual refresh.

## 6. Can it be better?
- Good: handles loading, empty, error; live updates; clean unsubscribe.
- Weak: code written without spaces and many statements per line (hard to read); `load` catches errors but keeps old `items` (good) yet no retry button; phone number shown in full; the 401 message says "sign in again" but no button does that.
- Cleaner way: run Prettier (a code formatter) so each statement has its own line:
```ts
// before: const load=useCallback(async(manual=false)=>{if(manual)...
// after
const load = useCallback(async (manual = false) => {
  if (manual) setRefreshing(true);
  ...
}, []);
```
- Security: shows passenger phone only to the assigned driver (backend should enforce that; not seen here).

## 7. Check yourself
1. Why is `load` wrapped in `useCallback`?
2. What does `messageFor` return when the phone has no internet?
