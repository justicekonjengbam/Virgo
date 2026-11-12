# driver-app/src/components/DriverButton.tsx

## 1. Purpose
`DriverButton` is the shared tappable button of the driver app. It has three looks (primary, secondary, danger), three sizes, a loading spinner and a disabled state. It calls `DriverText` for its label and reads the theme.

## 2. Imports, one by one
- `import type { ReactNode } from 'react';` (`DriverButton.tsx:1`) `ReactNode` is any thing React can draw (text, element, null). *Example:* an icon passed as `leading`. Type-only.
- `import { ActivityIndicator, Pressable, StyleSheet, View } from 'react-native';` (`:2`)
  - `ActivityIndicator` a spinning wheel.
  - `Pressable` a wrapper that reacts to taps and gives a `pressed` flag.
  - `StyleSheet` builds style tables. `View` is a box.
- `import { colors, radius, shadows, spacing } from '../theme';` (`:4`) design tokens from `driver-app/src/theme/tokens.ts`.
- `import { DriverText } from './DriverText';` (`:5`) the shared text component.

## 3. Walk through the code
`:7-15` type `DriverButtonProps`: `label` and `onPress` are required. `variant` (`'primary' | 'secondary' | 'danger'`), `size`, `leading` (an element shown before the label), `disabled`, `loading` are optional.

`:18` `export function DriverButton({...})` Defaults: `variant='primary'`, `size='large'`, `disabled=false`, `loading=false`.
- `:19` `const inactive = disabled || loading;` while loading the button also ignores taps.
- `:20` `textColor` is the primary blue for `secondary`, white otherwise (secondary has a pale background).
- `:21` The returned `Pressable` has:
  - `accessibilityLabel` / `accessibilityRole="button"` / `accessibilityState` so screen readers (TalkBack on Android) announce "label, button, busy/disabled".
  - `disabled={inactive}` blocks taps. `onPress` runs on tap.
  - `style={({ pressed }) => [...]}` Pressable accepts a function. It gets `pressed` (true during the tap). The array lists: base `styles.button`, size style (`styles[size]`), variant style (`styles[variant]`), and `styles.disabled` when `pressed && !inactive`.
  - Children: if `loading`, show the spinner; else a row `View` with `leading` and the label in `DriverText` (size 16, weight 700).

`:24-32` `StyleSheet.create`: center content, rounded corners (`radius.md`), minimum heights 36/44/56, primary has card shadow and blue fill, secondary has soft fill and 1-point blue border, danger uses error red, `content` is a row with a gap.

Example: `<DriverButton label="Go online" onPress={goOnline} loading={busy}/>`.

## 4. How data flows
```
Screen --label,onPress,variant--> DriverButton
 tap --> Pressable --> onPress() in screen
 loading? --> spinner, taps blocked
```

## 5. Try it
Not directly runnable alone. Render `<DriverButton label="Test" onPress={() => console.log('hi')}/>` in a screen. A tap logs `hi`. With `loading` it logs nothing.

## 6. Can it be better?
- Good: accessible, handles loading and disabled, typed.
- Weak: the style key `pressed` is defined (`:30`) but never used; the code uses `styles.disabled` (opacity 0.48) for the pressed look, which is likely a bug. The pressed look should use `styles.pressed`. The disabled look is not applied when `inactive` is true. The `danger` text color is white, fine. Line 21 is one very long line.
- Cleaner way:
```tsx
style={({ pressed }) => [styles.button, styles[size], styles[variant], inactive && styles.disabled, pressed && !inactive && styles.pressed]}
```
- Security: none.

## 7. Check yourself
1. What happens when `loading` is true?
2. Why is `styles.disabled` used for the pressed state, and what would you change?
