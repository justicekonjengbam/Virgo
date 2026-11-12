# passenger-app/src/features/support/screens/FaqScreen.tsx

## 1. Purpose
This screen shows a list of frequently asked questions. Tapping a question opens or closes its answer. It is reached from the login and signup screens through the "help" button. `PassengerNavigator.tsx:52` wraps it in `FaqRoute`. It uses `AuthHeader`, `DsCard`, `DsText`.

## 2. Imports, one by one
- `import { useState } from 'react';` (line 1). **useState** (a React hook that gives a component a memory value and a setter. *Example:* `const [n, setN] = useState(0); setN(1)` re-draws the screen with n = 1). Used for which question is open (line 35).
- `import { Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 2). `Pressable` is anything the user can tap. `SafeAreaView` avoids the notch. `ScrollView` scrolls. `StyleSheet` defines styles. `View` is a box.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (line 3). Icon pictures by name. *Example:* `name="chevron-down"`.
- `import { AuthHeader } from '../../../components/auth/AuthHeader';` (line 5). Top bar with a back button.
- `import { DsCard, DsText } from '../../../components/design-system';` (line 6). Shared card and text parts.
- `import { colors, spacing } from '../../../theme';` (line 7). Colour and gap values.

## 3. Walk through the code, top to bottom
- Line 9: props type, one function `onBack`.
- Lines 11-32: `questions` is a list of pairs `[question, answer]`. `as const` makes it read-only and keeps exact text types.
- Lines 34-81 `FaqScreen({ onBack })`:
  - Line 35: `useState<number | null>(0)` stores `openIndex`, the index of the open question. `0` means the first one starts open. `null` means all closed.
  - Lines 40-45: title "How can we help?" and a subtitle.
  - Lines 46-56: a blue info card, "Built for Tier 2 & Tier 3 Cities of India" (Tier 2 and 3 cities are smaller Indian cities).
  - Lines 59-67: `questions.map(([question, answer], index) => <FaqItem .../>)`. `.map` makes one `FaqItem` per pair. `isOpen={openIndex === index}`. `onPress` toggles: if this one is open, set `null` (close); otherwise set `index` (open). So only one answer is open at a time. `key={question}` is the unique label React needs in lists.
  - Lines 69-77: a green "Trust matters to us" card.
- Lines 83-113 `FaqItem({question, answer, isOpen, onPress})`: a card with a tappable row (`Pressable`, `accessibilityRole="button"` tells screen readers it is a button). The icon is `chevron-up` when open, else `chevron-down`. Line 106: `{isOpen ? <DsText>{answer}</DsText> : null}` shows the answer only if open.
- Lines 115-140: styles. `flex: 1` on `questionText` lets long text wrap and keeps the icon on the right. `marginTop: -spacing.md` pulls the subtitle closer to the title.

## 4. How data flows
```
tap on question i
  -> FaqItem.onPress
  -> setOpenIndex(openIndex === i ? null : i)
  -> FaqScreen re-draws -> FaqItem isOpen true only for i
```

## 5. Try it
Not directly runnable alone. Run the app, open Login, tap the help button. Tap a question: its answer shows and the previous one closes.

## 6. Can it be better?
- Good: small, clear, accessible role on the tap row, single open item.
- Weak: texts are hard coded in English, no translation. `key={question}` breaks if two questions are equal. No test. `FaqItem` has no `accessibilityState={{expanded: isOpen}}`. The tuple list is less readable than a list of objects.
- Cleaner way: `{ question: '...', answer: '...' }` objects with an `id`. (Opinion.)
- Security: none.

## 7. Check yourself
1. What value does `openIndex` have after you tap the open question again?
2. Why does `FaqItem` get `onPress` from its parent instead of owning the state?
