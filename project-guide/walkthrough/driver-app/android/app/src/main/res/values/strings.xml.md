# driver-app/android/app/src/main/res/values/strings.xml

## 1. Purpose
An Android **resource file** (a file of named values the app reads by name, in `res/`). It holds the app name shown under the launcher icon. The manifest reads it with `@string/app_name` (`AndroidManifest.xml:9` and `:18`).

## 2. Imports, one by one
None.

## 3. Walk through the file
- `<resources>` (`strings.xml:1`): the root tag for all resources.
- `<string name="app_name">DriverApp</string>` (line 2): defines the string `app_name` with the text `DriverApp`. Change the text to rename the app on the phone. Do not change `name`, or the manifest breaks. This is the name shown to drivers, so a friendlier one like "CabSure Driver" may be better.

## 4. How data flows
```
Build --> aapt packs strings.xml --> manifest @string/app_name --> launcher label "DriverApp"
```

## 5. Try it
Not directly runnable. Change the text, rebuild, and look at the icon label on the emulator.

## 6. Can it be better?
- Good: tiny and standard.
- Weak: the display name is the internal project name, not branded.
- Cleaner way: `<string name="app_name">CabSure Driver</string>` (opinion).
- Security: none.

## 7. Check yourself
1. Which file refers to `app_name`?
2. What would you edit to rename the app on the phone?
