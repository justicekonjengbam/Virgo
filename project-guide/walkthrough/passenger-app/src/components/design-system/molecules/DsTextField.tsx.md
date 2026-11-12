# DsTextField.tsx

## 1. Purpose
This file builds one text input box with an optional label, a help or error message, and optional icons on the left and right. It is called a "molecule" because it joins small parts (a label, an input, a message) into one unit. It sits in the design system folder (`passenger-app/src/components/design-system/molecules/`). It uses `DsText` from `../atoms/DsText` and the colors and sizes from `passenger-app/src/theme`. It is exported in `design-system/index.ts:6`, so screens import it from `components/design-system`.

## 2. Imports, one by one

Third-party (React and React Native):
- `import type { ReactNode } from 'react';` (`DsTextField.tsx:1`)
  - **React** (a library for building screens from small pieces called components. *Example:* a button is a component.) `ReactNode` is a TypeScript type that means "anything React can draw": text, a component, or nothing. `import type` means the import is only for type checking and is removed when the app is built.
  - Needed for the `leading` and `trailing` props, which hold icons.
  - Other types: `ReactElement`, `FC`.
- `import { StyleSheet, TextInput, View, type TextInputProps } from 'react-native';` (`:2`)
  - **React Native** (a library that draws real phone controls from React code.) `View` is a box (like a `div` on the web). `TextInput` is a typing box. `StyleSheet.create` makes a checked set of styles. `TextInputProps` is the type listing every prop a `TextInput` accepts (for example `value`, `onChangeText`, `placeholder`).
  - Needed to draw the box and to reuse all `TextInput` props.
  - Other things: `Pressable`, `ScrollView`.

Project imports:
- `import { colors, radius, spacing, typography } from '../../../theme';` (`:4`) from `passenger-app/src/theme`. These are the shared design numbers: colors, corner radius, gaps, text styles. *Example:* `spacing.xs` is a small gap.
- `import { DsText } from '../atoms/DsText';` (`:5`) the project text component. It picks a text style by `variant` and a `color`.

## 3. Walk through the code

### Props type (`:7`)
`type DsTextFieldProps = TextInputProps & { label?: string; helperText?: string; error?: string; leading?: ReactNode; trailing?: ReactNode };`
- **Props** (the inputs a component receives. *Example:* `<DsTextField label="Name" />` passes `label`.)
- `&` joins two types: everything `TextInput` accepts, plus five extra props. The `?` means optional.
- `label`: text shown above. `helperText`: grey hint below. `error`: red message below. `leading` and `trailing`: things placed inside the box on the left and right.

### The component (`:10`)
`export function DsTextField({ label, helperText, error, leading, trailing, editable = true, style, ...inputProps })`
- It takes the props object and pulls out named parts (**destructuring**. *Example:* `const { a } = { a: 1 }` gives `a = 1`).
- `editable = true` sets a default: if the caller gives nothing, the box can be typed in.
- `...inputProps` (the **rest** syntax) collects every other prop (`value`, `onChangeText`, `keyboardType`...) into one object so they can be passed on to `TextInput`.
- Output: a React element tree (what to draw).

Line 11: `const message = error ?? helperText;`. The `??` operator picks the left side unless it is `null` or `undefined`. So an error replaces the hint. *Example:* `error="Too short"` gives `"Too short"`; no error gives `helperText`.

Line 12 returns one long JSX expression. **JSX** (HTML-like syntax inside JavaScript. *Example:* `<View>hi</View>`). In order:
1. Outer `View` with `styles.root` (a vertical stack with a small gap).
2. `{label && <DsText variant="label" ...>}`: `&&` draws the label only if `label` is a non-empty string.
3. Inner `View` with an array of styles `[styles.field, !!error && styles.fieldError, !editable && styles.fieldDisabled]`. `!!error` turns text into true/false. When false, React Native ignores that array entry. So the red border shows only on error, and the muted background only when not editable.
4. `{leading}` draws the left accessory.
5. `<TextInput {...inputProps} accessibilityLabel={label} editable={editable} placeholderTextColor={colors.textTertiary} style={[styles.input, style]} />`. `{...inputProps}` spreads all the passed props in. `accessibilityLabel` is the text a screen reader speaks. `placeholderTextColor` colors the hint inside the empty box. `style` merges our style with the caller's style (the caller's wins because it is later).
6. `{trailing}` draws the right accessory.
7. `{message && <DsText variant="caption" color={error ? colors.error : colors.textSecondary}>...}`: shows the message in red for an error, grey for a hint.

Gotcha: the label is not tied to the input for focus, only through `accessibilityLabel` (`:12`).

### Styles (`:15`)
`StyleSheet.create({...})` returns the same object with checks. Notes:
- `root.gap: spacing.xs`: space between label, field and message.
- `field`: row layout (`flexDirection: 'row'`), centered items, 1 px border, `minHeight: 52`, side padding.
- `fieldError` swaps the border to the error color; `fieldDisabled` swaps the background.
- `input`: `...typography.body` copies the body font style; `flex: 1` makes the input fill the free space; `paddingVertical: 0` removes extra height on Android.

## 4. How data flows
```
Screen --props(label, value, onChangeText, error)--> DsTextField
   DsTextField --label--> DsText(label)
   DsTextField --inputProps--> TextInput  (user types)
   TextInput --onChangeText(text)--> Screen state
   DsTextField --error ?? helperText--> DsText(caption)
```

## 5. Try it
Not directly runnable alone. Use it inside a screen:
```tsx
<DsTextField label="Phone" value={phone} onChangeText={setPhone} error={phone ? undefined : 'Required'} />
```
Expected: a box with the label "Phone" above, and a red "Required" under it while empty. Run the app with `cd passenger-app && npx react-native run-android`.

## 6. Can it be better?
- Good: one place for focus, error and help style; accessibility label set; extra props pass through.
- Weak: the whole JSX is on one line (`:12`) and the styles are on one line (`:15`), which is hard to read and diff. The "focus" style that the comment promises (`:9`) is not implemented. There is no `accessibilityState` for the error.
- Cleaner way (opinion): split the JSX over lines.
```tsx
// before: <View>...</View> on one line
// after
return (
  <View style={styles.root}>
    {label && <DsText variant="label">{label}</DsText>}
    ...
  </View>
);
```
- Security: none here. If used for passwords, the caller must pass `secureTextEntry`.

## 7. Check yourself
1. What does `error ?? helperText` return when both are set?
2. Why is `...inputProps` used instead of listing every `TextInput` prop?
