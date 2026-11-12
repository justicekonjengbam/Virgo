# MainApplication.kt

## 1. Purpose
This is the Android **Application** class. It is created once when the app process starts, before any screen. Its job is to set up React Native and list the native packages (plugins written in Kotlin/Java) used by the app. `MainActivity.kt` runs after it.

## 2. Imports, one by one
- `package com.passengerapp` (`MainApplication.kt:1`): the code's namespace.
- `import android.app.Application` (line 3): Android base class for the app-wide object. *Example:* a place to put start-up code.
- `import com.facebook.react.PackageList` (line 4): a class that is auto-generated at build time. It lists all native libraries found in `node_modules` (this is **autolinking**: the build finds native modules by itself).
- `import com.facebook.react.ReactApplication` (line 5): an interface (a promise to provide certain members). It says "this app uses RN" and requires `reactHost`.
- `import com.facebook.react.ReactHost` (line 6): the object that owns the RN runtime (the JS engine and the UI bridge).
- `import ...ReactNativeApplicationEntryPoint.loadReactNative` (line 7): a function that loads RN native libraries (the C++ code).
- `import ...DefaultReactHost.getDefaultReactHost` (line 8): a function that builds a standard `ReactHost`.

## 3. Walk through the code
- `class MainApplication : Application(), ReactApplication` (line 10): extends `Application` and implements `ReactApplication`.
- `override val reactHost: ReactHost by lazy { ... }` (line 12): `val` is a read-only value. `by lazy` means "build it the first time someone asks, then remember it". It saves start-up time.
- `getDefaultReactHost(context = applicationContext, packageList = ...)` (lines 13-20): named arguments. `applicationContext` is the Android app context (access to files, resources). `PackageList(this).packages` returns the list of native packages; `.apply { }` runs a block on that list and returns it. The block is empty except comments. You would write `add(MyReactNativePackage())` there for a package that autolinking cannot find.
- `override fun onCreate()` (line 23): Android calls this at process start. `super.onCreate()` runs the parent version. `loadReactNative(this)` (line 25) loads RN native code. Order matters: do it early.

## 4. How data flows
```
Android starts process -> MainApplication.onCreate -> loadReactNative
MainActivity needs host -> reactHost (lazy) -> PackageList -> getDefaultReactHost -> JS engine
```

## 5. Try it
Not directly runnable. Build with `cd passenger-app/android && ./gradlew assembleDebug` (`./gradlew` is the Gradle wrapper script; `assembleDebug` builds a debug APK). Expected: `BUILD SUCCESSFUL`.

## 6. Can it be better?
- Good: standard template; lazy host is efficient.
- Weak: none; do not edit unless adding a manual package.
- Security: none.

## 7. Check yourself
1. What does `by lazy` do?
2. When would you put code inside `.apply { }`?
