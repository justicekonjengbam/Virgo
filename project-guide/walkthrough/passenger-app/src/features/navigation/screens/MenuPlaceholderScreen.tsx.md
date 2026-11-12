# MenuPlaceholderScreen.tsx

## 1. Purpose
A "Coming next" screen used for menu pages that are not built yet. It shows a header, an icon, and a description. It lives in `features/navigation/screens/`. The navigator renders it with a title, text and icon. It calls `AppPageHeader` (`src/components/navigation/AppPageHeader`).

## 2. Imports, one by one
- `import { SafeAreaView, StyleSheet, View } from 'react-native';` Safe-area box (avoids the notch), style builder, plain box.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` Icon font. *Example:* `<MaterialCommunityIcons name="cog" size={20}/>`.
- `import { DsCard, DsText } from '../../../components/design-system';` The app's card and text pieces.
- `import { AppPageHeader } from '../../../components/navigation/AppPageHeader';` Page header with a back button and a menu button.
- `import { colors, spacing } from '../../../theme';` Shared colours and spacing numbers.

## 3. Walk through the code, top to bottom
**`MenuPlaceholderScreenProps`** (lines 8-14): `title`, `description`, `icon` (an icon name string), `onBack`, `onMenuPress` callbacks.

**`MenuPlaceholderScreen`** (lines 16-35): a component. It returns a safe-area view, a content box (line 25) with the header (line 26) and an elevated card (line 27) holding the icon at size 40, the fixed text "Coming next", and the description. *Example:* `<MenuPlaceholderScreen title="Wallet" description="Pay in app soon" icon="wallet" onBack={...} onMenuPress={...}/>`.

**`styles`** (lines 36-40): `safe` fills the screen with the background colour (`flex: 1` = take all space). `content` pads and spaces children (`gap`). `card` centres items.

No errors can happen here.

## 4. How data flows
```
Navigator --props(title, description, icon)--> MenuPlaceholderScreen
   user taps back -> onBack() -> navigator pops
   user taps menu -> onMenuPress() -> navigator opens drawer
```

## 5. Try it
Not directly runnable alone. Render it from the navigator with test props and run the app (`npx react-native start`). Expected: a page with the title and a "Coming next" card.

## 6. Can it be better?
- Good: tiny and reusable.
- Weak: `icon` is a plain string, so a wrong name fails only at run time. "Coming next" is fixed and not translated. It is a placeholder, so delete it when all menu pages exist.
- Cleaner way: type `icon` as `React.ComponentProps<typeof MaterialCommunityIcons>['name']`.
- Security: none.

## 7. Check yourself
1. Which props are callbacks and who calls them?
2. Why is the icon prop typed as `string` a weak choice?
