# passengerRealtimeService.ts

File: `passenger-app/src/features/booking/services/passengerRealtimeService.ts` (66 lines)

## 1. Purpose
This file opens a **WebSocket** (a long-lived two-way connection to the server, so the server can push news without being asked. *Example:* a chat app) for one ride. The backend pushes ride status changes and driver locations. `BookingStatusScreen.tsx:19` calls `subscribeToRide`. The backend side is under `/api/v1/realtime/passengers/rides/{id}` (I did not read it here).

## 2. Imports, one by one
- `import AsyncStorage from '@react-native-async-storage/async-storage';` the phone's key-value store (*Example:* `await AsyncStorage.getItem('k')`). Used to read the saved login token.
- `import { environment } from '../../../config/environment';` project file `passenger-app/src/config/environment.ts`. `environment.wsBaseUrl` (line 14 there) is the server address, made from the API URL by replacing `http` with `ws`.
- `import { PASSENGER_SESSION_KEY } from '../../../services/apiClient';` the storage key name (apiClient.ts:6).
- `import type { RideStatus } from '../data/bookingApi';` a type only (erased at build time); shape in bookingApi.ts:6.

## 3. Walk through the code, top to bottom

### Types (7-9)
`RideStatusListener` and `ConnectionListener` are callback function types. A **callback** is a function you hand to someone else to call later. `DriverLocation` is the shape of a driver position message: coordinates, heading, accuracy, time.

### `subscribeToRide(rideId, onStatus, onConnectionChange, onDriverLocation?)` (11-66)
Returns a function (`() => void`) that stops everything. This "return a cleanup function" style is what React's `useEffect` expects.

State variables (17-21): `socket`, `retryTimer`, `heartbeat`, `stopped` (set when the caller unsubscribes), `retryAttempt` (counts failures).

`connect` (23-57), `async`:
1. Read the saved session text (24). If `stopped` or nothing saved, return.
2. `JSON.parse` the text and pick `access_token` (26-29). Bad JSON or missing token: give up quietly.
3. `new WebSocket(url, undefined, { headers: { Authorization: 'Bearer <token>' } })` (31-35). The third argument is a React Native extension that allows custom headers. The server uses this header to know who the passenger is. Browsers do not allow this, but React Native does.
4. `onopen` (36-40): reset `retryAttempt`, report connected, and start a **heartbeat**: every 20 s (`20_000` ms) send the text `'ping'` if the socket is open, so idle connections are not dropped.
5. `onmessage` (41-47): `JSON.parse(event.data)` gives `{ type, data }`. If `type` is `'ride.status'` call `onStatus`; if `'driver.location'` call `onDriverLocation`. Bad frames are ignored by the empty-ish `catch`.
6. `onerror` (48): report not connected.
7. `onclose` (49-56): report not connected, stop the heartbeat, and if not `stopped` schedule a reconnect. **Exponential backoff**: `Math.min(8000, 500 * 2 ** retryAttempt++)` waits 500, 1000, 2000, 4000, 8000, 8000... ms. `2 ** n` is "2 to the power n"; `n++` adds 1 after use.

Line 59 starts the first connection. Lines 60-65 return the cleanup: set `stopped`, clear timers, `socket?.close()` (`?.` means "only if not null").

Errors: none are thrown out. Failures become `onConnectionChange(false)`.

## 4. How data flows
```
BookingStatusScreen --subscribeToRide--> read token (AsyncStorage)
   --> WebSocket ws://.../realtime/passengers/rides/7  (Authorization header)
Backend --{"type":"ride.status","data":{...}}--> onmessage --> onStatus --> setStatus (screen redraws)
Backend --{"type":"driver.location",...}------> onDriverLocation --> setDriverLocation (map moves)
close/error --> onConnectionChange(false) --> retry with backoff
```

## 5. Try it
Not directly runnable (React Native only). To see messages, run the app on a ride and watch Metro logs, or test the server with `websocat` (if installed):
```zsh
websocat -H "Authorization: Bearer <secret>" ws://localhost:8000/api/v1/realtime/passengers/rides/1
```
`-H` adds a header. Expect JSON lines with `"type"`.

## 6. Can it be better?
- Good: automatic reconnect with backoff; cleanup function; ignores bad messages.
- Weak: after a reconnect the old `socket` handlers are not removed (they are replaced because a new socket is made, so this is minor); `heartbeat` may start twice if `onopen` fires again before `onclose`; the token is read once per connect and an expired token is never refreshed; `onclose` after `onerror` runs both (harmless); retries never stop; a 401 close still retries forever; no tests.
- Cleaner way (opinion): stop retrying after an auth rejection (close code 1008 or 4401, check the backend), and clear `heartbeat` at the start of `onopen`.
- Security: the token goes in a header, not in the URL (good, URLs get logged).

## 7. Check yourself
1. What waits happen on the 1st, 2nd and 4th reconnect attempts?
2. What does the function returned by `subscribeToRide` do, and who calls it?
