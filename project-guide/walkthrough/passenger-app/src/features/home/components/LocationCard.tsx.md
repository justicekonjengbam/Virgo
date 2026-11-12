# LocationCard.tsx

## 1. Purpose
A card on the Passenger home screen showing the pickup place and the destination. Tapping each row lets the user choose a place. The parent screen gives the places and tap handlers.

## 2. Imports, one by one
- `import { Pressable, StyleSheet, View } from 'react-native';` (1). `Pressable` is tappable, `View` is a box, `StyleSheet` builds styles.
- `MaterialCommunityIcons` (2): icons. *Example:* `name="map-marker"`.
- `DsCard, DsText` (4) from `components/design-system`: card and text.
- `colors, spacing` (5) from `theme`.
- `import type { LocationOption } from '../../booking/data/bookingApi';` (6): a type only (erased at build time) describing a place; it has at least a `name` (used on lines 20 and 25).

## 3. Walk through the code, top to bottom
- Line 9: component `LocationCard`. Props are typed inline: `pickup` and `destination` (a `LocationOption` or `null`), `onPickupPress`, `onDestinationPress`.
- Line 11: `DsCard elevated` is a raised card.
- Lines 12-16: left column: a blue pin, a thin vertical line (`connector`), a grey pin. It draws a route.
- Lines 18-21: pickup button. `accessibilityRole="button"` tells screen readers it is a button. `pickup?.name ?? 'Choose pickup'`: `?.` reads `name` only if `pickup` is not null; `??` gives the fallback text otherwise.
- Line 22: a divider line.
- Lines 23-26: destination button. Text is dark if chosen, grey if not; fallback "Where to?". `numberOfLines={1}` cuts long names to one line.
- Line 28: a chevron icon on the right.
- Lines 33-40: styles; `locations: { flex: 1 }` takes the middle space; `minHeight: 42` makes a comfortable tap area.

## 4. How data flows
```
Home screen: pickup, destination, handlers -> LocationCard
tap a row -> onPickupPress() / onDestinationPress() -> parent opens a picker
```

## 5. Try it
Not directly runnable alone. Seen on the Home screen.

## 6. Can it be better?
- Good: clear, accessible roles, fallback text.
- Weak: no `accessibilityLabel` that includes the current value; indentation of the inner Pressables is off (lines 19-20, 24-25); the chevron looks tappable but is not.
- Cleaner way: define a `LocationCardProps` type like other components.
- Security: none.

## 7. Check yourself
1. What does `pickup?.name ?? 'Choose pickup'` return when `pickup` is `null`?
2. Why is `LocationOption` imported with `import type`?
