# driver-app/android/app/src/main/java/com/driverapp/MainActivity.kt

## 1. Purpose
The Android screen (Activity) that hosts the React Native UI. It is named in the manifest (`AndroidManifest.xml:17`). It tells React Native which JavaScript component to start: `"DriverApp"`. Written in **Kotlin** (a JVM language Android uses. *Example:* `val x = 1`).

## 2. Imports, one by one
All are project-external React Native classes in `com.facebook.react`.
- `package com.driverapp` (`MainActivity.kt:1`): the folder/namespace this file belongs to (matches `namespace` in build.gradle).
- `ReactActivity` (line 3): base class of an Activity that shows React Native. *Example:* it creates the root view and handles back button.
- `ReactActivityDelegate` (line 4): helper object that does the real work for the Activity. Used here as a return type.
- `DefaultNewArchitectureEntryPoint.fabricEnabled` (line 5): a boolean flag, true if React Native's **New Architecture** (the newer renderer called Fabric) is on.
- `DefaultReactActivityDelegate` (line 6): the standard delegate implementation.

## 3. Walk through the code
- `class MainActivity : ReactActivity()` (line 8). The `:` means "extends". It inherits all the behavior.
- `override fun getMainComponentName(): String = "DriverApp"` (line 14). `override` replaces the parent's version. Returns the name registered in JavaScript with `AppRegistry.registerComponent('DriverApp', ...)` (in `driver-app/index.js`, not in this batch; check it). If the names differ, you get a red error screen.
- `override fun createReactActivityDelegate(): ReactActivityDelegate = DefaultReactActivityDelegate(this, mainComponentName, fabricEnabled)` (lines 20-21). Builds the delegate with: this activity, the component name, and the Fabric flag. Returns the delegate.

## 4. How data flows
```
Android --> MainActivity.onCreate (parent) --> createReactActivityDelegate()
Delegate --> asks getMainComponentName() = "DriverApp" --> runs JS component --> App.tsx
```

## 5. Try it
Not directly runnable. Check the name match:
```zsh
rg -n "DriverApp" driver-app/index.js driver-app/app.json
```
Expected: the registered name `DriverApp`.

## 6. Can it be better?
- Good: it is the standard React Native template; nothing extra.
- Weak: nothing to fix. The name is a magic string that must match JS.
- Security: none.

## 7. Check yourself
1. What breaks if `getMainComponentName` returns a different name than JS registers?
2. What does `fabricEnabled` control?
