# driver-app/src/components/auth/DriverAuthHeader.tsx

## 1. Purpose
The header for driver sign-in and sign-up screens: back button on the left, big brand mark in the middle, optional "Login" button and a help button on the right. Auth screens pass the three callbacks (functions to run on tap).

## 2. Imports, one by one
- `import { Pressable, StyleSheet, View } from 'react-native';` (`DriverAuthHeader.tsx:1`) tappable wrapper, style builder, box.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (`:2`) icon font. Used for `chevron-left` and `help-circle`.
- `import { DriverBrandMark } from '../brand/DriverBrandMark';` (`:3`) the logo mark (another file, not in this batch).
- `import { DriverText } from '../DriverText';` (`:4`) shared text.
- `import { colors, radius, shadows, spacing } from '../../theme';` (`:5`) tokens.

## 3. Walk through the code
`:7` `type DriverAuthHeaderProps = { onBack; onHelp; onLogin? }`. `onLogin` is optional.

`:8` `DriverAuthHeader` returns a row `View` of three parts:
1. Back `Pressable` (label "Go back") calling `onBack`, blue chevron size 30.
2. `DriverBrandMark size={54}`.
3. An `actions` row: if `onLogin` exists, a "Login" button (`DriverText` weight 500, blue); `{cond ? <X/> : null}` is how React shows something only when a condition is true. Then the help button (label "Get help") calling `onHelp`.

`:9` styles: header is 108 high with a blue bottom line; icon buttons are 48x48 with shadow and border; login button has min width 88.

Example: `<DriverAuthHeader onBack={goBack} onHelp={openHelp} onLogin={() => navigate('Login')}/>` on the sign-up screen; omit `onLogin` on the login screen.

## 4. How data flows
```
Auth screen --callbacks--> DriverAuthHeader
 tap "Login" --> onLogin() --> navigation
 tap "?"     --> onHelp()
```

## 5. Try it
Not directly runnable alone. Render it on the top of an auth screen and tap each button.

## 6. Can it be better?
- Good: the optional Login button is neat.
- Weak: back and help buttons lack `accessibilityRole="button"` (only the Login one has it). The 48 size repeats and the layout is one dense line. Fixed height 108 ignores phone notches (safe area).
- Cleaner way: add `accessibilityRole="button"` to both icon buttons and reuse one `IconButton` component (shared with `DriverPageHeader`).
- Security: none.

## 7. Check yourself
1. When is the Login button shown?
2. Which two files look almost the same as this header, and how could you share code?
