# app.json

## 1. Purpose
A tiny JSON config. It holds the app's registered name and a display name. `index.js` reads `name` to register the app. The native Android/iOS side must use the same name (`MainActivity.kt:14`).

## 2. Imports, one by one
None (JSON has no imports).

## 3. Walk through the code
- `"name": "PassengerApp"` (`app.json:2`): the key that identifies the root component. *Example:* `AppRegistry.registerComponent("PassengerApp", ...)`. Do not rename without changing native code.
- `"displayName": "CabApp Passenger"` (line 3): a human-friendly name. In plain RN, it is mostly informational (the real label is in `strings.xml`).

## 4. How data flows
```
app.json --import { name }--> index.js --> AppRegistry --> matches MainActivity.getMainComponentName
```

## 5. Try it
`jq .name /home/rem/projects/CabSure-Ride-Booking-Application/passenger-app/app.json` (`jq` reads JSON; `.name` picks the key). Output: `"PassengerApp"`.

## 6. Can it be better?
- Good: minimal.
- Weak: the display name differs from `strings.xml` ("PassengerApp"). Opinion: align them.
- Security: none.

## 7. Check yourself
1. Which three places must use the same name?
2. Does `displayName` change the label under the Android icon?
