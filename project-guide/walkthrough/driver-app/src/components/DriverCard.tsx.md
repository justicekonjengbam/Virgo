# driver-app/src/components/DriverCard.tsx

## 1. Purpose
`DriverCard` is a white box with a border, rounded corners, a shadow and padding. Screens wrap content in it so every panel looks the same. It uses only React Native `View` and the theme.

## 2. Imports, one by one
- `import type { PropsWithChildren } from 'react';` (`DriverCard.tsx:1`) adds a `children` prop to a props type. *Example:* `<DriverCard><Text/></DriverCard>`.
- `import { StyleSheet, View, type ViewStyle } from 'react-native';` (`:2`) `View` is the basic box (like a `div`). `StyleSheet.create` builds a style table. `ViewStyle` is the type for box styles.
- `import { colors, radius, shadows, spacing } from '../theme';` (`:3`) design tokens (named constants for colors, corner sizes, shadow settings, gaps) from `driver-app/src/theme/tokens.ts`.

## 3. Walk through the code
`DriverCard.tsx:5-7`
```tsx
export function DriverCard({ children, style }: PropsWithChildren<{ style?: ViewStyle }>) {
  return <View style={[styles.card, style]}>{children}</View>;
}
```
- Input: `children` (what goes inside) and an optional `style` for one-off changes. Output: a `View`.
- The array `[styles.card, style]` merges: the caller's `style` overrides the card defaults. If `style` is `undefined`, React Native ignores it.

`DriverCard.tsx:8`
```ts
const styles = StyleSheet.create({ card: { ...shadows.card, backgroundColor: colors.surface, borderColor: colors.border, borderRadius: radius.lg, borderWidth: 1, padding: spacing.lg } });
```
- `StyleSheet.create` returns the same object, but React Native can check and optimize it.
- `...shadows.card` is the **spread** operator: it copies every key of the shadow object into this object.
- The rest sets fill color, a 1-point border, rounded corners (`radius.lg` = 16) and inside space (`spacing.lg` = 16), per `tokens.ts:30-31`.

## 4. How data flows
```
Screen --> <DriverCard style={{marginTop: 8}}>kids</DriverCard>
       --> View with [card styles, marginTop] --> screen
```

## 5. Try it
Not directly runnable alone. Wrap any text: `<DriverCard><DriverText>Trip</DriverText></DriverCard>` and run the app.

## 6. Can it be better?
- Good: very small, token based.
- Weak: `style` accepts only `ViewStyle`, not arrays. No `padding` option. The one-line style is hard to read.
- Cleaner way: format the style object over several lines, and type `style` as `StyleProp<ViewStyle>`.
- Security: none.

## 7. Check yourself
1. What does `...shadows.card` do?
2. How can a screen change the card's margin without editing this file?
