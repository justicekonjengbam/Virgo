# driver-app/android/app/src/main/AndroidManifest.xml

## 1. Purpose
The **manifest** (an XML file that tells Android what the app is, what permissions it needs, and which screen starts first). Android reads it at install time. It points to `MainApplication` and `MainActivity` (Kotlin files) and uses `strings.xml`.

## 2. Imports, one by one
`xmlns:android="http://schemas.android.com/apk/res/android"` (`AndroidManifest.xml:1`) is an **XML namespace** (a label that makes the `android:` prefix valid). It is not downloaded; it is just a name.

## 3. Walk through the code
- Line 3 `INTERNET`: allows network calls to the backend.
- Lines 4-5 `ACCESS_COARSE_LOCATION`, `ACCESS_FINE_LOCATION`: approximate and exact GPS. The driver app needs them to share the driver's position. The user must still approve at runtime.
- `<application>` (lines 7-28):
  - `android:name=".MainApplication"` the class started first (`MainApplication.kt`).
  - `android:label="@string/app_name"` reads the name `DriverApp` from `strings.xml`.
  - `android:icon` and `roundIcon`: launcher icons in `mipmap` folders.
  - `android:allowBackup="false"`: Android will not copy app data to cloud backup.
  - `android:theme="@style/AppTheme"`: style from `res/values/styles.xml` (not in this batch).
  - `android:usesCleartextTraffic="true"` (line 14): allows plain `http://`, needed for `http://10.0.2.2:8000`. **Risky in production.**
  - `android:supportsRtl="true"`: supports right-to-left languages.
- `<activity>` (lines 16-27). **Activity** (one Android screen window). Here it is the only one, and React Native draws everything inside it.
  - `android:name=".MainActivity"` the Kotlin class.
  - `configChanges="..."` (line 19): tells Android not to restart the activity when keyboard, rotation, screen size or dark mode change; React handles it.
  - `launchMode="singleTask"`: only one instance of the app screen.
  - `windowSoftInputMode="adjustResize"`: shrink the window when the keyboard opens so inputs stay visible.
  - `exported="true"`: required because it has an intent filter; other apps (the launcher) may start it.
  - `<intent-filter>` (lines 23-26) with `MAIN` + `LAUNCHER`: marks this as the screen started when the user taps the app icon.

## 4. How data flows
```
User taps icon --> Android launcher --> reads manifest --> starts MainApplication, then MainActivity
MainActivity --> React Native --> JS App.tsx
```

## 5. Try it
Not directly runnable. After a build, view the merged manifest:
```zsh
rg -n "uses-permission" driver-app/android/app/build/intermediates/merged_manifests -g '*.xml'
```
`rg -n` searches text and prints line numbers. The folder exists only after a build; the exact path may vary.

## 6. Can it be better?
- Good: minimal, only needed permissions, backup off.
- Weak: cleartext traffic is on for all builds. No background location permission, so tracking may stop when the app is hidden (I am not sure if it is planned).
- Cleaner way: put `usesCleartextTraffic` in a `debug`-only manifest at `src/debug/AndroidManifest.xml` and leave it off for release.
- Security: cleartext HTTP can be read on the network; use HTTPS in production.

## 7. Check yourself
1. Which tag makes the app open when the icon is tapped?
2. Why is `usesCleartextTraffic` needed in development but unsafe in production?
