# DriverActiveRideScreen.tsx

## 1. Purpose
This screen shows the ride the driver has accepted and lets the driver move it forward: "I have arrived", "Start ride" (needs the passenger's 4-digit OTP), "Complete ride", or cancel. After completion it shows the fare summary and a rating screen. It is opened after a driver accepts a ride (`RideRequestScreen.tsx`). It calls `rideMatchingService`, `driverRealtimeService`, the map component `DriverRideMap`, and the hook `useDriverLocationReporter`.

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` (line 1). React hooks. `useState` keeps values that redraw the screen when changed. `useEffect` runs code after the screen shows (and can return a cleanup function).
- `import { Alert, Pressable, SafeAreaView, ScrollView, StyleSheet, TextInput, View } from 'react-native';` (line 2). `Alert` shows a native pop-up (`Alert.alert('Title','Text')`). `Pressable` is a tappable area. `SafeAreaView` avoids notch. `ScrollView` scrolls. `StyleSheet` defines styles. `TextInput` is a typing box. `View` is a box.
- `MaterialCommunityIcons` (line 3): icon font, `<MaterialCommunityIcons name="star-outline" size={36}/>`.
- Project components (lines 5-8): `DriverButton`, `DriverCard`, `DriverPageHeader`, `DriverText` from `driver-app/src/components`.
- `colors, radius, spacing, typography` from `driver-app/src/theme` (line 9): design values.
- `DriverRideMap` from `features/maps/components/DriverRideMap` (line 10): draws the map with pickup, destination and route.
- `useDriverLocationReporter` from `features/maps/hooks/...` (line 11): a hook that sends the driver's GPS to the server and says if permission was denied.
- `driverRealtimeService` (line 12): the WebSocket listener (see `driverRealtimeService.ts.md`).
- `rideMatchingService` and types `DriverActiveRide`, `RideSummary` (line 13).

## 3. Walk through the code

**Component** `DriverActiveRideScreen({ onBack, onFinished })` (line 15). `onBack` goes back; `onFinished` leaves the ride flow.

**State** (lines 16-20): `ride` (current ride or null), `message` (text shown when there is no ride), `updating` (a request is running), `startOtp` (what the driver typed), `summary` (set when the ride ends).

**Location** (line 21): `const { permissionDenied } = useDriverLocationReporter(true);` turns reporting on and returns whether the driver refused location permission.

**`refresh`** (line 22). Calls `rideMatchingService.activeRide()` (GET the active ride, or `null`). Then stores the ride and sets the message ('You do not have an active ride.' if null). On failure: 'Unable to load the active ride.'

**First effect** (line 23). `useEffect(refresh, [])` runs `refresh` once when the screen opens. Note: `refresh` returns `undefined` (because of `void`), which is a valid effect result.

**Realtime effect** (line 24). `driverRealtimeService.subscribe(handler)` registers a listener on the WebSocket. It returns an "unsubscribe" function, which React uses as cleanup. Rules: `ride.cancelled` or `ride.completed` clear the ride and show a message; any other event starting with `ride.` calls `refresh()`.

**`action(next)`** (line 25). For `'arrived' | 'start' | 'complete'`.
1. Return if no ride.
2. For `start`, check the OTP with the regex `/^\d{4}$/` (exactly four digits). If wrong, `Alert.alert` and stop.
3. `setUpdating(true)`, then `rideMatchingService.action(ride.ride_id, next, otp or undefined)` posts the action.
4. If `complete`, fetch `rideMatchingService.summary(...)` and store it (shows the summary page). Else `refresh()`.
5. On error show `Alert`; `finally` clears `updating`.

**`askToEnd`** (line 26). Shows a confirm pop-up with buttons "Keep ride" (cancel style) and a red "End trip"/"Cancel pickup" button that calls `cancel()`. Texts depend on `ride.can_end`.

**`cancel`** (line 27). Picks a reason: `vehicle_issue`, or `passenger_no_show` when status is `driver_arrived` (and the ride cannot be ended). Calls `rideMatchingService.cancel(id, reason)`, then alerts "Ride ended" with a Done button that calls `onFinished`.

**`rate(score)`** (line 28). Sends a 1-5 rating via `rideMatchingService.rate`, then alerts and finishes.

**Three screens in one component** (lines 29, 30, 32):
- `if (summary)` (line 29): fare summary. `summary.fare_items.map(...)` makes one row per fee line; `amount_paise / 100` converts paise (1/100 of a rupee) to rupees. Stars: `[1,2,3,4,5].map(...)` draws five tappable stars; `key` helps React track list items. "Skip for now" calls `onFinished`.
- `if (!ride)` (line 30): empty state with the `message` and a Home button.
- Main view (line 32): map, optional location-permission warning, passenger and addresses (`RouteRow`), the OTP box (only when status is `driver_arrived`; `keyboardType="number-pad"`, `maxLength={4}`), the main action button, and the cancel button.

**`nextAction`** (line 31). Maps status to a label and action: `driver_arriving` -> arrived; `driver_arrived` -> start; anything else -> complete. `as const` makes TypeScript treat the pair as fixed values.

**`RouteRow`** (line 35): small helper showing a label and value.
**`styles`** (line 36): the style table.

## 4. How data flows
```
Server --WebSocket event--> driverRealtimeService --> subscribe handler --> refresh()
refresh() --GET active ride--> rideMatchingService --> setRide --> redraw
Driver taps button --> action() --POST /rides/{id}/actions--> backend --> refresh()/summary()
```

## 5. Try it
Not directly runnable alone. Run the driver app, go online, accept a ride, and open the active ride. Press "I have arrived": the button should change to "Start ride".

## 6. Can it be better?
- Good: confirms before cancelling; checks OTP format; handles live events; `finally` resets loading.
- Weak: one long component with three screens; very long lines; `refresh` is re-created each render and used in effects with `[]` (the lint rule `react-hooks/exhaustive-deps` may warn); `summary` shows `Rate` stars but the icon is always `star-outline` (no filled state); `amount_paise / 100` may give decimals like `₹99.5`; the cancel reason is hard-coded and the driver cannot choose.
- Cleaner way: split into `FareSummary`, `EmptyRide`, `ActiveRideView` components; format money in one helper `formatRupees(paise)`.
- Security: the OTP is checked by the server too (not seen here; confirm in the backend). The app only checks the format.

## 7. Check yourself
1. Which events make the screen call `refresh()`, and which clear the ride?
2. Why is the OTP box shown only when the status is `driver_arrived`?
