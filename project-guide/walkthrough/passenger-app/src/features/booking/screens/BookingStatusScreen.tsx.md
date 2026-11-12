# BookingStatusScreen.tsx

File: `passenger-app/src/features/booking/screens/BookingStatusScreen.tsx` (40 lines)

## 1. Purpose
Shows a booked ride live: map, driver name and vehicle, status text, and a cancel or end button. It uses a WebSocket for live news, and falls back to asking every 10 seconds if the socket is down. A parent (not read here) renders it after booking. It calls `passengerRealtimeService.ts` and `bookingApi.ts`.

## 2. Imports, one by one
- `useEffect, useState` from `react` (hooks: `useState` for memory, `useEffect` for side effects such as network or timers, with cleanup).
- From `react-native`: `ActivityIndicator` (spinner), `Alert` (popup with buttons), `SafeAreaView`, `ScrollView`, `StyleSheet`, `View`.
- `MaterialCommunityIcons` from `react-native-vector-icons/MaterialCommunityIcons`: icon set (*Example:* `name="car-off"`).
- Project: `AppPageHeader`; `DsButton`, `DsCard`, `DsText`; `colors`, `radius`, `spacing` (`theme`); `CabSureMap` (`features/maps/components/CabSureMap`); `bookingApi`, types `RideBooking`, `RideStatus` (`../data/bookingApi`); `subscribeToRide`, type `DriverLocation` (`../services/passengerRealtimeService`).

## 3. Walk through the code, top to bottom

### Props (12)
`ride` (the booking just made), `onDone`, `onMenuPress`.

### State (15-18)
`status` (latest `RideStatus` or `null`), `driverLocation`, `liveConnected`, `ending`.

### Effect 1, live socket (19)
`useEffect(() => subscribeToRide(ride.ride_id, setStatus, setLiveConnected, setDriverLocation), [ride.ride_id]);` Opens the WebSocket. The function `subscribeToRide` returns a cleanup function, and React calls it when the screen closes or the ride id changes. The setters are passed as callbacks.

### Effect 2, polling fallback (20-26)
If `liveConnected`, do nothing. Otherwise `load()` asks `bookingApi.status` now and every 10 000 ms (`setInterval`). `mounted` stops updates after cleanup. The cleanup clears the timer. Failures are ignored (`catch(() => undefined)`). When the socket reconnects, `liveConnected` changes and the effect re-runs and stops polling.

### Derived values (27-30)
`state` = live status or the booking's status. `finished` is true for `cancelled` or `completed`. `title` and `icon` are chosen by chained ternaries (`a ? x : b ? y : z`). `state.startsWith('driver_')` matches `driver_arriving` and `driver_arrived`.

### `askToEnd` (31)
Shows `Alert.alert(title, text, buttons)`. Text differs by `status?.can_end` (trip in progress: "End"; otherwise "Cancel"). `?.` reads a field only if the object exists. The destructive button calls `endRide`.

### `endRide` (32)
Sets `ending`, calls `bookingApi.cancel(ride_id, reason)`, then re-reads the status. Errors show an `Alert`. `finally` clears `ending`.

### Map points (33-35)
`pickup`, `destination` from status; `driver` is the live socket location, or the last known one in `status`. `!= null` is true for both `null` and `undefined`.

### JSX (36)
One long line: header (back button either finishes or asks to cancel), map, a green or orange connection dot with caption, icon and title, a card with pickup, destination, and driver info if known, a spinner if no status yet, and the bottom button (Back to Home, or cancel/end).

### `RouteLine` (39)
A small component: caption plus value.

### `styles` (40)
Layout rules, including a small round `dot` (`borderRadius: radius.pill`).

## 4. How data flows
```
mount -> subscribeToRide -> WebSocket -> {ride.status} -> setStatus -> redraw title/driver card
                                      -> {driver.location} -> setDriverLocation -> map marker moves
socket down -> liveConnected=false -> poll bookingApi.status every 10s
tap Cancel -> Alert -> endRide -> bookingApi.cancel -> bookingApi.status -> setStatus
```

## 5. Try it
Not directly runnable alone. Run passenger app and driver app, book and accept a ride. Expected: title changes to "Driver is on the way" and a live green dot.

## 6. Can it be better?
- Good: live updates with a polling fallback; cleanup on unmount; confirmation before cancel; sets title from a single `state`.
- Weak: line 36 is one huge JSX line; status strings are repeated magic text (also in the backend); `finished` back button leaves while `ending`; the cancel error message uses `cause.message`, fine for `ApiError`; the "Reconnecting live tracking…" text also shows right after opening, before the first connection; `ride.pickup_address` is shown instead of `status` addresses; no tests.
- Cleaner way: split JSX into small components (`ConnectionBadge`, `DriverCard`), and use a map for titles:
```ts
const TITLES: Record<string, string> = { driver_arriving: 'Driver is on the way', completed: 'Ride completed' /* ... */ };
const title = TITLES[state] ?? 'Finding your driver';
```
- Security: shows the driver name and vehicle plate to the right passenger only; relies on the backend for that.

## 7. Check yourself
1. When does the 10-second polling run, and how does it stop?
2. How does the map know where the driver is?
