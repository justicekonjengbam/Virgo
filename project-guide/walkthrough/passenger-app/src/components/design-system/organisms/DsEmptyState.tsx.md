# DsEmptyState.tsx

## 1. Purpose
This component shows a "nothing here" or "something failed" block: a title, a short text, an optional picture, and an optional button to try again. It is an "organism" (a bigger piece built from smaller ones). It is exported in `design-system/index.ts:7`. `SavedAddressesScreen.tsx` uses it for errors and for an empty list.

## 2. Imports, one by one
- `import type { ReactNode } from 'react';` (`DsEmptyState.tsx:1`). **React** is the library that builds screens from components. `ReactNode` is the type for "anything drawable" (text, a component, nothing). Used for the `illustration` prop. Type-only, removed at build.
- `import { StyleSheet, View } from 'react-native';` (`:2`). **React Native** draws native phone controls. `View` is a box. `StyleSheet.create` builds styles. Other example: `Image`.
- `import { colors, spacing } from '../../../theme';` (`:4`) from `passenger-app/src/theme`: shared colors and gaps.
- `import { DsButton } from '../atoms/DsButton';` (`:5`) the project button.
- `import { DsText } from '../atoms/DsText';` (`:6`) the project text.

## 3. Walk through the code

### Props type (`:8`)
`{ title: string; description?: string; illustration?: ReactNode; actionLabel?: string; onAction?: () => void }`
- `title` is required. The rest are optional (`?`).
- `onAction` is a **callback** (a function the parent gives, which this component calls later. *Example:* the parent passes `() => refresh()`).

### Component (`:11`)
`export function DsEmptyState({ title, description, illustration, actionLabel, onAction })` takes the props, returns a React element.

Line 12 returns:
- `<View accessibilityRole="summary" style={styles.container}>`: a box. `accessibilityRole="summary"` tells screen readers this block summarizes content.
- `{illustration}`: draws the picture if given; `undefined` draws nothing.
- `{<DsText variant="h2" ...>{title}</DsText>}`: heading text. The extra `{ }` braces around it are not needed (see section 6).
- `{description && <DsText color={colors.textSecondary} ...>}`: `&&` draws the text only if `description` is non-empty.
- `{actionLabel && onAction && <DsButton label={actionLabel} onPress={onAction} size="medium" />}`: the button shows only when both a label and a callback exist. `onPress` is called when the user taps.

### Styles (`:15`)
`container`: centered column, gap `spacing.md`, big padding `spacing.xxxl`. `title` and `description` center their text.

## 4. How data flows
```
Screen (error) --title, description, actionLabel, onAction--> DsEmptyState
user taps DsButton --> onAction() --> Screen calls refresh()
```

## 5. Try it
Not directly runnable alone. Example:
```tsx
<DsEmptyState title="No rides" description="Book your first ride." actionLabel="Book" onAction={() => {}} />
```
Expected: centered heading, grey text and a medium button.

## 6. Can it be better?
- Good: all parts optional except the title; button only shows when it can work; accessibility role set.
- Weak: `{<DsText ...>}` at `:12` has useless braces. All JSX and styles are on single long lines. `accessibilityRole="summary"` is rarely announced as hoped; I am not sure how TalkBack treats it (check on a device).
- Cleaner way (opinion): remove the braces and break lines.
```tsx
// before
{<DsText variant="h2">{title}</DsText>}
// after
<DsText variant="h2">{title}</DsText>
```
- Security: none.

## 7. Check yourself
1. When does the button appear?
2. What happens if `description` is an empty string?
