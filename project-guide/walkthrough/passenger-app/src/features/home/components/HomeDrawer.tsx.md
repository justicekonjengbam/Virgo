# HomeDrawer.tsx

## 1. Purpose
The slide-in left menu of the passenger app. It lists six destinations and a Logout button. A parent home screen passes `visible`, `activeDestination` and callbacks. It uses `BrandMark`, `DsText`, and the theme. Most of the code is on very long lines (14-21), so this guide splits them.

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` (1). `useState` keeps a value; `useEffect` runs code when values change.
- `import { Animated, Dimensions, Modal, Pressable, SafeAreaView, StyleSheet, View } from 'react-native';` (2). `Animated` makes smooth motion (*Example:* slide a box). `Dimensions` reads screen size. `Modal` draws above everything. `Pressable` is tappable. `SafeAreaView` avoids notches. `StyleSheet` builds styles. `View` is a box.
- `MaterialCommunityIcons` (3): icon set. *Example:* `name="logout"`.
- `BrandMark` (4) from `components/auth/BrandMark`: the logo.
- `DsText` (5) from `components/design-system`: styled text.
- `colors, radius, shadows, spacing` (6) from `theme`: design values.

## 3. Walk through the code, top to bottom
- Line 8: `DrawerDestination` union: `'home' | 'rides' | 'addresses' | 'emergency' | 'support' | 'settings'`.
- Line 9: `HomeDrawerProps`: `visible`, `activeDestination`, `onClose`, `onLogout`, `onNavigate`.
- Line 10: `navigationItems`: a list of `[label, icon, destination]` triples. `as const` makes TypeScript treat the values as exact fixed words, so `destination` is typed correctly.
- Line 11: `drawerWidth` = 80% of the screen width. *Example:* 400px screen gives 320.
- Line 15: `translateX` is an `Animated.Value` (a number React Native can animate on the native side) starting at `-drawerWidth` (hidden off-screen left). `useState(() => new ...)` creates it once.
- Line 16: effect. When `visible` becomes true: reset to hidden, then `Animated.timing(translateX, { toValue: 0, duration: 220, useNativeDriver: true }).start()` slides it in over 220 ms. `useNativeDriver: true` runs the animation on the phone's UI thread for smoothness.
- Line 17: `dismiss(afterClose?)` slides back out in 180 ms. `.start(({ finished }) => ...)` runs a callback when done. If the animation finished, it calls `onClose()` then `afterClose?.()` (`?.()` calls only if given). So navigation happens after the drawer closes.
- Line 18: `selected(dest)` tells if a destination is the active one.
- Line 19: the view. `Modal` with `transparent` and `animationType="none"` (we animate ourselves). `onRequestClose` handles the Android back button. Inside: an overlay row with the animated drawer on the left (`transform: [{ translateX }]` moves it) and a `backdrop` Pressable on the right that closes on tap. In the drawer: a close button, `BrandMark`, a spacer, the menu from `navigationItems.map(...)` (`key={label}`, tap runs `dismiss(() => onNavigate(destination))`, active item has bigger `h3` text and a soft color), and a footer with Logout (`dismiss(onLogout)`) and "Version 0.0.1".
- Line 21: styles. `...shadows.floating` spreads shadow settings. `marginTop: 'auto'` pushes the footer down.

## 4. How data flows
```
Parent sets visible=true -> effect -> slide in
tap "My Rides" -> dismiss(cb) -> slide out -> onClose() -> onNavigate('rides')
tap Logout -> dismiss(onLogout) -> slide out -> onClose() -> onLogout()
```

## 5. Try it
Not directly runnable alone. Run the passenger app, tap the menu icon on Home, tap an item.

## 6. Can it be better?
- Good: smooth, closes before navigating, has accessibility labels (Close menu, Log out).
- Weak: minified-looking long lines are hard to read. Menu items have no `accessibilityLabel`. `Dimensions.get` is read once at load, so it will not update on rotation. The version "0.0.1" is hard coded. The `finished` check means that if a new animation interrupts, `onClose` never runs.
- Cleaner way: one JSX element per line, and read the version from `package.json` or config.
- Security: none directly. Logout logic lives in the parent (not checked here).

## 7. Check yourself
1. Why does `dismiss` call `onNavigate` only after the animation ends?
2. What does `as const` do to `navigationItems`?
