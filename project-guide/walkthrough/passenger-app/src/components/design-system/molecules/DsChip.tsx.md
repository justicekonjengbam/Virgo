# DsChip.tsx

## 1. Purpose
A small rounded label ("pill") for a status or a filter, such as "Active" or "Cash". It can be plain text or tappable. A **molecule**: it joins `Pressable` and `DsText`. Exported at `design-system/index.ts:5`.

## 2. Imports, one by one
- `import { Pressable, StyleSheet } from 'react-native';` (`DsChip.tsx:1`). `Pressable` handles taps; `StyleSheet` stores styles. *Example:* `<Pressable onPress={fn}>`.
- `import { colors, radius, spacing } from '../../../theme';` (`:3`) tokens (`theme/tokens.ts`).
- `import { DsText } from '../atoms/DsText';` (`:4`) themed text from the atoms folder.

## 3. Walk through the code
`type ChipTone = 'neutral' | 'primary' | 'success' | 'warning' | 'error';` (`:6`) a union of allowed color moods. `DsChipProps` (`:7`): `label` required; `selected`, `tone`, `onPress` optional.

`export function DsChip({ label, selected=false, tone='neutral', onPress })` (`:10`):
- `:11` `const palette = selected ? selectedPalette : palettes[tone];` the **ternary** `a ? b : c` picks `b` if `a` is true. Selected chips always use the blue filled palette; otherwise the tone decides.
- `:12` returns a `Pressable`. `accessibilityRole={onPress ? 'button' : 'text'}`: a button only if tappable. `disabled={!onPress}` turns off taps when there is no handler. Background comes from `palette.background`. Inside, `<DsText variant="caption" color={palette.text}>`.

`palettes` (`:15-17`) maps each tone to a background and text color (soft background, strong text). `selectedPalette` (`:18`) is primary background with white text. `styles.base` (`:19`): `alignSelf: 'flex-start'` (shrink to content width), pill radius, small padding.

Note: `palettes` and `styles` are defined after the function but used inside it. This is fine because the function runs later, after the file has loaded.

## 4. How data flows
```
Screen --label,tone,selected,onPress--> DsChip --pick palette--> Pressable + DsText
tap (if onPress) -> onPress() in Screen (e.g. change filter)
```

## 5. Try it
Not directly runnable. `<DsChip label="Paid" tone="success" />` is a static green pill. `<DsChip label="Today" selected onPress={() => {}} />` is a tappable blue pill.

## 6. Can it be better?
- Good: one API for static and tappable chips, accessible role switches.
- Weak: the JSX at `:12` and the `palettes` object at `:16` are long single lines. No pressed feedback. Selected state is not announced to screen readers (no `accessibilityState={{ selected }}`).
- Cleaner (opinion): add `accessibilityState={{ selected }}` and split the lines.
- Security: none.

## 7. Check yourself
1. What happens to `tone` when `selected` is true?
2. Why is `disabled={!onPress}` used?
