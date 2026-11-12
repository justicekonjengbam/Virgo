# DsButton.tsx

## 1. Purpose
The one button style for the whole passenger app. It has four looks, three sizes, a loading spinner and a disabled state. An **atom** is the smallest design-system part (*example:* a button; a card made of several atoms is a molecule). Used by `AuthPrompt.tsx` and many screens.

## 2. Imports, one by one
- `import type { ReactNode } from 'react';` (`DsButton.tsx:1`). **React** is the UI library. `ReactNode` is the type for anything React can draw (text, element, null). `import type` is erased at build time. *Example:* `leading={<Icon/>}`.
- `import { ActivityIndicator, Pressable, StyleSheet, View } from 'react-native';` (`:2`). `ActivityIndicator` is the spinning circle. `Pressable` handles taps and gives a `pressed` flag. `View` box. `StyleSheet` styles.
- `import { colors, radius, shadows, spacing } from '../../../theme';` (`:4`) tokens from `passenger-app/src/theme/tokens.ts`: colors, corner radius, shadow styles, gaps.
- `import { DsText } from './DsText';` (`:5`) themed text, same folder.

## 3. Walk through the code
`type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';` (`:7`). A **union type** (a value must be one of these strings; *example:* `'ghost'` is fine, `'red'` is a build error). `ButtonSize` (`:8`) likewise.

`DsButtonProps` (`:10-20`): `label` and `onPress` are required. The rest are optional: `variant`, `size`, `disabled`, `loading`, `leading` and `trailing` (items before and after the label), `accessibilityLabel` (text for screen readers).

`export function DsButton({...})` (`:23-33`) sets defaults: variant `primary`, size `large`, not disabled, not loading.
- `:34` `const inactive = disabled || loading;` the button cannot be tapped in either case.
- `:35` label color is white on `primary` and `danger` (filled backgrounds), blue (`colors.primary`) on the others.
- `:38-45` `<Pressable>`: `accessibilityLabel={accessibilityLabel ?? label}` falls back to the label. `accessibilityRole="button"`. `accessibilityState` reports disabled and busy. `disabled={inactive}` stops taps. `onPress` is the parent callback.
- `:44` `style` can be a **function** of the press state: `({ pressed }) => [...]`. The array merges: `styles.base`, `styles[size]` (looks up `styles.small` etc.), `styles[variant]`, `pressed && !inactive && styles.pressed` (fade while finger is down), `inactive && styles.disabled`.
- `:46` if `loading` show a spinner, else a row with `{leading}`, the `DsText` label (`variant="label"`), and `{trailing}`.

Styles (`:51-60`): `base` centers and rounds the corners. Minimum heights 36, 44, 52 points (touch targets). `primary` spreads `...shadows.card` (copies shadow keys) and uses the primary background. `pressed` opacity 0.82, `disabled` opacity 0.48.

Errors: none at run time.

## 4. How data flows
```
Screen --label,onPress,variant--> DsButton --> Pressable --> DsText
finger down: pressed=true -> opacity 0.82
finger up:   onPress() -> Screen handler
loading=true: spinner shown, taps ignored
```

## 5. Try it
Not directly runnable. `<DsButton label="Book ride" onPress={() => console.log('hi')} loading={false} />`. Tap and check the log.

## 6. Can it be better?
- Good: accessible, consistent, protects against double tap while loading, typed variants.
- Weak: one long line at `:44` and `:46` is hard to read. `ghost` and `secondary` text colors are the same blue. The `danger` label has no pressed color change other than opacity. Loading spinner replaces the label, so the button width may jump.
- Cleaner (opinion): split the JSX at `:46` into a small `Content` variable.
- Security: none.

## 7. Check yourself
1. Which two props make the button ignore taps?
2. What does `styles[variant]` do when `variant` is `'danger'`?
