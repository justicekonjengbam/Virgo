# EmergencyContactsScreen.tsx

## 1. Purpose
This screen shows the passenger's emergency contacts as cards, each with a call button. It is a React Native screen (a screen is a function that returns what to draw). It is used by the passenger app's navigation (the parent passes `onBack` and `onMenuPress`). It calls `emergencyContactsApi.ts` and uses the design-system components.

## 2. Imports, one by one
Third-party:
- `import { useEffect, useState } from 'react';` (line 1)
  - **React** (a library for building screens from functions). **useState** (keeps a value that, when changed, redraws the screen. *Example:* `const [n, setN] = useState(0)`). **useEffect** (runs code after the screen appears. *Example:* load data once).
- `import { Linking, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 2)
  - **react-native** (draws real phone UI). `Linking` opens links, including phone calls. `Pressable` is something you can tap. `SafeAreaView` keeps content away from notches. `ScrollView` scrolls. `StyleSheet` builds styles. `View` is a box (like a div).
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (line 3): an icon set. *Example:* `<MaterialCommunityIcons name="phone" size={21} />`.

Project:
- `DsCard, DsEmptyState, DsLoading, DsText` from `components/design-system` (line 5): the app's own card, empty-state box, spinner and text components ("Ds" = design system).
- `AppPageHeader` from `components/navigation/AppPageHeader` (line 6): page title bar with back and menu buttons.
- `colors, radius, spacing` from `theme` (line 7): shared design values (*Example:* `spacing.lg`).
- `emergencyContactsApi, type EmergencyContact` from `../data/emergencyContactsApi` (line 8): the fetch function and the data type. `type` means it is only a type and disappears at build time.

## 3. Walk through the code, top to bottom
### Props type (line 10)
`EmergencyContactsScreenProps` says the screen receives two functions: `onBack` and `onMenuPress`. **Props** (inputs that a parent gives to a component).

### Component `EmergencyContactsScreen` (lines 12-65)
- Line 13: `contacts` starts as an empty list. `setContacts` replaces it and redraws.
- Line 14: `error` starts as `null`.
- Lines 15-20: `useEffect(..., [])`. The empty `[]` means "run once, when the screen first appears". It calls `list()`, then `.then(setContacts)` stores the result, and `.catch(...)` stores an error text if it fails. `void` marks that we do not wait for the Promise on purpose.
- Lines 21-26: if there is an error, show `DsEmptyState` with a "Back" button.
- Lines 27-32: if the list is empty, show a full-screen loading spinner.
- Lines 33-64: otherwise draw the page:
  - `AppPageHeader` (line 36).
  - A notice card with a shield icon (37-42).
  - `contacts.map(...)` (43) turns each contact into a card. `key={contact.id}` helps React track each row.
  - Avatar: `contact.name.charAt(0)` is the first letter (47). *Example:* "Asha" gives "A".
  - `contact.relationship ?? 'Emergency contact'` (53): `??` uses the right side when the left is `null`.
  - Call button (57): `Linking.openURL('tel:...')` opens the phone dialer. `phone_number.replace(/[^0-9+]/g, '')` removes every character that is not a digit or `+`. *Example:* `"+91 98765-43210"` becomes `"+919876543210"`. `accessibilityLabel` is text for screen readers.

### Styles (lines 67-85)
`StyleSheet.create` makes named style objects. `flex: 1` fills space, `gap` is space between children, `radius.pill` makes round shapes (48x48 avatar, 44x44 button).

### Errors
Load failure sets "Unable to load emergency contacts." (line 19).

## 4. How data flows
```
Screen appears -> useEffect -> emergencyContactsApi.list() -> backend
backend -> array -> setContacts -> redraw -> cards
tap phone icon -> Linking.openURL('tel:+91...') -> phone dialer
```

## 5. Try it
Not directly runnable alone. Run the passenger app (`cd passenger-app && npm run android`, or your project's start command) and open "Emergency Contacts" from the drawer. Expected: a spinner, then contact cards.

## 6. Can it be better?
- Good: handles loading, error and success. Strips bad characters from phone numbers.
- Weak (bug): if the user has zero contacts, `!contacts.length` is true forever, so the spinner never ends. Empty and loading are mixed up.
- Weak: the call button line (57) is very long. No retry on error. If `name` is empty, `charAt(0)` is an empty string.
- Cleaner way:
```ts
const [contacts, setContacts] = useState<EmergencyContact[] | null>(null);
if (contacts === null) return <Loading/>;
if (!contacts.length) return <EmptyState/>;
```
- Security: `tel:` links are safe here because digits and `+` only are kept.

## 7. Check yourself
1. Why does a passenger with no contacts see a spinner forever?
2. What does `phone_number.replace(/[^0-9+]/g, '')` return for `"(022) 555-1234"`?
