# driver-app/ios/DriverApp/AppDelegate.swift

## 1. Purpose
This is the iOS start-up file written in **Swift** (Apple's programming language). When the iPhone launches the app, it first runs this code. The code creates a window and starts React Native, which then runs `driver-app/index.js`. It reads the module name `"DriverApp"` (same as `driver-app/app.json:2`).

## 2. Imports, one by one
- `import UIKit` (line 1). Apple's UI framework. Gives `UIWindow`, `UIScreen`, `UIApplicationDelegate`. *Example:* `UIScreen.main.bounds` is the screen size.
- `import React` (line 2). React Native's native core, for types like `RCTBridge`.
- `import React_RCTAppDelegate` (line 3). Helper classes for app start-up: `RCTReactNativeFactory`, `RCTDefaultReactNativeFactoryDelegate`.
- `import ReactAppDependencyProvider` (line 4). A generated module that supplies native modules (autolinking result) through `RCTAppDependencyProvider`.

## 3. Walk through the code, top to bottom
- `@main` (line 6). An **attribute** (a tag that gives the compiler special meaning). It marks this class as the program's entry point.
- `class AppDelegate: UIResponder, UIApplicationDelegate` (line 7). A **delegate** (an object the system calls on events. *Example:* "app finished launching"). `UIApplicationDelegate` is the protocol (a list of methods) for app events.
- `var window: UIWindow?` (line 8). The app's window. `?` means optional: it may be `nil` (empty) until created.
- `var reactNativeDelegate: ReactNativeDelegate?` and `var reactNativeFactory: RCTReactNativeFactory?` (lines 10-11). Stored so they are not freed from memory.
- `func application(_:didFinishLaunchingWithOptions:) -> Bool` (lines 13-16). iOS calls it once at launch. Input: the app and launch options (why it was opened). Output: `true` means "launch OK".
  - line 17 `let delegate = ReactNativeDelegate()` makes the delegate object (defined below).
  - line 18 `RCTReactNativeFactory(delegate: delegate)` makes the factory that builds the React Native runtime.
  - line 19 sets `delegate.dependencyProvider = RCTAppDependencyProvider()`, which connects autolinked native modules.
  - lines 21-22 store both in the properties.
  - line 24 `UIWindow(frame: UIScreen.main.bounds)` creates a full-screen window.
  - lines 26-30 `factory.startReactNative(withModuleName: "DriverApp", in: window, launchOptions:)` starts React Native, loads the JS bundle, and shows the registered component `DriverApp` in the window.
  - line 32 returns `true`.
- `class ReactNativeDelegate: RCTDefaultReactNativeFactoryDelegate` (line 36). Tells React Native where the JS bundle is.
  - `sourceURL(for:)` (lines 37-39) just returns `self.bundleURL()`.
  - `bundleURL()` (lines 41-47). `#if DEBUG` (line 42) is a compile-time switch. In Debug builds it asks Metro (`RCTBundleURLProvider...jsBundleURL(forBundleRoot: "index")`, line 43) for `index` over the network, so live reload works. In Release builds (`#else`, line 44) it loads `main.jsbundle` stored inside the app (line 45).

## 4. How data flows
```
iOS launches app
  -> AppDelegate.didFinishLaunching
  -> factory.startReactNative("DriverApp")
  -> ReactNativeDelegate.bundleURL()
        DEBUG:   http://<Mac>:8081/index.bundle (Metro)
        RELEASE: main.jsbundle in app
  -> index.js -> registerComponent("DriverApp") -> screen
```

## 5. Try it
Needs a Mac with Xcode, so not runnable on Arch Linux. On a Mac: `cd driver-app && npx react-native run-ios`.

## 6. Can it be better?
- Good: modern template; very small; debug/release split is correct.
- Weak: no push notification or Firebase setup lines here (if the app needs push on iOS, they would be needed; not checked). No location permission code here (that sits in `Info.plist`, not read).
- Cleaner way: none for the template.
- Security: Release uses a bundled file, so no network code load. Good.

## 7. Check yourself
1. What is the difference between Debug and Release in `bundleURL()`?
2. What string must match `app.json` and `index.js`?
