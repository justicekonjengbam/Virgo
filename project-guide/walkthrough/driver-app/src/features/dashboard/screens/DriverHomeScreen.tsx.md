# DriverHomeScreen.tsx

## 1. Purpose
This is the main screen of the driver app. It shows the greeting, the online/offline switch, earnings, stats, pending ride request, current vehicle, quick actions, and a side menu. It is the busiest file in the driver app. It calls `useDriverDashboard`, `useDriverSession`, `rideMatchingService`, `driverRealtimeService` and `useDriverLocationReporter`. The app navigator (not read here) renders it and passes the `on...` functions.

## 2. Imports, one by one
React and React Native:
- `import { useEffect, useState } from 'react';` (`driver-app/src/features/dashboard/screens/DriverHomeScreen.tsx:1`): `useState` stores values; `useEffect` runs side effects (start and stop timers, subscriptions).
- `import { ActivityIndicator, Alert, Modal, Pressable, RefreshControl, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 2): spinner; `Alert` (native popup, *example:* `Alert.alert('Hi')`); `Modal` (a panel above the screen); `Pressable` (tap area); `RefreshControl` (pull-to-refresh); `SafeAreaView`; `ScrollView`; `StyleSheet`; `View`.
- `MaterialCommunityIcons` (line 3): icons.

Project imports:
- `DriverCard`, `DriverText` (lines 5-6): shared UI.
- `colors, radius, shadows, spacing` (line 7): theme.
- `DriverDrawer` (line 8), `DriverHeader` (line 9): sibling components in `dashboard/components`. Header is explained in its own file.
- `useDriverDashboard` (line 10): loads dashboard data.
- types `DriverDashboard`, `DriverVehicleStatus` (line 11) from `driverDashboardService.ts`.
- `useDriverSession` (line 12): shared online flag from `DriverSessionContext.tsx`.
- `rideMatchingService` (line 13): REST calls for offers and active ride, from `features/rides/services`.
- `driverRealtimeService` (line 14): live event connection (probably WebSocket, a long-lived two-way connection; I did not read it).
- `useDriverLocationReporter` (line 15): sends GPS.

## 3. Walk through the code
**Types** (lines 17-18): `DriverHomeScreenProps` lists eight callbacks the parent supplies (open active ride, earnings, help, outstation, request, settings, trip history, logout). `DetailSheet` is `'earnings' | 'history' | 'vehicle' | null`.

**`DriverHomeScreen(props)`** (line 20)

State (lines 21-29):
- `session` is the shared context. `useDriverDashboard()` gives dashboard data, error, loading flags, `refresh`, `updateAvailability`.
- Local state: `menuVisible`, `sheet`, `updatingAvailability`, `hasPendingOffer`, `liveConnected`, `activeRideId`.
- `useDriverLocationReporter(session.isOnline)` starts GPS reporting while online and returns `permissionDenied`.

Effects:
1. Lines 31-33: when a dashboard arrives, copy its `is_online` into the shared session, so the backend value wins.
2. Lines 35-50: `driverRealtimeService.subscribe(onEvent, onConnectedChange)` listens to live events and returns an unsubscribe function, which React uses as cleanup.
   - `outstation.assigned`: show an `Alert` with buttons "Later" and "View schedule" (calls `onOpenOutstation`).
   - `outstation.updated` with status `completed`: informational alert.
   - Other events: `setHasPendingOffer(event.type === 'ride.offer')`. So a `ride.offer` event turns the banner on; any other event type turns it off.
   - The second argument `setLiveConnected` stores whether the live link is up.
   - Empty dependency list `[]` means subscribe once.
3. Lines 52-58: fallback polling. If the live link is up, do nothing. Otherwise call `rideMatchingService.getCurrentOffer()` now and every 10 s (`10_000` ms; underscores are only for reading). `Boolean(offer)` turns "offer or null" into true/false. Errors are ignored. Cleanup clears the interval.
4. Lines 60-64: every 10 s, ask `rideMatchingService.activeRide()` and store `ride?.ride_id ?? null` (`?.` safely reads; `??` gives null if missing).

**`toggleAvailability`** (line 66): ignores clicks while an update runs. Sets the flag, calls `updateAvailability(!session.isOnline)`, copies the result into the session, and always clears the flag in `finally`. If the request fails the error is thrown from the async function and is not caught (an unhandled promise rejection, because it is called with `void` on line 92).

**`quickActions`** (lines 77-83): a list of `[icon, label, onPress]`. `as const` makes TypeScript treat the values as fixed.

**Early returns** (lines 85-86): spinner while first loading; error screen with retry if there is no dashboard.

**Main JSX** (lines 88-105):
- `hasPendingRequest` = online and offer pending.
- `ScrollView` with `RefreshControl` (pull down calls `refresh(true)`).
- `DriverHeader` (line 90).
- Error banner if `error` (line 91) with Retry.
- `AvailabilityCard` (line 92).
- Warning if location permission was denied while online (line 93).
- "Continue active ride" card if `activeRideId` (line 94).
- `EarningsCard`, `PerformanceStats` (lines 95-96).
- Either the "New ride request" banner or the "ready" notice (line 97).
- Vehicle card that opens the vehicle sheet (line 99).
- Quick actions grid built with `.map` (line 101). `key={label}` helps React track list items.
- Summary card, version text (lines 102-103).
- `DriverDrawer` side menu and `DriverDetailSheet` modal (line 104).

**Helper components** (lines 107-121):
- `DashboardLoading`, `DashboardError({ onRetry })`: full-screen states.
- `AvailabilityCard`: power icon, "You are Online/Offline" text, and a `Pressable` with `accessibilityRole="switch"` and state. While updating it shows a spinner and is disabled.
- `EarningsCard` / `EarningColumn`: blue card with Today and This month; `rides === 1 ? 'ride' : 'rides'` handles plural.
- `PerformanceStats`: three tiles: active time (`formatMinutes`), safety score (`—` if null), rating (`New` if null else `toFixed(1)`, e.g. `4.8`).
- `VehicleCard`: no vehicle placeholder, or an icon by category (bike, auto, other becomes car), the make and model, registration, seats, and a status word picked from `verification_status` (verified, pending, expired, else "needs attention").
- `QuickAction`: icon and label button; `style` as a function receives `pressed` to dim while held.
- `DriverDetailSheet`: returns `null` when no type; otherwise a bottom `Modal`. The outer `Pressable` closes on a tap outside; the inner one does `() => undefined` so taps inside do not close it. Note `'earnings'` and `'history'` are valid types but only `'vehicle'` is set from this file (lines 81, 99); the others are leftover.

**Helpers** (lines 123-126):
- `formatRupees(paise)`: `formatRupees(1234500)` gives `₹12,345`.
- `formatMinutes(90)` gives `1 hr 30 min`; `45` gives `45 min`.
- `capitalize('auto')` gives `Auto`.
- `summaryText(dashboard)`: sentence about today's rides and earnings.

**`styles`** (line 128): one long object of layout rules. Reused tokens like `spacing.lg` come from the theme.

## 4. How data flows
```
Backend --GET dashboard--> useDriverDashboard --> dashboard --> UI
Backend --live event 'ride.offer'--> driverRealtimeService --> setHasPendingOffer --> banner
(no live link) timer 10 s --> rideMatchingService.getCurrentOffer --> banner
Driver taps switch --> updateAvailability --> PUT --> new dashboard --> session.isOnline
session.isOnline --> useDriverLocationReporter --> GPS --> backend
```

## 5. Try it
Not directly runnable. Start the backend, then `cd driver-app && npx react-native run-android`. Log in as a driver and use the switch. Pull down to refresh. Turn off the network to see the error banner.

## 6. Can it be better?
- Good: handles loading, error, offline fallback, plural forms, accessibility roles, and cleans up timers.
- Weak:
  - Very long file with many one-line components and a huge `styles` line. Hard to read and review.
  - `toggleAvailability` has no `catch`, so a failed toggle is silent or unhandled.
  - Effect on line 31 depends on `session`, which changes whenever its value changes; this can rerun the effect more than needed.
  - The effect on line 46 treats any non-outstation event as "offer or no offer", which may hide other event types.
  - Two polling timers every 10 s even when the live link works (the active-ride poll always runs).
  - `formatRupees` duplicates `rupees` in `DriverEarningsScreen.tsx:15`.
  - Hard-coded version text "0.0.1" (line 103).
  - Unused sheet types 'earnings' and 'history'.
  - No tests.
- Cleaner way: split each helper component into its own file, move formatters to a `utils/format.ts`, and wrap the toggle:
```
try { ... } catch { Alert.alert('Could not change status'); } finally { ... }
```
- Security: it renders data from the server only as text, so there is no injection risk here.

## 7. Check yourself
1. When does the app poll `getCurrentOffer`, and when does it not?
2. What stops a tap inside the detail sheet from closing it?
