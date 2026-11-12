# RememberMe.tsx

## 1. Purpose
A tappable checkbox with the words "Remember me". Login and signup flows use it. The parent owns the true/false value; this component only shows it and reports taps. That pattern is called a **controlled component** (the value lives in the parent; *example:* `<input value={x}>` in HTML forms).

## 2. Imports, one by one
- `import { Pressable, StyleSheet, View } from 'react-native';` (`RememberMe.tsx:1`). `Pressable` is a box that reacts to taps. *Example:* `<Pressable onPress={fn}>`. `View` and `StyleSheet` as in other files.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (`:2`). **react-native-vector-icons** gives icon fonts. This one is the Material Design Community set. *Example:* `<MaterialCommunityIcons name="check" size={15} />` draws a tick. Needs the font installed in the native app.
- `import { colors, spacing } from '../../theme';` (`:4`) color and spacing tokens (`theme/tokens.ts`).
- `import { DsText } from '../design-system';` (`:5`) themed text.

## 3. Walk through the code
`type RememberMeProps = { checked: boolean; onChange: (checked: boolean) => void };` (`:7`). `onChange` is a callback that receives the new value.

`export function RememberMe({ checked, onChange })` (`:10`):
- `:12` `<Pressable accessibilityRole="checkbox" accessibilityState={{ checked }} onPress={() => onChange(!checked)} style={styles.row}>`. Role and state tell screen readers this is a checkbox and whether it is on. On tap, call `onChange` with the opposite value (`!checked`; `!true` is `false`).
- `:13` a small square `View`. `[styles.checkbox, checked && styles.checked]`: when `checked` is true, `styles.checked` is added (blue fill). When false, `false` is added, which React Native ignores.
- `:14` `{checked && <MaterialCommunityIcons .../>}` shows a white tick only if checked. `&&` returns the right side only when the left is true.
- `:16` the label "Remember me" in grey.

Styles (`:21-26`): row with a gap; 20x20 box with 1 point border; checked state fills with `colors.primary`.

## 4. How data flows
```
LoginScreen state: remember=false --checked--> RememberMe
user taps -> onChange(true) -> LoginScreen sets state -> re-render with checked=true -> tick shows
```

## 5. Try it
Not directly runnable. `const [r,setR]=useState(false); <RememberMe checked={r} onChange={setR} />`. Tap: the box turns blue with a tick.

## 6. Can it be better?
- Good: accessible role and state, controlled, small.
- Weak: the label text is fixed English, no translation. Touch area is small (20 points box; the whole row is pressable, which helps). Font sizes are magic numbers. Uses a different icon system than `DsIcon`.
- Cleaner (opinion): accept a `label` prop; use `DsIcon name="check"` to keep one icon system.
- Security: none. (Whether "remember me" stores a token safely is decided elsewhere, not here.)

## 7. Check yourself
1. Who stores the checked value, this component or its parent?
2. What does `checked && styles.checked` give when `checked` is false?
