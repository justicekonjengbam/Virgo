# driver-app/android/app/build.gradle

## 1. Purpose
The **Gradle** build script (Gradle is Android's build tool; it turns code into an installable `.apk`) for the Android app module. Written in **Groovy** (a scripting language for Gradle). It sets the app id, versions, signing, React Native tasks, fonts and dependencies. Gradle runs it when you do `pnpm android`. It uses values from the root `android/build.gradle` (not in this batch) through `rootProject.ext`.

## 2. Imports, one by one
Gradle uses plugins and `apply from`, not imports.
- `apply plugin: "com.android.application"` (`build.gradle:1`). Makes this module an Android app.
- `"org.jetbrains.kotlin.android"` (line 2). Lets it compile Kotlin (`MainActivity.kt`).
- `"com.facebook.react"` (line 3). The React Native Gradle plugin: bundles JS, links native libraries.
- `"com.google.gms.google-services"` (line 4). Reads `google-services.json` to set up Firebase. The file itself is not in this batch.
- `apply from: project(':react-native-config').projectDir.getPath() + "/dotenv.gradle"` (line 5). Runs the script of `react-native-config` that reads `.env` (see `driver-app/.env.example`) and exposes it to the app.
- `apply from: file("../../node_modules/react-native-vector-icons/fonts.gradle")` (line 8). Copies icon fonts into Android assets.

## 3. Walk through the code
- Lines 12-14: `tasks.named("preBuild").configure { dependsOn("copyReactNativeVectorIconFonts") }`. `preBuild` is a task that runs before every build. This makes the font copy always run first, as the comment (lines 10-11) says React Native 0.86 no longer does it.
- `react { ... }` (lines 20-66). Config for the React Native plugin. Most lines are comments. Active lines: `root = file("../..")` (the `driver-app` folder), `reactNativeDir` (where the `react-native` package is), `hermesCommand = "C:/tmp/cabsure-hermes/hermesc.exe"` (line 59), and `autolinkLibrariesWithApp()` (line 65). **Hermes** (React Native's JavaScript engine; `hermesc` compiles JS to bytecode). The Hermes path is a Windows path, so on Arch Linux this will fail for release builds. **Autolinking** (the plugin finds installed native libraries and adds them automatically).
- Line 71: `def enableProguardInReleaseBuilds = true`. **Proguard/R8** (shrinks and obfuscates code in release builds).
- Line 84: `def jscFlavor = ...`. Fallback JavaScriptCore engine, used only if Hermes is off.
- `android { ... }` (lines 86-124):
  - `ndkVersion`, `buildToolsVersion`, `compileSdk` come from `rootProject.ext` (shared version numbers).
  - `namespace "com.driverapp"` (line 91) and `applicationId "com.driverapp"` (line 96): the package name and unique store id.
  - Line 93: `main.assets.srcDirs += ["../../src/assets"]` adds `driver-app/src/assets` (fonts such as Poppins) to the app assets.
  - Line 97: `resValue "string", "build_config_package", ...` creates a string resource.
  - Lines 98-99: min and target SDK (Android versions supported).
  - Lines 100-101: `versionCode 2` (integer, must rise each store upload), `versionName "1.1"` (shown to users).
  - `signingConfigs.debug` (lines 103-110): keystore file `debug.keystore` with the public default password `android`. That is the standard Android debug value, not a real secret.
  - `buildTypes` (lines 111-123): debug uses the debug key. Release also uses the debug key (line 118), with minify and shrink on, and rules from `proguard-rules.pro` (line 121).
- `dependencies` (lines 126-135): `react-android` (React Native itself), then Hermes if `hermesEnabled` (a property in `gradle.properties`) is true, else JSC.

## 4. How data flows
```
pnpm android --> Gradle reads settings.gradle + build.gradle
  --> plugins run (React Native bundles JS, Firebase reads json, dotenv reads .env)
  --> compile Kotlin + resources --> app-debug.apk --> emulator
```

## 5. Try it
```zsh
cd driver-app/android && ./gradlew assembleDebug
```
`./gradlew` is the Gradle wrapper script (downloads the right Gradle version). `assembleDebug` builds the debug APK. Expected: `BUILD SUCCESSFUL`, APK under `app/build/outputs/apk/debug/`. Needs the Android SDK and a Java version from mise.

## 6. Can it be better?
- Good: font task fix is documented, Proguard on, debug key not used by accident for secrets.
- Weak: release is signed with the debug key (line 118), so it cannot go to Google Play. Hermes path is hard-coded to a Windows folder (line 59). Version numbers are hard-coded.
- Cleaner way: add a `release` signing config reading from `~/.gradle/gradle.properties`; delete line 59 to use the default Hermes compiler (opinion: only if the default works for you).
- Security: a real release keystore and its passwords must never be committed. Write `<secret>` in docs.

## 7. Check yourself
1. Which line makes Firebase work, and which file does it read?
2. Why can this release build not be published to the Play Store yet?
