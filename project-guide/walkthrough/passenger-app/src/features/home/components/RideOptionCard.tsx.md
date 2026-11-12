# RideOptionCard.tsx

## 1. Purpose
One tappable card for a ride type (name, arrival time, and fare when selected). It lifts up slightly when pressed. The Home screen shows several of them. It uses `ImagePlaceholder.tsx`.

## 2. Imports, one by one
- `import { useState } from 'react';` (1). Keeps a value between redraws.
- `import { Animated, Pressable, StyleSheet, View, type ImageSourcePropType } from 'react-native';` (2). `Animated` makes motion, `Pressable` is tappable, `View` a box, `StyleSheet` styles, `ImageSourcePropType` is a type for image sources.
- `DsCard, DsText` (3) from `components/design-system`.
- `colors, spacing` (4) from `theme`.
- `ImagePlaceholder` (5) from `./ImagePlaceholder`.

## 3. Walk through the code, top to bottom
- Lines 6-13: props. Required: `name`, `eta`, `fare` (all strings). Optional: `imageSource`, `selected`, `onPress`.
- Lines 15-22: defaults: `selected = false`.
- Line 23: `lift` is an `Animated.Value` starting at 0 (created once via `useState(() => ...)`).
- Lines 24-30: `animate(value)` runs `Animated.spring` (a bouncy motion toward `toValue`). `useNativeDriver: true` runs it on the native UI thread. `.start()` begins it.
- Lines 32-38: `Pressable`. `onPressIn` (finger down) calls `animate(1)`; `onPressOut` (finger up) calls `animate(0)`.
- Lines 39-48: `Animated.View` moves up by 4 px: `lift.interpolate({ inputRange: [0, 1], outputRange: [0, -4] })` maps 0 to 0 and 1 to -4 (negative Y is up).
- Lines 49-65: a `DsCard` with an extra border when `selected` (`selected && styles.selected`). `ImagePlaceholder` gets `label={`${name} image`}` (53). Then name, eta, and, only if selected, "Base fare: ₹ {fare}" (59-63; `&&` draws only when true).
- Lines 70-78: styles. `minWidth: 106` keeps cards from getting too small.

Example: `<RideOptionCard name="Mini" eta="3 min" fare="50" selected />` shows "Base fare: ₹ 50".

## 4. How data flows
```
Home -> name, eta, fare, selected, onPress -> RideOptionCard
press down -> lift 0->1 -> card moves up 4px; release -> back
tap -> onPress() -> Home updates the selected ride
```

## 5. Try it
Not directly runnable alone. Press a ride card on the Home screen.

## 6. Can it be better?
- Good: small animation, clear props.
- Weak: label becomes "Mini image image" (see ImagePlaceholder). No `accessibilityState={{ selected }}`, so screen readers cannot tell which is chosen. `₹` is hard coded. `fare` is a string, so formatting happens elsewhere.
- Cleaner way: add `accessibilityState={{ selected }}` on the Pressable (line 33).
- Security: none.

## 7. Check yourself
1. What does `interpolate` do with `inputRange [0,1]` and `outputRange [0,-4]`?
2. When is the fare line shown?
