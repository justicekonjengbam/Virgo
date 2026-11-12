# strings.xml

## 1. Purpose
Android keeps text in resource files. This file holds one text: the app name shown under the icon and in the app list. It sits in `res/values/`, the default language folder. Android code reads it as `@string/app_name` (the manifest does this; not in this batch).

## 2. Imports, one by one
None. XML has no imports.

## 3. Walk through the code
- `<resources>` (`strings.xml:1`): the root tag. Everything inside is a resource.
- `<string name="app_name">PassengerApp</string>` (line 2): a text resource. `name` is the key; the text between tags is the value. *Example:* to show "CabSure" on the phone, change `PassengerApp` to `CabSure`.

## 4. How data flows
```
AndroidManifest android:label="@string/app_name" -> strings.xml -> "PassengerApp" under the icon
```

## 5. Try it
Not directly runnable. Change the text, rebuild with `npx react-native run-android`, check the launcher label.

## 6. Can it be better?
- Good: simple.
- Weak: `app.json` says displayName "CabApp Passenger", but this says "PassengerApp". Names are not consistent (opinion: use a user-friendly name here).
- Security: none.

## 7. Check yourself
1. Where does the label under the app icon come from?
2. Which file would you add a translated name to?
