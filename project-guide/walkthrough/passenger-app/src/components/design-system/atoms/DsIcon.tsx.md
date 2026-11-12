# DsIcon.tsx

## 1. Purpose
A tiny icon component that draws a text symbol (like an arrow or a tick) in a theme color. Callers say `name="arrowRight"` and never need to know which character is used. It lives in the atoms folder of the design system.

## 2. Imports, one by one
- `import { StyleSheet, Text, type StyleProp, type TextStyle } from 'react-native';` (`DsIcon.tsx:1`). `Text` draws text. `StyleSheet` stores styles. `StyleProp<TextStyle>` is the type for "any text style, or an array of them, or nothing" (types only, erased at build). *Example:* `style={{ marginLeft: 4 }}`.
- `import { colors } from '../../../theme';` (`:3`) the color tokens (`theme/tokens.ts`).

## 3. Walk through the code
`const glyphs = { arrowRight: '→', ... minus: '−' } as const;` (`:5-16`). A **glyph** is one drawn character. `as const` tells TypeScript the object is read-only and its keys and values are exact. Note: `phone` and `search` both use `⌕` (`:12-13`), so they look the same.

`export type IconName = keyof typeof glyphs;` (`:18`). `typeof glyphs` takes the type of the object, `keyof` takes its keys. Result: `'arrowRight' | 'arrowLeft' | ... | 'minus'`. This type is re-exported in `design-system/index.ts:2`.

`type DsIconProps` (`:20`): `name` required; `color`, `size`, `style` optional.

`export function DsIcon({ name, color = colors.textPrimary, size = 20, style })` (`:23`) returns `<Text style={[styles.base, { color, fontSize: size, lineHeight: size }, style]}>{glyphs[name]}</Text>`. `glyphs[name]` looks up the character: `glyphs['check']` is `'✓'`. Setting `lineHeight` equal to `fontSize` keeps the box tight. The caller `style` comes last so it wins.

`styles.base` (`:27`): font `'Poppins-Medium'` (a font that must be installed in the app) and `includeFontPadding: false` (Android only; removes extra space above and below text).

## 4. How data flows
```
Screen --name="check"--> DsIcon --glyphs['check']--> '✓' in a <Text> --> screen
```

## 5. Try it
Not directly runnable. `<DsIcon name="arrowRight" color="#fff" size={24} />` shows a white arrow.

## 6. Can it be better?
- Good: type-safe names, one place to change a symbol.
- Weak: `phone` uses a search symbol (bug-like); `location` `⌖` may not exist in every font and can show as a box. Text glyphs look different per phone. Other files (`RememberMe.tsx`) use a real icon library instead, so there are two icon systems.
- Cleaner (opinion): use `react-native-vector-icons` here and keep the same `IconName` keys, so callers do not change.
- Security: none.

## 7. Check yourself
1. How does `IconName` stop you from writing `name="home"`?
2. Why does `phone` look like `search`?
