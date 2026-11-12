# passenger-app/src/components/auth/AuthInput.tsx

## 1. Purpose
A reusable form field for the login and signup screens: label on top, then a box with an icon, optional prefix (like `+91`), the text input, an optional trailing word, and an optional red error line below. Screens pass props; this file calls `DsText` from the design system and the theme.

## 2. Imports, one by one
Third-party:
- `import type { ComponentProps } from 'react';` (`:1`). `import type` brings in a TypeScript type only (no runtime code). `ComponentProps<X>` gives the props type of component X. *Example:* `ComponentProps<typeof Button>['title']` is the type of Button's `title`.
- `import { StyleSheet, TextInput, View } from 'react-native';` (`:2`). `TextInput` is the typing box. `View` is a box. `StyleSheet` makes styles.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (`:3`). Icon set. *Example:* `name="lock"`.
Project:
- `import { colors, radius, spacing, typography } from '../../theme';` (`:5`). Shared design values.
- `import { DsText } from '../design-system';` (`:6`). The app's text component with `variant` and `color` props.

## 3. Walk through the code
**`type IconName`** (`:8`). Takes the `name` prop type of the icon component, so only real icon names compile. *Example:* `icon="lock"` is fine, `icon="lcok"` is a compile error.

**`AuthInputProps`** (`:10-23`). Required: `icon`, `label`, `placeholder`. Optional: `trailingLabel`, `prefix`, `maxLength`, `editable`, `inputMode` (one of email, numeric, tel, text), `onChangeText`, `secureTextEntry` (hide characters for passwords), `value`, `error`.

**`export function AuthInput({...})`** (`:26-39`). Destructures props (pulls them out by name) and sets defaults: `editable = true`, `inputMode = 'text'`, `secureTextEntry = false`.

**Render** (`:40-65`):
- `<DsText variant="h3">{label}</DsText>` (`:42`) the label.
- `<View style={[styles.field, error && styles.fieldError]}>` (`:43`). An array merges styles. If `error` is a non-empty string, the red border style is added.
- Icon (`:44`), grey, size 28.
- `{prefix ? <DsText ...>{prefix}</DsText> : null}` (`:45`) shows the prefix only if given.
- `<TextInput ...>` (`:46-60`): `accessibilityLabel` for screen readers; `autoCapitalize="none"` and `autoCorrect={false}` stop the phone from changing what you type; `inputMode` hints the keyboard type; `keyboardType` forces the number pad when inputMode is `numeric` or `tel`; `editable` can lock it; `maxLength` limits characters; `onChangeText` is called with the new text on each key press (this is a **controlled input**: the parent keeps the text in state and passes it back as `value`); `placeholderTextColor` colours the hint; `secureTextEntry` shows dots.
- `{trailingLabel && ...}` (`:61`) shows the extra word at the right. Note: if `trailingLabel` were an empty string `''`, React Native would try to render `''` outside a text component and can crash. The prefix line uses the safer `? :` form.
- `{error ? <DsText color={colors.error} variant="caption">{error}</DsText> : null}` (`:63`) the red message.

**`styles`** (`:68-83`): `group` has gap `spacing.sm` between label, field and error. `field` is a row with a 1-px primary border, rounded, min height 56. `input` copies `typography.body`, text colour, `flex: 1` (take all free width), `paddingVertical: 0`.

## 4. How data flows
```
Screen state (phone) --value--> AuthInput --> TextInput shows it
user types --> onChangeText(newText) --> Screen sets state --> new value passed down
Screen validation error --error prop--> red border + message
```

## 5. Try it
Not directly runnable alone. Example use:
```tsx
<AuthInput icon="phone" label="Phone" placeholder="98765 43210" prefix="+91"
  inputMode="tel" maxLength={10} value={phone} onChangeText={setPhone} error={phoneError} />
```
`setPhone` is a React state setter. Run the app and open the login screen.

## 6. Can it be better?
- Good: typed icon names, accessibility label, controlled input, error styling.
- Weak: `trailingLabel &&` risk (above); `inputMode="email"` still uses default keyboardType (`:51`), so on some phones it may not show the email keyboard; `autoCapitalize="none"` applies to names too; no way to show/hide a password.
- Cleaner way: use a ternary for trailingLabel, and map `email` to `keyboardType="email-address"`.
```tsx
{trailingLabel ? <DsText ...>{trailingLabel}</DsText> : null}
```
- Security: `secureTextEntry` hides passwords. `autoCorrect={false}` avoids the keyboard learning them. No secrets stored here.

## 7. Check yourself
1. What does `[styles.field, error && styles.fieldError]` do when `error` is empty?
2. Why does the parent pass both `value` and `onChangeText`?
