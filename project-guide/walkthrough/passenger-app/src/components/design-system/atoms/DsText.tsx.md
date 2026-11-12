# DsText.tsx

## 1. Purpose
The themed text component. Every piece of text in the passenger app should use it, so fonts and colors stay the same. It is an atom (smallest design-system part). Used by `DsButton.tsx`, `DsChip.tsx`, `AuthPrompt.tsx`, `RememberMe.tsx` and others.

## 2. Imports, one by one
- `import type { ReactNode } from 'react';` (`DsText.tsx:1`). Type for anything React can draw. Erased at build.
- `import { Text, type StyleProp, type TextStyle } from 'react-native';` (`:2`). `Text` is the only way to show text in React Native (plain strings outside it crash). `StyleProp<TextStyle>` is the style type.
- `import { colors, typography, type TypographyVariant } from '../../../theme';` (`:4`). From `theme/tokens.ts`. `typography` is an object of ready text styles (font, size) keyed by name, e.g. `typography.body`. `TypographyVariant` is the type of those names. *Example:* `typography['caption']`.

## 3. Walk through the code
`DsTextProps` (`:6-12`): `children` is required (the text). `variant`, `color`, `numberOfLines` (cut text with "..." after N lines), `style` are optional.

`export function DsText({ children='Dishant', variant='body', color=colors.textPrimary, numberOfLines, style })` (`:14-20`). Defaults: variant `body`, main text color. The default `children='Dishant'` (`:15`) looks like a leftover test value. It only shows if `children` is `undefined`. Since `children` is typed required, TypeScript normally blocks that.

Return (`:22-24`): `<Text numberOfLines={numberOfLines} style={[typography[variant], { color }, style]}>{children}</Text>`. Style order: variant style, then color, then caller `style` (last wins, so callers can override).

## 4. How data flows
```
DsButton --variant="label", color--> DsText --typography['label'] + color--> <Text> on screen
```

## 5. Try it
Not directly runnable. `<DsText variant="caption" color="#888" numberOfLines={1}>Hello</DsText>`.

## 6. Can it be better?
- Good: single place for text style, caller can override.
- Weak: the default `'Dishant'` is a stray name (a person's name) and no docblock. There is a blank line before `);` (`:25`), a style nit. A `style` with `color` is overridden after the `color` prop, which can surprise.
- Cleaner: remove the default `children='Dishant'`; add a short docblock.
- Security: none.

## 7. Check yourself
1. In what order are the three styles merged, and who wins?
2. When would the text "Dishant" appear?
