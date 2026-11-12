# passenger-app/android/app/build.gradle

## 1. Purpose
**Gradle** (the Android build tool. It compiles the code, packs the files and makes the `.apk` installer. *Example:* `./gradlew assembleDebug`) reads this file to build the Passenger app module `app`. It is written in Groovy (a scripting language for the JVM). The command `pnpm android` ends up running it.

## 2. Imports, one by one
Gradle uses plugins, not imports.
- `apply plugin: "com.android.application"` (`build.gradle:1`). The Android plugin. Turns the module into an installable app.
- `apply plugin: "org.jetbrains.kotlin.android"` (line 2). Support for Kotlin (the language of `MainApplication`).
- `apply plugin: "com.facebook.react"` (line 3). The React Native Gradle plugin. Bundles the JS code and links native libraries.
- `apply plugin: "com.google.gms.google-services"` (line 4). Reads `google-services.json` for Firebase. The file itself is not read here; I am not sure where it sits (check `fd google-services.json passenger-app/android`).
- `apply from: project(':react-native-config').projectDir.getPath() + "/dotenv.gradle"` (line 5). Runs a script from the `react-native-config` library. It loads `.env` values (see `.env.example`).
- `apply from: file("../../node_modules/react-native-vector-icons/fonts.gradle")` (line 8). Copies icon fonts into Android assets (comment on line 7).

## 3. Walk through the code, top to bottom
- `react { ... }` (lines 14-60). Settings for the React Native plugin. Most lines are comments with defaults.
  - `root = file("../..")` (line 17): the project root (`passenger-app`). `reactNativeDir` (line 19): where `react-native` is installed.
  - `hermesCommand = "C:/tmp/cabsure-hermes/hermesc.exe"` (line 53). **Hermes** (the JavaScript engine of React Native; `hermesc` compiles JS to fast bytecode). This path is a Windows path. On Linux this build step will fail unless you change or remove the line.
  - `autolinkLibrariesWithApp()` (line 59). Finds native libraries in `node_modules` and links them. *Example:* Firebase.
- `def enableProguardInReleaseBuilds = true` (line 65). **Proguard** (shrinks and hides the Java bytecode in release builds). `true` means it is on.
- `def jscFlavor = '...jsc-android:2026004.+'` (line 78). The alternative JS engine (JavaScriptCore). Used only if Hermes is off.
- `android { ... }` (lines 80-121):
  - `ndkVersion`, `buildToolsVersion`, `compileSdk` come from `rootProject.ext` (the parent `android/build.gradle`, not read here).
  - `namespace "com.passengerapp"` (line 85) and `applicationId "com.passengerapp"` (line 87): the app's unique id on the phone and Play Store.
  - `resValue "string", "build_config_package", ...` (line 88): makes a string resource.
  - `minSdkVersion`, `targetSdkVersion` (lines 89-90): lowest and target Android versions.
  - `versionCode 2`, `versionName "1.1"` (lines 91-92). `versionCode` is a whole number that must grow with every store upload. `versionName` is shown to users.
  - `sourceSets.main.assets.srcDirs += ['../../src/assets']` (line 97): adds the folder with Poppins fonts so React Native finds `fonts/Poppins-*.ttf`.
  - `signingConfigs.debug` (lines 100-107): `storeFile file('cabapp-debug.keystore')` with a store password, key alias and key password, shown in the source as `<secret>` values. A **keystore** (a file with the key that signs your app). A debug keystore is normal for development, but its passwords are committed to git.
  - `buildTypes` (lines 108-120): `debug` signs with the debug key. `release` also uses the debug key (line 115). The comment says to make a real keystore for production. It turns on `minifyEnabled` and `shrinkResources` (line 116-117, remove unused code and resources) and uses proguard files (line 118).
- `dependencies` (lines 123-132): `implementation("com.facebook.react:react-android")` is the React Native core. `if (hermesEnabled.toBoolean())` picks Hermes (`hermes-android`) or the JSC flavor. `hermesEnabled` comes from `gradle.properties` (not read).

## 4. How data flows
```
pnpm android -> react-native CLI -> ./gradlew installDebug
   -> plugins -> .env loaded -> JS bundled -> Hermes compiled -> APK signed (debug key) -> phone
```

## 5. Try it
```zsh
cd passenger-app/android && ./gradlew assembleDebug
```
`./gradlew` is the Gradle wrapper script. `assembleDebug` builds the debug APK. Expect `BUILD SUCCESSFUL`. On Linux this may fail at the Hermes path (line 53).

## 6. Can it be better?
- Good: font and env setup have comments. Release uses shrinking.
- Weak: Hermes path is Windows-only and fixed. Release builds are signed with the debug key, so they cannot go to the Play Store. Keystore passwords are in git. `versionCode` is edited by hand.
- Cleaner way: read the Hermes path from `gradle.properties`, and read release keystore data from environment variables:
```groovy
storePassword System.getenv("RELEASE_STORE_PASSWORD")
```
- Security: committed signing passwords (even for debug) are a bad habit. Never reuse them for a release key.

## 7. Check yourself
1. Why can a release build from this file not be published as is?
2. What does `autolinkLibrariesWithApp()` do?
