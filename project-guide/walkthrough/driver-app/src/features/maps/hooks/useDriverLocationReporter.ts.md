# useDriverLocationReporter.ts

## 1. Purpose
While the driver is online, this hook reads the phone's GPS position and sends it to the backend so ride matching can find nearby drivers. `DriverHomeScreen.tsx:29` calls it. It calls MapLibre's `LocationManager` and `rideMatchingService.updateLocation`.

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` (`driver-app/src/features/maps/hooks/useDriverLocationReporter.ts:1`): `useState` remembers a value; `useEffect` runs code when the component appears and when listed values change.
- `import { LocationManager, type GeolocationPosition } from '@maplibre/maplibre-react-native';` (line 2): **MapLibre React Native** is an open map library. `LocationManager` (a helper object that asks for GPS permission and streams positions). *Example:* `LocationManager.getCurrentPosition()` returns the position once. `GeolocationPosition` is the type of a position (coordinates plus extra data).
- `import { rideMatchingService } from '../../rides/services/rideMatchingService';` (line 4): project file. Its `updateLocation(position)` sends the position to the backend.

## 3. Walk through the code
**`useDriverLocationReporter(enabled: boolean)`** (line 6). Input: `enabled` (true when online). Output: `{ permissionDenied }`.
- Line 7: state `permissionDenied`, starts `false`.
- Line 8: `useEffect(..., [enabled])` reruns when `enabled` changes.
- Line 9: if not enabled, do nothing.
- Lines 10-11: `active` is a flag that says "this effect is still alive". `lastSentAt` stores the last send time in milliseconds.
- `report(position)` (line 12): skips if inactive or if less than 5000 ms (5 s) passed since the last send (**throttle**: limit how often something runs). Otherwise saves the time and calls `rideMatchingService.updateLocation(position)`. `.catch(() => undefined)` ignores network errors.
- Line 17: `LocationManager.requestPermissions()` shows the Android permission popup and returns `true` or `false`.
  - If the effect was cleaned up meanwhile, stop (line 18).
  - Save the result into state (line 19). If denied, stop.
  - `setMinDisplacement(10)` (line 21): only fire updates after the phone moves at least 10 metres.
  - `addListener(report)` (line 22): call `report` on every update.
  - `getCurrentPosition()` (line 23): get one position now so the backend learns the location without waiting for movement.
- Line 25: the **cleanup** function: sets `active = false` and removes the listener. It runs when `enabled` becomes false or the screen closes.

## 4. How data flows
```
GPS -> LocationManager -> report() [throttle 5 s] -> rideMatchingService.updateLocation -> backend
```

## 5. Try it
Not directly runnable. Run the app, go online, grant location. Watch the backend log for location updates about every 5 s while you move.

## 6. Can it be better?
- Good: cleanup is correct, throttle protects the server, denied state is shown to the user.
- Weak: failures are silent. Magic numbers 5000 and 10. Stops reporting when the app goes to the background (probably; no background service is used here, I am not sure). `LocationManager` is a global shared object, so `setMinDisplacement` affects other users of it.
- Cleaner way: `const SEND_EVERY_MS = 5_000;` as named constants.
- Security: location is sensitive personal data. It must be sent only over HTTPS and only while online. This hook respects the online flag.

## 7. Check yourself
1. Why is `active` needed in the cleanup?
2. What stops a position being sent twice within 5 seconds?
