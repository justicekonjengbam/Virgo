# DsCard.tsx

## 1. Purpose
A box with a background, border, round corners and padding, to group content (a ride summary, a selectable option). A **molecule** (a part built from simple parts; here it uses only a `View`). Exported by `design-system/index.ts:4`.

## 2. Imports, one by one
- `import type { ReactNode } from 'react';` (`DsCard.tsx:1`) type for children.
- `import { StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';` (`:2`). `View` is the layout box. `StyleProp<ViewStyle>` is the type of a box style.
- `import { colors, radius, shadows, spacing } from '../../../theme';` (`:4`) tokens from `theme/tokens.ts`.

## 3. Walk through the code
`type DsCardProps = { children: ReactNode; elevated?: boolean; style?: StyleProp<ViewStyle> };` (`:6`). `children` is whatever is placed inside the tags. `elevated` adds a shadow.

`export function DsCard({ children, elevated = false, style })` (`:9`) returns `<View style={[styles.card, elevated && shadows.card, style]}>{children}</View>` (`:10`). `elevated && shadows.card` adds the shadow only when `elevated` is true. Caller `style` comes last and can override.

`styles.card` (`:13`): surface color background, border color, large radius, border width 1, padding `spacing.lg`.

## 4. How data flows
```
Screen --<DsCard elevated>children</DsCard>--> View(styles.card + shadow) --> grouped content on screen
```

## 5. Try it
Not directly runnable. `<DsCard elevated><DsText>Hello</DsText></DsCard>`.

## 6. Can it be better?
- Good: small, flexible, overridable.
- Weak: not tappable, so "selectable options" need a wrapper `Pressable`. The whole `StyleSheet` is on one long line. No accessibility props.
- Cleaner: put each style key on its own line.
- Security: none.

## 7. Check yourself
1. What does `elevated && shadows.card` give when `elevated` is false?
2. Why is `style` last in the array?
