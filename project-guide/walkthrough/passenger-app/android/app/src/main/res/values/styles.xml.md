# styles.xml

## 1. Purpose
This file defines the app's Android **theme**. A theme is a set of default look rules (colors, title bar) for all screens. The manifest uses `AppTheme` for the app (not in this batch).

## 2. Imports, one by one
None. The `parent=` attribute acts like inheritance.

## 3. Walk through the code
- `<resources>` (`styles.xml:1`): root tag.
- `<!-- ... -->` (line 3): an XML comment.
- `<style name="AppTheme" parent="Theme.AppCompat.DayNight.NoActionBar">` (line 4): makes a style called `AppTheme`. It copies a ready-made theme from the AppCompat library: `DayNight` follows the phone's light/dark mode; `NoActionBar` removes the default top bar (RN draws its own UI).
- `<item name="android:editTextBackground">@drawable/rn_edit_text_material</item>` (line 6): changes one setting: the background of text input fields. `@drawable/...` points to an image/shape resource that RN provides. It makes `TextInput` look the same on all Android versions.

## 4. How data flows
```
Manifest android:theme="@style/AppTheme" -> styles.xml -> every Activity uses it
```

## 5. Try it
Not directly runnable. Add `<item name="android:windowBackground">#000</item>`, rebuild, and the window behind the app turns black.

## 6. Can it be better?
- Good: minimal and standard.
- Weak: no brand colors (`colorPrimary`) set. Opinion: add them for a branded look.
- Security: none.

## 7. Check yourself
1. What does `NoActionBar` remove?
2. What does `parent` do?
