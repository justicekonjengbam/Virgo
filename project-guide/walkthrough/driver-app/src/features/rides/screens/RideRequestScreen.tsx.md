# RideRequestScreen.tsx

## 1. Purpose
Shows an incoming ride offer to the driver, with pickup, drop, distance and fare. The driver can accept or decline. It gets offers live through a WebSocket and, if the socket is down, polls the server every 10 seconds. It uses `rideMatchingService`, `driverRealtimeService` and `useDriverSession` (`features/dashboard/state/DriverSessionContext`).

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` (line 1): hooks (memory and side effects).
- `import { Alert, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 2): pop-up, notch-safe box, scroll box, styles, box.
- `MaterialCommunityIcons` (line 3): icons.
- `DriverPageHeader`, `DriverButton`, `DriverCard`, `DriverText` (lines 4-7): app components.
- `colors, radius, spacing` (line 8): theme.
- `rideMatchingService`, type `DriverRideOffer` (line 9): HTTP calls and offer type.
- `driverRealtimeService` (line 10): WebSocket listener.
- `useDriverSession` (line 11): a **context** hook. A context shares values across screens without passing props. *Example:* `const { isOnline } = useDriverSession()` reads "is the driver online?" from anywhere.

## 3. Walk through the code

**Props type** (line 13): `{ onBack, onAccepted }`, both functions with no inputs.

**State** (lines 15-18): `isOnline` and `setRequestStatus` from the session; `request` (the offer or null); `message` (error text); `liveConnected` (is the WebSocket open).

**Realtime effect** (lines 19-26). `driverRealtimeService.subscribe(listener, setLiveConnected)` registers an event listener and a connection-change listener. If `event.type === 'ride.offer'`, store the offer and clear the message. For any other event (cancel, cleared, etc.) set the request to null. Returns the unsubscribe function for cleanup.
Note: any other event, even `outstation.assigned`, clears the shown offer. See section 6.

**Polling effect** (lines 27-33). If live, do nothing. Else define `load` that calls `rideMatchingService.getCurrentOffer()` (GET the current offer or null), call it now, and repeat with `setInterval(load, 10_000)` (every 10 000 ms; `_` is only for readability). Cleanup `clearInterval` stops the timer. It reruns when `liveConnected` changes.

**`unavailable`** (line 34): true when the driver is offline.

**`actOnRequest(status)`** (line 35). Calls `rideMatchingService.respond(request!.offer_id, status)`. The `!` tells TypeScript "request is not null here". On success: `setRequestStatus(status)` updates the shared session and shows an `Alert` whose button goes to `onAccepted` (accepted) or `onBack` (declined). On any error: message "This offer is no longer available..." and clears the request.

**Render** (line 36). Optional red message. If no request: "No ride request is available right now." Else cards: route (two `RouteRow`s), distance and fare (`Math.round(expected_fare_paise / 100)`), a note "respond within 15 seconds ... `pickup_minutes_away` minutes away", then either an "unavailable" card (offline) or Decline / Accept buttons.
Ternary `!isOnline ? 'Go online...' : 'This request has already been handled.'` is inside a branch where `unavailable` already equals `!isOnline`, so the second text can never show.

**`RouteRow`** (line 38): icon in a coloured circle plus label and address. `icon: string` is passed as the icon `name`.

**`styles`** (line 39).

## 4. How data flows
```
backend --WS 'ride.offer'--> driverRealtimeService --> listener --> setRequest --> card shown
(WS down) screen --GET current offer every 10s--> rideMatchingService --> setRequest
Accept tap --> respond(offer_id,'accepted') --POST--> backend --> Alert --> onAccepted()
```

## 5. Try it
Not directly runnable alone. Go online in the driver app and request a ride from the passenger app. Expected: the offer appears. Turn off the server's WebSocket and see polling every 10 seconds in the network log.

## 6. Can it be better?
- Good: live plus fallback polling; cleanup of timers and listeners; error recovery.
- Weak: the "15 seconds" is only text; there is no countdown or use of `expires_at`; any non-offer event clears the offer (even unrelated ones); the dead text branch noted above; error is swallowed (`catch {}`) so a network failure looks like "offer gone"; no double-tap guard on Accept.
- Cleaner way: clear only on `ride.offer_cleared` or `ride.cancelled`, and disable buttons while the request runs.
```ts
// before: } else { setRequest(null); }
// after
} else if (event.type === 'ride.offer_cleared' || event.type === 'ride.cancelled') { setRequest(null); }
```
- Security: the server must check that the offer belongs to this driver (not visible here).

## 7. Check yourself
1. When does the screen poll, and how often?
2. What does `request!.offer_id` mean?
