# driver-app/android/build.gradle

## 1. Purpose
This is the **root build file** of the Android part of the driver app. **Gradle** (the build tool for Android. *Example:* `./gradlew assembleDebug` makes an APK file) reads it first. It sets version numbers shared by all modules and lists the plugins needed to build. It works with `driver-app/android/settings.gradle` and `driver-app/android/app/build.gradle` (the second one was not part of this task).

## 2. Imports, one by one
Gradle files have no import lines here. The `classpath(...)` lines (lines 15-18) are the "imports" of build plugins:
- `com.android.tools.build:gradle` (line 15) is the Android Gradle Plugin. It knows how to build Android apps. No version is given. React Native's plugin supplies it (simplified; I did not trace exactly where).
- `com.facebook.react:react-native-gradle-plugin` (line 16) is React Native's plugin. It bundles the JavaScript and links native libraries. It comes from the `includeBuild` in `settings.gradle:1`.
- `org.jetbrains.kotlin:kotlin-gradle-plugin` (line 17) compiles Kotlin code, the language of `MainApplication.kt`.
- `com.google.gms:google-services:4.4.4` (line 18) reads `google-services.json` for Firebase (for example push messages). The version `4.4.4` is fixed here.

## 3. Walk through the code, top to bottom
- `buildscript { ... }` (line 1) is the setup block for Gradle itself, not the app.
- `ext { ... }` (lines 2-9) defines shared variables. **ext** (extra properties, like global constants. *Example:* `minSdkVersion = 24`).
  - `buildToolsVersion = "36.0.0"` (line 3) the version of Android's build tools.
  - `minSdkVersion = 24` (line 4) the oldest Android version that can install the app (Android 7.0).
  - `compileSdkVersion = 36` (line 5) the Android API the code is compiled against.
  - `targetSdkVersion = 36` (line 6) the Android version the app says it was tested for. Google Play checks it.
  - `ndkVersion = "27.1.12297006"` (line 7) the NDK (tool for C++ code), needed by React Native native parts.
  - `kotlinVersion = "2.1.20"` (line 8) the Kotlin compiler version.
- `repositories { google() mavenCentral() }` (lines 10-13) tell Gradle where to download the plugins: Google's server and Maven Central.
- `dependencies { classpath(...) }` (lines 14-19) lists the plugins above.
- `apply plugin: "com.facebook.react.rootproject"` (line 22) turns on React Native's root-project plugin. It sets up shared defaults for every module.

Errors: a missing download or wrong version makes `./gradlew` fail with "Could not resolve ...".

## 4. How data flows
```
./gradlew assembleDebug
   -> settings.gradle (which modules?)
   -> build.gradle (this file: versions + plugins)
   -> app/build.gradle (reads ext values like minSdkVersion)
   -> APK file
```

## 5. Try it
```zsh
cd driver-app/android
./gradlew tasks
```
`./gradlew` is the Gradle wrapper script (downloads the right Gradle). `tasks` lists what you can run. Expected: a long list that includes `assembleDebug`. It needs JDK and Android SDK installed.

## 6. Can it be better?
- Good: all versions are in one place. Matches the React Native template.
- Weak: `google-services` plugin is listed, so a `google-services.json` file is needed or the build fails (not checked here). Version `4.4.4` is hard-coded and may become old.
- Cleaner way: keep it, but run `npx react-native upgrade` style updates together, not one by one. (Opinion.)
- Security: `google-services.json` holds project keys. Do not share it publicly. Not shown here.

## 7. Check yourself
1. What does `minSdkVersion = 24` stop?
2. Why is `google()` in `repositories`?
