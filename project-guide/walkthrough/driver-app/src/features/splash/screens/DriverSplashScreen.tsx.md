# DriverSplashScreen.tsx

## 1. Purpose
The welcome screen shown first in the driver app: logo, "Welcome", a tagline and a Continue button. The parent (app navigation) passes `onContinue` to move on. It has no data and no network calls.

## 2. Imports, one by one
- `import { SafeAreaView, StyleSheet, View } from 'react-native';` (line 1). React Native widgets: `SafeAreaView` (box that avoids the notch), `StyleSheet` (style helper), `View` (plain box).
- `import { DriverBrandMark } from '../../../components/brand/DriverBrandMark';` (line 2). The CabSure logo component. `size={118}` sets its size.
- `DriverButton` (line 3): styled button. `DriverText` (line 4): styled text. Both from `driver-app/src/components`.
- `colors, spacing` from `driver-app/src/theme` (line 5): shared design values.

## 3. Walk through the code
**`DriverSplashScreen({ onContinue })`** (line 7). Input: `onContinue`, a function with no inputs. Output: UI (a **component**: a function that returns what to draw).
- Layout: `content` box fills the screen and pushes the button to the bottom (`justifyContent: 'space-between'`). `hero` centres logo and texts and is pushed down by `marginTop: '45%'` (45% of the parent width).
- `<DriverButton label="Continue" onPress={onContinue}/>` calls `onContinue` when tapped.
**`styles`** (line 8): `flex: 1` fills the space; `gap` is space between children; `textAlign: 'center'` centres the tagline.

## 4. How data flows
```
user taps Continue -> DriverButton.onPress -> onContinue() -> parent changes the screen
```

## 5. Try it
Not directly runnable alone. Start the driver app (`cd driver-app && npx react-native start`, then run on a device). The first screen should be this one.

## 6. Can it be better?
- Good: tiny, no logic, easy to read.
- Weak: texts are hard-coded in English (no translation); the whole component is on one line; no auto-skip when the driver is already logged in (the parent may do it; not checked).
- Cleaner way: put the function body on several lines and move texts to a strings file if you add languages.
- Security: nothing risky.

## 7. Check yourself
1. What happens when Continue is pressed?
2. What does `justifyContent: 'space-between'` do here?
