# ImagePlaceholder.tsx

## 1. Purpose
A box that shows an image if one is given, or a dashed box with an icon and label if not. `RideOptionCard.tsx` uses it for vehicle pictures that are not ready yet.

## 2. Imports, one by one
- `import { Image, StyleSheet, View, type ImageSourcePropType, type StyleProp, type ViewStyle } from 'react-native';` (1). `Image` draws a picture. `View` is a box. `StyleSheet` builds styles. The three `type` imports are TypeScript-only: `ImageSourcePropType` (what `source` may be, *Example:* `require('./car.png')`), `StyleProp<ViewStyle>` (a style the parent may pass).
- `MaterialCommunityIcons` (2): icon set. *Example:* `name="image-outline"`.
- `colors, radius, spacing` from `theme` (4).
- `DsText` from `components/design-system` (5).

## 3. Walk through the code, top to bottom
- Line 7: props: `label` (required), `source` (optional), `style` (optional).
- Lines 10-16: component. The outer `View` gets `accessibilityLabel="<label> image"` (12) for screen readers, and `style={[styles.container, style]}` (an array merges styles; later ones win).
- Line 13: ternary `source ? A : B`. If a source exists, draw `Image` with `resizeMode="contain"` (fit whole picture inside). Else draw `<>...</>` (a **fragment**, a wrapper that adds no box) with the icon and caption text.
- Lines 18-21: container is centered, has a dashed border, `overflow: 'hidden'` clips the image to rounded corners. `image` fills 100% width and height.

Example: `<ImagePlaceholder label="Mini" />` draws a dashed box saying "Mini".

## 4. How data flows
```
RideOptionCard -> label, source?, style -> ImagePlaceholder
source present -> Image    source missing -> icon + text
```

## 5. Try it
Not directly runnable alone. Seen on the Home screen ride cards.

## 6. Can it be better?
- Good: small, reusable, accessible.
- Weak: `RideOptionCard` passes `label={`${name} image`}`, so the accessibility label becomes "Mini image image" (line 12 adds " image" again). The inner `Image` and the outer View both carry labels.
- Cleaner way: pass just `name` as the label.
- Security: none.

## 7. Check yourself
1. What shows when `source` is missing?
2. Why does the screen reader text repeat the word "image"?
