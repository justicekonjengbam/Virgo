# AppPageHeader.tsx

## 1. Purpose
The top bar for pages after login: a back button on the left, the page title in the middle, and a menu button on the right. It sits in `components/navigation/`. `SavedAddressesScreen.tsx:10` uses it. It calls `DsText` and the theme.

## 2. Imports, one by one
- `import { Pressable, StyleSheet, View } from 'react-native';` (`AppPageHeader.tsx:1`). **React Native** draws native controls. `Pressable` is anything the user can tap. `View` is a box. `StyleSheet.create` builds styles.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (`:2`). **react-native-vector-icons** is a package of icon fonts. This one is the Material Design Community set. *Example:* `<MaterialCommunityIcons name="menu" size={27} />` draws three lines. Used for the back arrow and menu icons.
- `import { DsText } from '../design-system';` (`:4`) from the barrel file `design-system/index.ts`. Draws the title.
- `import { colors, radius, shadows, spacing } from '../../theme';` (`:5`) from `passenger-app/src/theme`: colors, corner radius, shadow styles, gaps.

## 3. Walk through the code
- `type AppPageHeaderProps = { title: string; onBack: () => void; onMenuPress: () => void }` (`:7`). Two **callbacks** (functions the parent passes in, called on tap).
- `export function AppPageHeader({ title, onBack, onMenuPress })` (`:10`).
- Line 11 returns a row `View` with three children:
  1. `Pressable accessibilityLabel="Go back" onPress={onBack}` with a `chevron-left` icon size 30. `accessibilityLabel` is the text a screen reader says.
  2. `DsText numberOfLines={1} variant="h2"` shows the title cut to one line (with `...` if long). `styles.title` has `flex: 1` so it takes the middle space.
  3. `Pressable accessibilityLabel="Open menu" onPress={onMenuPress}` with a `menu` icon.
- Styles (`:14`): `header` is a row with `space-between` and min height 52. `iconButton` copies `...shadows.card`, then makes a 48x48 square with border, radius and background.
- *Example:* `<AppPageHeader title="Rides" onBack={goBack} onMenuPress={openMenu} />`.

## 4. How data flows
```
Screen --title, onBack, onMenuPress--> AppPageHeader
user taps left button --> onBack() --> navigation goes back
user taps right button --> onMenuPress() --> menu opens
```

## 5. Try it
Not directly runnable. Put it at the top of a screen; tap the arrow and the callback runs.

## 6. Can it be better?
- Good: accessibility labels on both buttons; consistent look.
- Weak: no `accessibilityRole="button"` on the `Pressable`s; the touch size 48 is fine. Title is not marked as a header. Icon sizes (30, 27) are magic numbers. The JSX is on one line.
- Cleaner way (opinion): `<Pressable accessibilityRole="button" accessibilityLabel="Go back" ...>`.
- Security: none.

## 7. Check yourself
1. What does `numberOfLines={1}` do?
2. Which two callbacks does the screen have to provide?
