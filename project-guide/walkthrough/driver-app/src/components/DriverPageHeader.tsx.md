# driver-app/src/components/DriverPageHeader.tsx

## 1. Purpose
The top bar of inner driver screens: a back button on the left, the brand mark plus a title in the middle, and an empty space on the right so the title stays centered. Screens pass `title` and `onBack`. It calls `DriverBrandMark` (`./brand/DriverBrandMark`, not in this batch) and `DriverText`.

## 2. Imports, one by one
- `import { Pressable, StyleSheet, View } from 'react-native';` (`DriverPageHeader.tsx:1`) tappable wrapper, style builder, box.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (`:2`) an icon library. *Example:* `<MaterialCommunityIcons name="chevron-left" size={30}/>` draws a left arrow. Here it is the back arrow. Its types come from a `.d.ts` file (the passenger app has one; the driver app may need its own, I did not check).
- `import { DriverBrandMark } from './brand/DriverBrandMark';` (`:4`) the logo mark.
- `import { DriverText } from './DriverText';` (`:5`) shared text.
- `import { colors, radius, shadows, spacing } from '../theme';` (`:6`) tokens.

## 3. Walk through the code
`:8-10` `DriverPageHeader({ title, onBack })` returns one row `View` with three children:
1. A `Pressable` (label "Go back", role button) calling `onBack` on tap, with a blue chevron icon.
2. A `View` with `DriverBrandMark size={28}` and the title in `DriverText` (size 19, weight 700).
3. An empty `View` of width 48 (`styles.spacer`) equal to the back button width, so the middle group is centered.

`:12` styles: `header` is a row with `justifyContent: 'space-between'`; `action` is a 48x48 rounded button with border and shadow; `title` is a row with a gap; `spacer` width 48.

Example: `<DriverPageHeader title="Trip history" onBack={() => navigation.goBack()}/>`.

## 4. How data flows
```
Screen --title,onBack--> DriverPageHeader
 tap arrow --> onBack() --> navigation goes back
```

## 5. Try it
Not directly runnable alone. Render it at the top of a screen and tap the arrow.

## 6. Can it be better?
- Good: accessible back button; the spacer keeps the title centered.
- Weak: the number 48 appears three times (magic number). The whole JSX is on one line. Long titles are not shortened (no `numberOfLines`).
- Cleaner way: `const BUTTON = 48;` and use it in `action` and `spacer`.
- Security: none.

## 7. Check yourself
1. Why is there an empty `spacer` view?
2. What runs when the user taps the arrow?
