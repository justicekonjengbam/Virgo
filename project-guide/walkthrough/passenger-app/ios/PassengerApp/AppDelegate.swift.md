# passenger-app/ios/PassengerApp/AppDelegate.swift

## 1. Purpose
This is the first code that runs when the iOS app opens. It starts React Native, which then runs your JavaScript app from `index.js` / `App.tsx`. It is written in Swift (Apple's programming language). It is called by iOS itself and it calls the React Native libraries.

## 2. Imports, one by one
- `import UIKit` (`AppDelegate.swift:1`): Apple's library for screens, windows and app life cycle. Used for `UIWindow`, `UIResponder`. *Example:* `UIScreen.main.bounds` gives the screen size.
- `import React` (`:2`): the core React Native native library. Needed for `RCTBridge`, `RCTBundleURLProvider`.
- `import React_RCTAppDelegate` (`:3`): React Native's helper module with the ready-made factory and default delegate (`RCTReactNativeFactory`, `RCTDefaultReactNativeFactoryDelegate`).
- `import ReactAppDependencyProvider` (`:4`): generated code that lists the native modules of the installed npm packages (like maps, Firebase). *Example:* `RCTAppDependencyProvider()` knows which native modules to load.

All four come from libraries (installed via CocoaPods, the iOS package manager). None come from other project files.

## 3. Walk through the code, top to bottom
- `@main` (`:6`): an attribute that marks this class as the app entry point. (**Attribute**: a label in Swift that gives a special meaning. *Example:* `@main` = "start here".)
- `class AppDelegate: UIResponder, UIApplicationDelegate` (`:7`): the object iOS talks to about app events. `UIApplicationDelegate` is a protocol (a list of methods iOS may call).
- `var window: UIWindow?` (`:8`): the app's window. The `?` means it can be empty (`nil`) at first.
- `var reactNativeDelegate`, `var reactNativeFactory` (`:10-11`): they keep the two React objects alive. If they were only local variables, they would be freed at once.
- `func application(_:didFinishLaunchingWithOptions:) -> Bool` (`:13-33`): iOS calls this once, when launching is done.
  - `:17` `ReactNativeDelegate()` makes the delegate (defined below at line 36).
  - `:18` `RCTReactNativeFactory(delegate:)` makes the factory that builds React Native.
  - `:19` gives the delegate its `RCTAppDependencyProvider()`.
  - `:21-22` stores both objects.
  - `:24` `UIWindow(frame: UIScreen.main.bounds)` creates a full-screen window.
  - `:26-30` `factory.startReactNative(withModuleName: "PassengerApp", in: window, launchOptions:)` loads the JS bundle and shows the component registered as `"PassengerApp"`. This name must match the name registered in JavaScript (`AppRegistry.registerComponent`). I did not check that file here; check `passenger-app/index.js`.
  - `:32` `return true` tells iOS the launch worked.
- `class ReactNativeDelegate: RCTDefaultReactNativeFactoryDelegate` (`:36`): tells React Native where its JavaScript code is.
  - `sourceURL(for:)` (`:37-39`): old-style hook; it just calls `bundleURL()`.
  - `bundleURL()` (`:41-47`): `#if DEBUG` is a compile-time switch. In a debug build, it asks the Metro dev server (`RCTBundleURLProvider...jsBundleURL(forBundleRoot: "index")`) for the live bundle. In a release build, it loads the file `main.jsbundle` packed inside the app. It returns `URL?` (a URL or nil).

## 4. How data flows
```
iOS launches app -> AppDelegate.didFinishLaunching
  -> make ReactNativeDelegate + factory -> make window
  -> startReactNative("PassengerApp")
  -> delegate.bundleURL(): DEBUG ? Metro server : main.jsbundle
  -> JS runs -> screens appear
```

## 5. Try it
Not directly runnable on Arch Linux. It needs macOS and Xcode. On a Mac: `cd passenger-app && pnpm ios`.

## 6. Can it be better?
- Good: it follows the standard React Native template, so upgrades are easy.
- Weak: nothing custom here, so nothing to fix. The module name is a string; a typo gives a red screen at launch.
- Security: none here. Release builds should not point to a dev server; the `#if DEBUG` handles that.
- Note: the Android half of this app is the main target in `package.json` scripts, so iOS may be untested.

## 7. Check yourself
1. What is the difference between the DEBUG and release bundle source?
2. Why are `reactNativeDelegate` and `reactNativeFactory` stored in properties?
