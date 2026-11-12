# passenger-app/android/app/src/main/AndroidManifest.xml

## 1. Purpose
The **manifest** (an XML file that tells Android what the app is, which screens it has and which permissions it needs. *Example:* "this app may use the internet") is read by Android when the app is installed and started. It points to `MainApplication` and `MainActivity` (Kotlin files in the same module, not read here).

## 2. Imports, one by one
No imports. Line 1 declares the XML namespace `xmlns:android="http://schemas.android.com/apk/res/android"`. This makes the `android:` prefix valid on attributes. It is a name label, not a web call.

## 3. Walk through the code, top to bottom
- `<uses-permission android:name="android.permission.INTERNET" />` (`AndroidManifest.xml:3`). Allows network access. Needed for the API and Firebase.
- `ACCESS_COARSE_LOCATION` (line 4) and `ACCESS_FINE_LOCATION` (line 5): approximate and exact GPS position. The app needs them for pickup location. These are "dangerous" permissions, so the app must also ask the user at run time.
- `<application ...>` (lines 7-28), the app:
  - `android:name=".MainApplication"`: the class that starts first.
  - `android:label="@string/app_name"`: the name under the icon. `@string/...` reads a value from the resource files.
  - `android:icon`, `android:roundIcon`: launcher icons.
  - `android:allowBackup="false"` (line 12): Android will not back up the app data to Google. Good for privacy.
  - `android:theme="@style/AppTheme"`: base look.
  - `android:usesCleartextTraffic="true"` (line 14): allows plain `http://` calls. Needed now because `.env.example` uses `http://10.0.2.2:8000`.
  - `android:supportsRtl="true"`: supports right-to-left languages.
- `<activity android:name=".MainActivity" ...>` (lines 16-27). An **activity** (one screen window of an Android app; React Native uses a single one for all screens).
  - `configChanges="keyboard|keyboardHidden|orientation|..."` (line 19): Android will not restart the activity on these changes. React Native handles them itself.
  - `launchMode="singleTask"` (line 20): only one copy of the activity exists.
  - `windowSoftInputMode="adjustResize"` (line 21): the screen shrinks when the keyboard opens.
  - `exported="true"` (line 22): other apps (the launcher) may start it. Required for the entry activity.
  - `<intent-filter>` with `MAIN` action and `LAUNCHER` category (lines 23-26): marks this as the screen to open when the user taps the app icon.

## 4. How data flows
```
user taps icon -> Android reads manifest -> intent-filter MAIN/LAUNCHER -> MainActivity -> MainApplication -> React Native -> App.tsx
```

## 5. Try it
```zsh
rg -n "uses-permission" passenger-app/android/app/src/main/AndroidManifest.xml
```
`rg -n` searches with line numbers. Expect three lines (INTERNET and two location permissions).

## 6. Can it be better?
- Good: only the needed permissions. Backups are off.
- Weak: `usesCleartextTraffic="true"` is on for every build, including release. No notification permission or foreground-service permission (probably fine for the passenger app; I am not sure).
- Cleaner way: move cleartext to a debug-only manifest at `android/app/src/debug/AndroidManifest.xml` and use `https` in release.
- Security: cleartext HTTP can be read on the network. Turn it off before production.

## 7. Check yourself
1. Which attribute decides which screen opens from the launcher icon?
2. Why is `usesCleartextTraffic` a risk in release?
