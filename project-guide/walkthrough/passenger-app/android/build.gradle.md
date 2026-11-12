# android/build.gradle

## 1. Purpose
This is the top-level **Gradle** build file for the Android project. Gradle is the build tool for Android (like `make` or `npm run build`). This file sets shared version numbers and the tools used to build. The app module has its own `app/build.gradle` (not in this batch). Written in Groovy (a scripting language).

## 2. Imports, one by one
There are no import lines. The `classpath(...)` lines (below) work like imports of build tools.

## 3. Walk through the code
- `buildscript { ... }` (`build.gradle:1`): settings for Gradle itself, not for the app.
- `ext { ... }` (line 2): defines shared variables other build files read as `rootProject.ext.minSdkVersion`.
  - `buildToolsVersion = "36.0.0"` (line 3): version of the Android build tools.
  - `minSdkVersion = 24` (line 4): oldest Android supported (Android 7.0). Older phones cannot install the app.
  - `compileSdkVersion = 36` (line 5): Android API version used to compile code.
  - `targetSdkVersion = 36` (line 6): the Android version the app is tested for. It decides which new rules Android applies.
  - `ndkVersion = "27.1.12297006"` (line 7): NDK = Native Development Kit, compiles C++ code (RN needs it).
  - `kotlinVersion = "2.1.20"` (line 8): Kotlin compiler version.
- `repositories { google() mavenCentral() }` (lines 10-13): where to download build tools. `google()` is Google's Maven server; `mavenCentral()` is the big public one.
- `dependencies { classpath(...) }` (lines 14-19): build plugins to download:
  - `com.android.tools.build:gradle` (line 15): the Android Gradle Plugin (version set elsewhere by RN plugin).
  - `com.facebook.react:react-native-gradle-plugin` (line 16): RN's plugin (autolinking, bundling JS).
  - `org.jetbrains.kotlin:kotlin-gradle-plugin` (line 17): compiles Kotlin.
  - `com.google.gms:google-services:4.4.4` (line 18): plugin that reads `google-services.json` for Firebase (push notifications). Pinned to 4.4.4.
- `apply plugin: "com.facebook.react.rootproject"` (line 22): runs the RN root-project plugin that wires up all sub-projects.

## 4. How data flows
```
./gradlew -> settings.gradle (which modules?) -> build.gradle (versions, plugins) -> app/build.gradle -> APK
```

## 5. Try it
`cd passenger-app/android && ./gradlew --version` prints Gradle, Kotlin and JVM versions. `./gradlew tasks` lists tasks.

## 6. Can it be better?
- Good: versions are in one place.
- Weak: `google-services` is pinned while others are unpinned (set by RN). Opinion: fine.
- Security: `google-services.json` holds project keys; do not commit it if it has private values (I did not check it).

## 7. Check yourself
1. What does `minSdkVersion = 24` mean for users?
2. Why is `ext { }` useful?
