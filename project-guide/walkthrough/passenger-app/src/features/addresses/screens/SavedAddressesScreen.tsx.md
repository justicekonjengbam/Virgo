# SavedAddressesScreen.tsx

## 1. Purpose
This screen lists the passenger's saved places (Home, Work...). Tapping one calls `onEdit`, so the parent can open the address editor. It loads data with the hook `usePassengerHome` (the same data as the Home screen). It sits in `features/addresses/screens/`. Its parent gives it `onBack`, `onMenuPress`, `onEdit`. It calls `usePassengerHome`, `AppPageHeader`, and design-system parts.

## 2. Imports, one by one
React Native and icons:
- `import { Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (`SavedAddressesScreen.tsx:1`). **React Native** draws native controls. `Pressable` is a tappable area. `SafeAreaView` keeps content away from the phone notch and edges. `ScrollView` lets content scroll. `View` is a box. `StyleSheet.create` builds styles.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (`:2`). An icon set. *Example:* `name="home"` draws a house.

Project:
- `import { DsCard, DsEmptyState, DsLoading, DsText } from '../../../components/design-system';` (`:3`) via the barrel file `design-system/index.ts`. A card, an empty/error block, a spinner, and text.
- `import { AppPageHeader } from '../../../components/navigation/AppPageHeader';` (`:4`) the top bar.
- `import { colors, radius, spacing } from '../../../theme';` (`:5`) shared design numbers.
- `import type { SavedPlace } from '../../home/domain/homeTypes';` (`:6`). The type of one saved place: `{ id, label, formatted_address, latitude, longitude }` (`homeTypes.ts:1`). Type-only.
- `import { usePassengerHome } from '../../home/state/usePassengerHome';` (`:7`). A **hook** (a function whose name starts with `use` that gives a component state and data. *Example:* `useState`). It returns `{ data, error, loading, refresh }` (`usePassengerHome.ts:21`).

## 3. Walk through the code
- Props type (`:8`): `onBack`, `onMenuPress` (callbacks) and `onEdit(place)`.
- Component (`:10`), all on one line. Read it as:
  1. `const { data, error, loading, refresh } = usePassengerHome();` calls the hook. It fetches home data from the backend (FastAPI) and returns the state. `refresh` fetches again.
  2. `if (loading) return ...DsLoading fullScreen label="Loading saved addresses…"` shows a full-screen spinner. This is an **early return**: the function stops here.
  3. `if (error || !data) return ...DsEmptyState ... onAction={() => void refresh()}` shows "Unable to load addresses", the error text as the description (`error ?? undefined` turns `null` into `undefined`), and a "Try again" button. `void refresh()` calls the async function and ignores its returned promise (a value for work still running).
  4. Main return: `SafeAreaView > ScrollView` with
     - `AppPageHeader` titled "Saved Addresses",
     - a grey help text,
     - `data.saved_places.map(place => <Pressable key={place.id} onPress={() => onEdit(place)}>...)`. `.map` turns each item of the list into a row. `key` is a unique id React needs to track list rows. Each row is a `DsCard` with an icon box (briefcase if the label is `Work`, otherwise a home), the label (`h3`), the address (grey), and a pencil icon.
     - `{!data.saved_places.length && <DsEmptyState title="No saved addresses" .../>}` shows when the list is empty (`!0` is true).
- Styles (`:11`): `safe` fills the screen with the background color; `content` has gaps and padding; `card` is a row; `icon` is a 48x48 tinted square; `copy` has `flex: 1` so long addresses wrap.
- *Example:* `data.saved_places = [{id:1,label:'Home',...}]` draws one card "Home".

## 4. How data flows
```
Screen mounts --> usePassengerHome --HTTP GET--> backend (home data)
backend --JSON {saved_places: [...]}--> hook state (data)
loading? --> DsLoading | error? --> DsEmptyState | ok --> cards
user taps card --> onEdit(place) --> parent opens editor
```

## 5. Try it
Not directly runnable alone. Run the passenger app with the backend running:
```zsh
cd passenger-app && npx react-native run-android
```
`npx` runs a local tool; `react-native run-android` builds and installs on an emulator. Open the saved addresses page; expect cards, or the empty message.

## 6. Can it be better?
- Good: handles loading, error and empty states; every state is covered; uses design-system parts.
- Weak: the component and styles are written on one huge line (`:10`, `:11`), which is hard to read, review and debug. Only `Work` gets a briefcase; other labels like `Gym` show a home icon. No "add address" button. Cards are tappable but the `Pressable` has no `accessibilityLabel`. It fetches the whole Home payload just for addresses. A missing `key` problem does not exist (key is set). Import lines have no blank line before the type.
- Cleaner way (opinion): format with Prettier and split into a small `SavedPlaceRow` component.
```tsx
// before: one line
// after
function SavedPlaceRow({ place, onEdit }) { return (<Pressable ...>...</Pressable>); }
```
- Security: addresses are personal data; do not log `data`.

## 7. Check yourself
1. In what order does the screen check loading, error and empty list?
2. What does `void refresh()` do, and why is `void` used?
