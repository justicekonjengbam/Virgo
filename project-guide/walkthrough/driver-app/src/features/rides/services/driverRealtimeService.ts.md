# driverRealtimeService.ts

## 1. Purpose
Keeps one WebSocket open between the driver app and the backend, so the driver gets ride offers and ride/outstation updates instantly. **WebSocket** (a long-lived two-way connection. *Example:* a phone call, versus HTTP which is like sending letters). It auto-reconnects and sends a ping every 20 seconds. Screens `RideRequestScreen`, `DriverActiveRideScreen` and `DriverOutstationScreen` subscribe to it.

## 2. Imports, one by one
- `import AsyncStorage from '@react-native-async-storage/async-storage';` (line 1). Phone key-value storage that survives app restarts. *Example:* `await AsyncStorage.getItem('k')`. Used to read the saved login session.
- `import { environment } from '../../../config/environment';` (line 3). Project file `driver-app/src/config/environment`; holds `wsBaseUrl`, the server's WebSocket address.
- `import { DRIVER_SESSION_KEY } from '../../../services/apiClient';` (line 4). The storage key under which the session is saved.
- `import type { DriverRideOffer } from './rideMatchingService';` (line 5). A type only; no runtime code.

## 3. Walk through the code

**`DriverRealtimeEvent`** (lines 7-12). A **union type** (a value can be one of several shapes, joined by `|`). Each shape has `type` (a label) and `data`. *Example:* `{ type: 'ride.offer', data: {...offer} }`. TypeScript can narrow: after `event.type === 'ride.offer'`, it knows `data` is a `DriverRideOffer`.

**`Listener`, `ConnectionListener`** (lines 14-15): function types. A listener gets an event; a connection listener gets true/false.

**`class DriverRealtimeService`** (line 17). A **class** groups data and functions. `private` fields are hidden from outside.
- `socket`: the open WebSocket or null.
- `retryTimer`, `heartbeat`: timer handles (`ReturnType<typeof setTimeout>` means "whatever type setTimeout returns").
- `retryAttempt`: how many reconnect tries in a row.
- `listeners`, `connectionListeners`: `Set`s (lists without duplicates).
- `manuallyStopped`: true when nobody listens.

**`subscribe(listener, onConnectionChange?)`** (lines 26-36). Adds the listener(s), sets `manuallyStopped = false`, and starts `connect()`. Returns a function that removes them, and calls `stop()` when no listeners are left. *Example:* `const off = driverRealtimeService.subscribe(e => console.log(e)); off();`

**`connect()`** (lines 38-75), `async`, returns nothing.
1. Return if already connected or stopped (line 39).
2. Read the saved session text from `AsyncStorage` (line 40); return if none.
3. `JSON.parse` it and take `access_token`; if parsing fails, return (lines 42-44).
4. `new WebSocket(url, undefined, { headers: { Authorization: 'Bearer <token>' } })` (lines 47-51). It connects to `/api/v1/realtime/drivers/me`. The `Authorization` header with a **Bearer token** proves who the driver is. (The third argument is a React Native extension; browsers do not support it.)
5. `onopen` (52-56): reset retry count, tell listeners "connected", start a heartbeat that sends the text `ping` every 20 000 ms if the socket is open.
6. `onmessage` (57-64): parse JSON; if `type` is `ride.offer`, `ride.offer_cleared`, or starts with `ride.` or `outstation.`, call every listener. A broken message is ignored on purpose.
7. `onerror` (65): tell listeners "disconnected".
8. `onclose` (66-74): clear socket and heartbeat, tell listeners, and if listeners remain, retry after `delay = Math.min(8000, 500 * 2 ** retryAttempt++)`. That is **exponential backoff** (wait longer each time): 500, 1000, 2000, 4000, 8000, 8000 ms.

**`emitConnection`** (77-79): calls each connection listener.

**`stop()`** (81-87): marks stopped, clears timers, closes the socket.

**Export** (line 90): `export const driverRealtimeService = new DriverRealtimeService();` creates the single shared object (a **singleton**).

## 4. How data flows
```
Screen --subscribe(listener)--> service --connect()--> AsyncStorage (token)
service --WebSocket + Bearer token--> backend
backend --JSON {type,data}--> onmessage --> every listener --> screen setState
service --'ping' every 20s--> backend
```

## 5. Try it
Not directly runnable alone. In a screen, call `driverRealtimeService.subscribe(e => console.log(e.type))` and watch Metro logs (the React Native dev server output). Turn the backend off and on to watch reconnects.

## 6. Can it be better?
- Good: backoff, heartbeat, cleanup, bad frames ignored.
- Weak: the token is read once per connect; when it expires the socket just reconnects with the old token (no refresh); the heartbeat is not cleared before `onopen` creates a new one if events overlap; `retryTimer` is not cleared in `onclose` before setting a new one; a failed connect after `stop()` then `subscribe()` quickly can race; the checks in `onmessage` are redundant (`startsWith('ride.')` already covers the first two). Offers are lost if the app was closed (polling covers this elsewhere).
- Cleaner way: `if (message.type.startsWith('ride.') || message.type.startsWith('outstation.'))`.
- Security: the token is sent in a header, not in the URL, which is better for logs. Use `wss://` (encrypted) in production; check `environment.wsBaseUrl`.

## 7. Check yourself
1. What waiting time is used before the 4th reconnect try?
2. Why does `subscribe` return a function?
