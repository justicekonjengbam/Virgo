# driver-app/src/components/DriverTextField.tsx

## 1. Purpose
A labelled text input used by all driver forms. It shows a label, an input box with optional icons on the left and right, a blue border that thickens on focus, a red border on error, and a message below. It uses `DriverText` and the theme.

## 2. Imports, one by one
- `import { useState, type ReactNode } from 'react';` (`DriverTextField.tsx:1`) `useState` is a React **hook** (a function that gives a component memory. *Example:* `const [n, setN] = useState(0)`). `ReactNode` types things React can draw.
- `import { StyleSheet, TextInput, View } from 'react-native';` (`:2`) `TextInput` is the native typing box. Others: style builder and box.
- `import { colors, radius, spacing, typography } from '../theme';` (`:4`) tokens; `typography.body` is the text style for typed text.
- `import { DriverText } from './DriverText';` (`:5`) shared text.

## 3. Walk through the code
`:7-20` props type: required `label`, `value`, `onChangeText`, `placeholder`. Optional `error`, `helperText`, `leading`, `trailing`, `editable`, `inputMode` (`'numeric' | 'text'`), `maxLength`, `autoCapitalize`.

`:23` function with defaults: `editable=true`, `inputMode='text'`, `autoCapitalize='words'`.
- `:24` `const [focused, setFocused] = useState(false);` remembers whether the box has focus (the cursor is in it).
- `:25` `const message = error ?? helperText;` `??` takes the left value unless it is `null`/`undefined`. So an error hides the helper text.
- `:26` JSX:
  - `DriverText weight="600"` shows the label.
  - Field `View` styles combined: base, plus `disabled` if not editable, `focused` if focused, `inputError` if `error` is set.
  - `leading`, then `TextInput`, then `trailing`.
  - `TextInput` props: `accessibilityLabel` for screen readers; `autoCapitalize` is forced `'none'` for numeric; `autoCorrect={false}` stops auto-fix; `editable`; `inputMode`; `keyboardType` is `'number-pad'` for numeric; `maxLength` limits characters; `onFocus`/`onBlur` set `focused`; `onChangeText` sends the new text up; `value` makes it a **controlled input** (the parent owns the text. *Example:* parent keeps `phone` in state and passes it as `value`).
  - Message: red if `error`, grey otherwise, size 13.

`:29` styles: focus uses a 2-point darker border and `paddingHorizontal: spacing.md` (smaller by 4) so the box content does not shift when the border gets 1 point thicker on each side.

Example: `<DriverTextField label="Phone" value={phone} onChangeText={setPhone} placeholder="09..." inputMode="numeric" maxLength={11} error={err}/>`.

## 4. How data flows
```
user types --> TextInput.onChangeText(text) --> parent setState
parent re-renders --> value=text --> TextInput shows it
focus/blur --> setFocused --> border style changes
```

## 5. Try it
Not directly runnable alone. Use it in a login screen, type text and watch the border change on focus.

## 6. Can it be better?
- Good: accessible, handles focus/error/disabled, controlled.
- Weak: no `secureTextEntry` for passwords, no `onSubmitEditing`. Error text is not announced to screen readers. `error && styles.inputError` with an empty string `''` returns `''`, which React Native styles ignore, but a boolean is cleaner. `autoCorrect={false}` for names is a choice (opinion).
- Cleaner way: `error ? styles.inputError : null`.
- Security: no password mode, so do not use it for passwords as is.

## 7. Check yourself
1. Which message shows when both `error` and `helperText` are set?
2. Why is `paddingHorizontal` smaller when focused?
