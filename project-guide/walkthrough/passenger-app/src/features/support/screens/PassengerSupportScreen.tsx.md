# passenger-app/src/features/support/screens/PassengerSupportScreen.tsx

## 1. Purpose
This is the "Support" page. It shows a header card and five fixed question-and-answer cards. It is a simple read-only page. `PassengerNavigator.tsx:62` (`SupportRoute`) shows it. The drawer menu opens it.

## 2. Imports, one by one
- `import { SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 1). **React Native** draws native screens. `SafeAreaView` avoids the notch, `ScrollView` scrolls, `StyleSheet` defines styles, `View` is a box.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (line 2). Icon by name, here `headphones`.
- `import { DsCard, DsText } from '../../../components/design-system';` (line 3). Shared card and text.
- `import { AppPageHeader } from '../../../components/navigation/AppPageHeader';` (line 4). Top bar with back and menu.
- `import { colors, radius, spacing } from '../../../theme';` (line 5). Style values.

## 3. Walk through the code, top to bottom
- Line 6: props type with `onBack` and `onMenuPress` (functions, no result).
- Lines 7-19: `topics`, a list of `[question, answer]` pairs.
- Lines 20-45 `PassengerSupportScreen`: a scroll view with the header (`title="Support"`), a hero card (round icon box and "We are here to help"), then `topics.map(([question, answer]) => <DsCard key={question}>...)`. `.map` makes one card per pair. `key` is the unique label React uses for list items.
- Lines 46-61: styles. `heroIcon` is a 52 by 52 box with a soft blue background, a blue border and rounded corners from `radius.sm`.

There is no state, no network call and no error case.

## 4. How data flows
```
Navigator -> PassengerSupportScreen(onBack,onMenuPress)
  topics (constant list) --map--> DsCard per topic --> screen
```

## 5. Try it
Not directly runnable alone. Run the app, open the menu, tap Support. You see five cards.

## 6. Can it be better?
- Good: very simple and readable.
- Weak: text is almost a copy of `FaqScreen.tsx`'s list, so there are two places to edit. There is no phone or chat link to real support (`InstantRideScreen.tsx` has the number). Inconsistent code style (some entries on one line, some split). No translation.
- Cleaner way: one shared `faq` data file used by both screens. (Opinion.)
- Security: none.

## 7. Check yourself
1. Where does the page get its text from?
2. Why does each card need a `key`?
