# driver-app/src/features/dashboard/components/DriverDrawer.tsx

## 1. Purpose
The slide-in menu from the left side of the driver dashboard. It lists seven destinations plus Sign out, and animates open and closed. The dashboard screen (under `features/dashboard/screens/`) shows it and passes the callbacks.

## 2. Imports, one by one
- `import { Component } from 'react';` (line 1) React has two ways to write a component: a function (with hooks) or a **class** that extends `Component`. This file uses a class because it needs lifecycle methods. *Example:* `class A extends Component { render() { return <View/>; } }`.
- `import { Animated, Dimensions, Modal, Pressable, SafeAreaView, StyleSheet, View } from 'react-native';` (2) `Animated` makes smooth movement. `Dimensions.get('window')` gives the screen size. `Modal` draws content above everything. The rest: tap area, safe area, styles, box.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (3) icon font. *Example:* `name="logout"`.
- Project: `DriverText` (5); `colors, radius, shadows, spacing` from `src/theme` (6).

## 3. Walk through the code
**`DriverDrawerProps`** (8): `visible` (show or hide) and eight callbacks (`onClose`, `onOpenEarnings`, ...).

**`drawerWidth`** (9): 82 percent of screen width, at most 340. *Example:* width 400 gives 328.

**`menuItems`** (10-18): `[label, icon name]` pairs. `as const` locks the values.

**`class DriverDrawer`** (21):
- `translateX = new Animated.Value(-drawerWidth)` (22): an animated number. At `-drawerWidth` the drawer sits fully off the left edge. At 0 it is fully visible.
- `componentDidMount` (24): a **lifecycle method**, run once after the component first appears. If `visible` is already true, open.
- `componentDidUpdate(previousProps)` (28): runs after each change. If `visible` just changed from false to true, open.
- `open()` (32): reset to off-screen, then `Animated.timing(..., {toValue: 0, duration: 220, useNativeDriver: true}).start()` slides it in over 220 ms. `useNativeDriver` runs the animation on the phone's native side so it stays smooth.
- `dismiss(afterClose?)` (37): slide out over 180 ms. The `.start(({finished}) => ...)` callback runs when done. If the animation finished, call `onClose()` (parent sets `visible=false`) and then `afterClose?.()` (such as opening the next screen). Waiting for the slide first avoids a jump.
- `choose(label)` (45): chain of `if`s. "Dashboard" just closes. Others close and then call the matching callback.
- `render()` (55): a `Modal` (no built-in animation, transparent). `onRequestClose` handles the Android back button. Inside: an `overlay` (dim colour, row) containing the animated drawer (`transform: [{translateX}]`) and, to its right, a full-height `backdrop` `Pressable`. Tapping the dark area closes the drawer. The drawer has a top bar (close button, title, spacer), the menu list (the first item is highlighted, `index === 0 && styles.activeItem`), and a footer with Sign out (red, `colors.danger`) and "Version 0.0.1" (hard-coded).

**`styles`** (61): `footer` uses `marginTop: 'auto'` to push to the bottom. `shadows.floating` adds a shadow.

## 4. How data flows
```
Dashboard sets visible=true -> componentDidUpdate -> open() -> slide in
user taps "Earnings" -> choose -> dismiss(onOpenEarnings)
   -> slide out -> onClose() (parent hides) -> onOpenEarnings() (parent navigates)
```

## 5. Try it
Not directly runnable alone. In the app, tap the menu icon on the dashboard. Expect the drawer to slide in from the left in about 0.2 seconds.

## 6. Can it be better?
- Good: smooth native animation, correct close-then-navigate order, back button support.
- Weak: `drawerWidth` is computed once at load, so it will not update on rotation. If the animation is interrupted, `finished` is false and `onClose` never runs. The "active" item is always the first one. Menu labels are matched by text, so a typo breaks the link (use ids). The version is hard-coded. The JSX is one very long line. A class is older style (opinion: a function component with hooks is simpler).
- Cleaner way:
```ts
const menuItems = [{ id: 'earnings', label: 'Earnings', icon: 'wallet-outline', onPress: props.onOpenEarnings }]
```
- Security: none.

## 7. Check yourself
1. Why does `dismiss` wait for `finished` before calling `onClose`?
2. What number does `translateX` have when the drawer is hidden?
