# MainActivity.kt

## 1. Purpose
This file is the first screen (Android calls it an **Activity**) of the passenger app. An Activity is one window of an Android app. *Example:* the login screen of a bank app is one Activity. Here, `MainActivity` hosts the whole React Native app. Android starts it, and it starts the JavaScript code in `passenger-app/index.js`. It calls React Native classes only. The Android manifest (not in this batch) points to it.

## 2. Imports, one by one
All are third-party (React Native, "RN").
- `package com.passengerapp` (`MainActivity.kt:1`): the **package** is the folder-like name of this code. *Example:* `com.passengerapp.MainActivity` is its full name. It must match the app id.
- `import com.facebook.react.ReactActivity` (line 3): the RN base class for an Activity that shows RN. We extend it so we get all RN setup for free. It can also handle the hardware back button.
- `import com.facebook.react.ReactActivityDelegate` (line 4): a helper object that does the real work for the Activity. Used here as a return type.
- `import ...DefaultNewArchitectureEntryPoint.fabricEnabled` (line 5): a true/false flag. It says if RN **New Architecture** (the newer renderer called Fabric) is on. It is set by `newArchEnabled` in `gradle.properties`.
- `import ...DefaultReactActivityDelegate` (line 6): the standard delegate class that takes the flag above.

## 3. Walk through the code
- `class MainActivity : ReactActivity()` (line 8): Kotlin syntax. `:` means "extends". We make a new class from `ReactActivity`. The `()` calls its constructor.
- `override fun getMainComponentName(): String = "PassengerApp"` (line 14): **override** means we replace a method from the parent. It returns the name JavaScript registered. This must equal `name` in `app.json` and the name in `AppRegistry.registerComponent` (`index.js:6`). If they differ, you get a red screen "has not been registered".
- `override fun createReactActivityDelegate()` (line 20): builds the delegate. `DefaultReactActivityDelegate(this, mainComponentName, fabricEnabled)` gets the activity, the component name, and the Fabric flag. Returns a `ReactActivityDelegate`.
- The `/** ... */` blocks are documentation comments.

## 4. How data flows
```
Android OS --launch--> MainActivity --getMainComponentName "PassengerApp"--> ReactActivityDelegate
   --> runs JS bundle --> AppRegistry.registerComponent("PassengerApp") --> <App/> on screen
```

## 5. Try it
Not directly runnable. Run the app with `cd passenger-app && npx react-native run-android` (starts the build and installs on an emulator/phone). Expected: the app opens.

## 6. Can it be better?
- Good: it is the standard template, small and correct.
- Weak: the name `"PassengerApp"` is duplicated in three places (opinion: fine, RN requires it).
- Security: nothing risky.

## 7. Check yourself
1. What happens if `getMainComponentName` returns a different name than `app.json`?
2. What does `: ReactActivity()` mean in Kotlin?
