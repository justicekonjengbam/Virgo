# driver-app/android/app/src/main/res/values/styles.xml

## 1. Purpose
This file defines the visual theme of the Android driver app. A **theme** (a named bundle of colors and look rules for every screen. *Example:* "dark text on a white background") is picked in the Android manifest, which is the file `driver-app/android/app/src/main/AndroidManifest.xml`. Android reads this file at build time. No JavaScript calls it.

## 2. Imports, one by one
XML has no imports. This file only refers to two outside names:
- `Theme.AppCompat.DayNight.NoActionBar` (line 4) comes from the AndroidX AppCompat library. It is a ready-made theme that switches between light and dark by the phone setting and hides the default top bar.
- `@drawable/rn_edit_text_material` (line 6) is a small image/shape resource that React Native ships. It draws the underline of a text input.

## 3. Walk through the code, top to bottom
- `<resources>` (line 1) is the root tag. Android treats the file as a list of named values.
- `<style name="AppTheme" parent="...">` (line 4) makes a style called `AppTheme`. `parent` means "start from that theme, then change a few things". *Example:* copy a recipe, then add salt.
- `<item name="android:editTextBackground">@drawable/rn_edit_text_material</item>` (line 6) overrides one setting. Every text input uses that drawable as its background. Without it, the text input would use the AppCompat default look.
- The comment on line 3 and 5 is XML comment syntax `<!-- ... -->`. It has no effect.

No errors can occur at runtime. A wrong name makes the Android build fail, not the app.

## 4. How data flows
```
AndroidManifest.xml  --android:theme="@style/AppTheme"-->  styles.xml
        |                                                      |
   Android OS builds the Activity  <---- gets look rules ------+
```
I did not open the manifest in this task, so the exact attribute is "expected", not checked. Check with `rg -n "AppTheme" driver-app/android`.

## 5. Try it
Not directly runnable. It is used when you build the app: `cd driver-app && npx react-native run-android`. To see the effect, change the parent to `Theme.AppCompat.Light.NoActionBar` and rebuild. The app will stay light even when the phone is in dark mode.

## 6. Can it be better?
- Good: it is tiny and matches the React Native template.
- Weak: there is no color or status bar setting, so the app looks like the default template. A `values-night` folder is not present here (not checked).
- Cleaner way: add items such as `<item name="android:statusBarColor">@color/brand</item>` and define `brand` in a `colors.xml`.
- Security: nothing risky.

## 7. Check yourself
1. What does `parent` mean on line 4?
2. Which setting does line 6 change, and which widget does it affect?
