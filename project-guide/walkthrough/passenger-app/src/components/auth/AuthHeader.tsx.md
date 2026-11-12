# passenger-app/src/components/auth/AuthHeader.tsx

## 1. Purpose
A **component** (a reusable piece of screen written as a function. *Example:* `<AuthHeader />` draws a top bar). It is the top bar on login, signup and document screens: a back button on the left, the brand mark in the middle, a help button on the right. Screens in `passenger-app/src/` use it and pass two actions. It uses `BrandMark.tsx` and the theme.

## 2. Imports, one by one
Third-party:
- `import { Pressable, StyleSheet, View } from 'react-native';` (`:1`). **React Native** builds phone apps with React. `View` is a box (like `div` on the web). `Pressable` is anything you can tap. `StyleSheet.create` makes style objects. *Example:* `<Pressable onPress={() => alert('hi')}>`.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (`:2`). An icon set. *Example:* `<MaterialCommunityIcons name="home" size={24} />` draws a house icon.

Project:
- `import { colors, radius, shadows } from '../../theme';` (`:4`). Shared design values (colours, corner sizes, shadows) from `passenger-app/src/theme`. Keeps the look in one place.
- `import { BrandMark } from './BrandMark';` (`:5`). The logo piece, same folder.

## 3. Walk through the code
**Props type** (`:7-10`): `type AuthHeaderProps = { onBack?: () => void; onHelp?: () => void }`. **Props** (inputs passed to a component. *Example:* `<AuthHeader onBack={goBack} />`). The `?` means optional. Each is a function that returns nothing.

**`export function AuthHeader({ onBack, onHelp }: AuthHeaderProps)`** (`:13`). Takes the props and returns screen elements (JSX, HTML-like syntax inside code).
- `<View style={styles.header}>` (`:15`) is the row.
- First `Pressable` (`:16`): `accessibilityLabel="Go back"` is the text a screen reader says. `hitSlop={8}` makes the tap area 8 px bigger on every side. `onPress={onBack}` runs the parent's function when tapped. It has a chevron-left icon in the primary colour, size 32 (`:17`).
- `<BrandMark />` (`:19`) the logo in the middle.
- Second `Pressable` (`:20-22`) is the help button with `help-circle` icon.

If a parent passes no `onBack`, tapping does nothing. No errors are raised.

**`styles`** (`:27-48`). `header`: horizontal row (`flexDirection: 'row'`), items centred vertically (`alignItems`), spaced to the edges (`justifyContent: 'space-between'`), height 108, a 1-pixel primary bottom line. `iconButton`: `...shadows.card` copies the shadow style, then a 48x48 rounded square with border and surface background.

## 4. How data flows
```
Screen --props onBack/onHelp--> AuthHeader --renders--> View [Pressable, BrandMark, Pressable]
user taps left button --> onPress --> parent's onBack() --> navigation goes back
```

## 5. Try it
Not directly runnable alone. Use it in a screen: `<AuthHeader onBack={() => navigation.goBack()} />`. Run the app with Metro (see passenger-app scripts) and open the login screen.

## 6. Can it be better?
- Good: accessibility labels, bigger tap area, theme values, small and focused.
- Weak: the back button shows even when there is nothing to go back to; the height 108 and size numbers are magic numbers; the label text is English only.
- Cleaner way (opinion): hide the back button when `onBack` is missing: `{onBack && <Pressable .../>}` (keep a spacer so the logo stays centred).
- Security: none.

## 7. Check yourself
1. What does `hitSlop={8}` change?
2. What happens when `onBack` is not passed?
