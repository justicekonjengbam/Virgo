# DriverHeader.tsx

## 1. Purpose
This file draws the top bar of the driver home screen. It shows an avatar, a greeting with the driver's name, a bell button and a menu button. `DriverHomeScreen.tsx` (same feature, `screens/`) is the only caller. It calls the shared `DriverText` component and the theme values.

## 2. Imports, one by one
Third-party:
- `import { Pressable, StyleSheet, View } from 'react-native';` (`driver-app/src/features/dashboard/components/DriverHeader.tsx:1`)
  - **React Native** (a library that draws real phone screens from React code. *Example:* `<View>` becomes an Android view).
  - **View** (a box, like a `div` on the web). **Pressable** (a box that reacts to taps). **StyleSheet** (a helper that holds style objects).
  - Needed to build the layout and the two tap buttons.
  - It can also give `Text`, `Image`, `FlatList`.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (line 2)
  - An icon library. *Example:* `<MaterialCommunityIcons name="bell-outline" size={25} />` draws a bell.
  - Used for the avatar, bell and menu icons.

Project imports:
- `DriverText` from `driver-app/src/components/DriverText` (line 3): the app's shared text component. It takes `color`, `size`, `weight`.
- `colors, radius, shadows, spacing` from `driver-app/src/theme` (line 4): shared design values (colors, corner sizes, shadow styles, gaps).

## 3. Walk through the code
**`DriverHeader({ fullName, onMenuPress, onRequestPress })`** (line 6)
- A **component** (a function that returns what to draw. *Example:* `<DriverHeader fullName="Asha" .../>`).
- Inputs (props): `fullName` text, and two callback functions. A **callback** is a function the parent gives you to call later.
- Line 7: `new Date().getHours()` returns the current hour from 0 to 23.
- Line 8: a nested ternary picks the greeting. Under 12 is morning, under 17 is afternoon, otherwise evening. At hour 9 you get "Good morning".
- Line 9: returns the layout in JSX (HTML-like syntax inside JavaScript). Structure: header row > identity (avatar + texts) and actions (two buttons).
  - The bell `Pressable` has `accessibilityLabel="View ride request"` so screen readers can name it, and `onPress={onRequestPress}` runs the parent's function on tap.
  - The menu `Pressable` calls `onMenuPress`.
  - `Hello, {fullName}` shows the name inside curly braces.
- Line 11: `StyleSheet.create({...})` builds named styles. `flexDirection: 'row'` puts children side by side. `gap` adds space between children. `...shadows.card` copies the shadow settings into the object. `radius.pill` gives fully round corners.

No errors are raised here. If `fullName` is empty the line shows "Hello, ".

## 4. How data flows
```
DriverHomeScreen --(fullName, onMenuPress, onRequestPress)--> DriverHeader
user taps bell --> onRequestPress() --> DriverHomeScreen opens request screen
```

## 5. Try it
Not directly runnable. Run the app (`cd driver-app && npx react-native run-android`) and look at the top of the home screen. The greeting changes with the phone clock.

## 6. Can it be better?
- Good: small, takes plain props, has accessibility labels.
- Weak: the whole JSX is on one very long line (line 9), hard to read and diff. The avatar and name have no accessibility label. The `onRequestPress` label says "View ride request" but the icon is a bell, which is slightly unclear.
- Cleaner way: put each JSX element on its own line. Move the greeting into a small function `greetingFor(hour)`.
- Security: none.

## 7. Check yourself
1. What does the ternary on line 8 return at 14:00?
2. Which function runs when the driver taps the menu icon, and who owns it?
