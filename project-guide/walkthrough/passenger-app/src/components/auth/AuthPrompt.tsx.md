# AuthPrompt.tsx

## 1. Purpose
This file draws one small line of text with a button next to it, for example "Do not have an account? **Sign up**". It sits under login and signup forms and lets the user switch screens. It is a **component** (a function that returns a piece of screen; *example:* `<AuthPrompt .../>` draws that piece). It calls `DsText` and `DsButton` from the design system (`passenger-app/src/components/design-system/index.ts`).

## 2. Imports, one by one
Third-party:
- `import { StyleSheet, View } from 'react-native';` (`AuthPrompt.tsx:1`). **React Native** is the library that turns React code into real phone screens. `View` is an empty box used for layout (like a `div` on the web). `StyleSheet` builds style objects. *Example:* `<View style={{flexDirection:'row'}}>` makes a row box. It can also give `Text`, `Image`, `Pressable`.

Project:
- `import { colors, spacing } from '../../theme';` (`:3`). From `passenger-app/src/theme/index.ts`, which re-exports `tokens.ts`. **Design tokens** (named values for colors and sizes; *example:* `spacing.huge` instead of the number 48). `colors.textTertiary` is the grey text color. `spacing.huge` is a big gap.
- `import { DsButton, DsText } from '../design-system';` (`:4`). From `design-system/index.ts`. `DsText` draws text with theme styles. `DsButton` draws a tappable button.

## 3. Walk through the code
**Props type** (`:6`): `type AuthPromptProps = { actionLabel: string; message: string; onAction?: () => void };`
A **prop** (an input given to a component; *example:* `message="Hello"`). The `?` means optional. `onAction` is a **callback** (a function the parent gives, called later when something happens).

**Function** (`:9`): `export function AuthPrompt({ actionLabel, message, onAction }: AuthPromptProps)`.
The curly braces in the parameter list pick the three props out of one object (*destructuring*). It returns **JSX** (HTML-like code inside JavaScript that describes the screen).
- `:11` `<View style={styles.row}>` is the outer row box.
- `:12` `<DsText color={colors.textTertiary} style={styles.message}>{message}</DsText>` shows the message in grey. The `style` prop adds font size 18 and line height 26 on top of the default text style.
- `:13` `<DsButton label={actionLabel} onPress={onAction ?? (() => undefined)} size="small" variant="ghost" />`. `??` means "use the left side unless it is null or undefined". So if no `onAction` is given, a function that does nothing is used. `size="small"` and `variant="ghost"` give a small, see-through button.

**Styles** (`:18-21`): `StyleSheet.create({...})` checks and stores the styles. `row` is a horizontal (`flexDirection: 'row'`) box, centered both ways, with a top margin of `spacing.huge`.

Errors: none thrown. A wrong prop type is caught by TypeScript at build time, not at run time.

## 4. How data flows
```
LoginScreen --message, actionLabel, onAction--> AuthPrompt
AuthPrompt --label, onPress--> DsButton
user taps button -> DsButton calls onPress -> onAction() in LoginScreen (navigate)
```

## 5. Try it
Not directly runnable. Use it inside a screen: `<AuthPrompt message="No account?" actionLabel="Sign up" onAction={() => navigation.navigate('Signup')} />`. Expect grey text and a small blue-ish text button on one line.

## 6. Can it be better?
- Good: small, reusable, optional callback is safe.
- Weak: a button that silently does nothing when `onAction` is missing is confusing. Font sizes 18 and 26 are magic numbers (numbers with no name). The docblock says "reused" but `onAction` should probably be required.
- Cleaner (opinion): make `onAction` required, or hide the button without it.
- Security: none.

## 7. Check yourself
1. What does `onAction ?? (() => undefined)` do when `onAction` is not given?
2. Why does the file import from `'../design-system'` and not from each atom file?
