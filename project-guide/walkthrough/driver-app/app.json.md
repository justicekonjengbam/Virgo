# driver-app/app.json

## 1. Purpose
A tiny JSON config file with the app's registered name and the name shown to people. `driver-app/index.js:3` imports `name` from it. The native code (iOS `AppDelegate.swift:27`) uses the same name string `"DriverApp"`.

## 2. Imports, one by one
JSON has no imports. Nothing here.

## 3. Walk through the code, top to bottom
- `"name": "DriverApp"` (line 2). This is the **component name** (the key React Native uses to find which JS app to start. *Example:* the phone says "start DriverApp", and JS answers). It must match what native code asks for. iOS asks for `"DriverApp"` in `AppDelegate.swift:27`. Android's `MainActivity` also names it (not read in this task).
- `"displayName": "CabApp Driver"` (line 3) a friendly name. This is the template field. I am not sure the app label on the phone uses it. The phone label usually comes from `strings.xml` on Android and `Info.plist` on iOS. Check with `rg -n "CabApp" driver-app/android driver-app/ios`.

## 4. How data flows
```
app.json --name--> index.js --registerComponent("DriverApp", ...)
                                 ^
iOS AppDelegate.startReactNative(withModuleName: "DriverApp")
```

## 5. Try it
```zsh
jq .name driver-app/app.json
```
`jq` reads JSON, `.name` picks one key. Expected output: `"DriverApp"`.

## 6. Can it be better?
- Good: simple, one source for the name in JS.
- Weak: the name `DriverApp` is repeated in native files, so a rename needs many edits. `displayName` (CabApp) differs from the repo name (CabSure), which can confuse. (Opinion.)
- Cleaner way: pick one product name and use it in the label files too.
- Security: nothing risky.

## 7. Check yourself
1. Which file reads `name` from this JSON?
2. What breaks if the iOS module name and `name` differ?
