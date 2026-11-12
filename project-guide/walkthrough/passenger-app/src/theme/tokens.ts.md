# passenger-app/src/theme/tokens.ts

## 1. Purpose
This file holds the app's **design tokens** (named values for colour, space, corner roundness, text style and shadow, so every screen looks the same. *Example:* `colors.primary` is always the same blue). The comment on line 3 says they come from the Figma design export. Almost every screen imports them through `theme/index.ts`. It has no logic.

## 2. Imports, one by one
- `import type { TextStyle, ViewStyle } from 'react-native';` (line 1). Types only (erased at build). `TextStyle` describes text style fields like `fontSize`. `ViewStyle` describes box style fields like `shadowColor`. Used to check `typography` (line 69) and `shadows` (line 80).

## 3. Walk through the code
- `colors` (lines 4-28). Hex codes like `#2563EB` are colours (red, green, blue in base 16). Groups: `primary*` (brand blue, pressed, soft background, shadow), `background`, `surface` (cards), `surfaceMuted`, `text*` (primary, secondary, tertiary greys), `border`, `borderStrong`, status colours `success`, `warning`, `error`, `info` each with a `Soft` light version, `overlay` (dark see-through layer behind pop-ups), `transparent`, `white`, `black`. **`as const`** freezes the object so each value is its exact text, not just `string`. *Example:* `colors.primary` has type `'#2563EB'`.
- `spacing` (30-41). Gap sizes in device-independent pixels (**dp**, a size unit that looks the same on all screens): xxs 2, xs 4, sm 8, md 12, lg 16, xl 20, xxl 24, xxxl 32, huge 40, massive 48.
- `radius` (43-51). Corner roundness: none 0 up to xl 20, and `pill: 999` (big number that makes a full round end).
- `typography` (53-69). `family` names Poppins fonts. Then styles `display`, `h1`, `h2`, `h3`, `body`, `bodyMedium`, `label`, `caption`, `overline`, each with `fontSize`, `lineHeight`, `fontFamily` (`overline` also has `letterSpacing`). `satisfies Record<string, TextStyle | Record<string,string>>` makes TypeScript check the shape without widening the type.
- `TypographyVariant` (line 71): `Exclude<keyof typeof typography, 'family'>`. `keyof typeof typography` is the list of keys; `Exclude` removes `'family'`. Result: `'display' | 'h1' | ...`. `DsText` uses it for its `variant` prop.
- `elevation` (73-78). Android shadow depth numbers: 0, 2, 4, 8.
- `shadows` (80-103). A `Record<keyof typeof elevation, ViewStyle>`: for each name, the style. `elevation` is the Android shadow. `shadowColor`, `shadowOffset`, `shadowOpacity`, `shadowRadius` are the iOS shadow. `card` is soft, `floating` is strong.

Usage example: `{ backgroundColor: colors.surface, padding: spacing.lg, ...shadows.card }`.

## 4. How data flows
```
tokens.ts --colors/spacing/...--> theme/index.ts --> every screen's StyleSheet
```

## 5. Try it
Not directly runnable. In a screen: `const s = StyleSheet.create({ box: { padding: spacing.lg, ...shadows.card } })`. Run `cd passenger-app && npx tsc --noEmit` to check the types.

## 6. Can it be better?
- Good: central tokens, typed, `as const`, clear names.
- Weak: only a light theme (no dark mode). `typography.family` is used with inline `fontFamily` strings repeated (lines 60-68). `info` (`#2F68F4`) and `primary` are almost the same. The font files must be installed, or text falls back to the system font; I am not sure where they are linked (check `react-native.config.js` and the `assets/fonts` folder).
- Cleaner way: build `typography` from `typography.family.semibold` to avoid repeated strings.
- Security: none.

## 7. Check yourself
1. What does `as const` give you on `colors`?
2. What is the difference between `elevation` and the `shadow*` fields in `shadows`?
