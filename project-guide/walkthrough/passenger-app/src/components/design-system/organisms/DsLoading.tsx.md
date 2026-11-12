# DsLoading.tsx

## 1. Purpose
This component shows a small spinner with a text label while something loads. It can be inline or fill the whole screen. It is exported in `design-system/index.ts:8`. `LoadingState.tsx` and `SavedAddressesScreen.tsx` use it.

## 2. Imports, one by one
- `import { ActivityIndicator, StyleSheet, View } from 'react-native';` (`DsLoading.tsx:1`). **React Native** draws native controls from React code. `ActivityIndicator` is the native spinning circle. `View` is a box. `StyleSheet.create` builds styles. Other example: `Switch`.
- `import { colors, spacing } from '../../../theme';` (`:3`) from `passenger-app/src/theme`: shared colors and gaps.
- `import { DsText } from '../atoms/DsText';` (`:4`) the project text component.

## 3. Walk through the code

### Props (`:6`)
`type DsLoadingProps = { label?: string; fullScreen?: boolean };` Both are optional.

### Component (`:9`)
`export function DsLoading({ label = 'Loading…', fullScreen = false })`
- Defaults: label `Loading…`, `fullScreen` false. *Example:* `<DsLoading />` shows "Loading…".

Line 10 returns:
- `View accessibilityLiveRegion="polite"` (Android feature: when the content changes, the screen reader speaks it without interrupting).
- `style={[styles.container, fullScreen && styles.fullScreen]}`: a style array; the second entry applies only if `fullScreen` is true. `fullScreen` is `flex: 1`, which makes the box grow to fill its parent.
- `<ActivityIndicator color={colors.primary} size="small" />` the spinner.
- `<DsText color={colors.textSecondary}>{label}</DsText>` the grey label.

### Styles (`:13`)
`container`: column, centered both ways, gap `spacing.md`.

## 4. How data flows
```
Screen (loading=true) --label, fullScreen--> DsLoading --> spinner + text
```

## 5. Try it
Not directly runnable alone. `<DsLoading fullScreen label="Loading saved addresses…" />` shows a centered spinner on the whole screen.

## 6. Can it be better?
- Good: small, with defaults; accessible live region.
- Weak: `accessibilityLiveRegion` is Android only (iOS ignores it). The `…` is a non-ASCII character in code; fine, but keep file encoding UTF-8. Style on one line.
- Cleaner way (opinion): add `accessibilityRole="progressbar"` so iOS users also hear it.
- Security: none.

## 7. Check yourself
1. What does `fullScreen && styles.fullScreen` do when `fullScreen` is false?
2. What label shows if none is passed?
