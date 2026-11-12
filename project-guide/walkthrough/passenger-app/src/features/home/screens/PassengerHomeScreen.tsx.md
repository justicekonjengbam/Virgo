# PassengerHomeScreen.tsx

## 1. Purpose
This file draws the passenger Home screen. It shows a greeting, the pickup and destination card, saved places (Home and Work), ride categories, two support-booking cards, and recent rides. It sits in `passenger-app/src/features/home/screens/`. The app navigator (not in this batch) renders it and passes callbacks. It calls the hook `usePassengerHome` (`../state/usePassengerHome`) for data, `authService.clearSession` for logout, and the small components `HomeDrawer`, `LocationCard`, `RideOptionCard`, `ImagePlaceholder`.

## 2. Imports, one by one
**Third-party**
- `import { useState } from 'react';` **React** is the UI library. **useState** (a hook, which is a function that gives a component memory. *Example:* `const [n, setN] = useState(0)` gives a number `n` and a function `setN` to change it). Used at lines 59, 60, 227 to remember if the menu is open, which ride category is picked, and if a recent ride is pressed.
- `import { Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` **React Native** gives native building blocks. `View` is a box (like a `div`). `ScrollView` is a box that scrolls. `Pressable` is a box that reacts to touch. `SafeAreaView` keeps content away from the phone notch. `StyleSheet.create` builds a style table. Example: `<Pressable onPress={() => alert('hi')}><Text>Tap</Text></Pressable>`.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` An icon font. Example: `<MaterialCommunityIcons name="home" size={24} />` draws a home icon. Used for bell, menu, chevrons and more.

**Project**
- `DsButton, DsCard, DsEmptyState, DsLoading, DsText` from `../../../components/design-system` (lines 5-11): the app's own design-system pieces (button, card, empty/error box, spinner, text).
- `colors, radius, shadows, spacing` from `../../../theme` (line 12): shared design values. Example: `spacing.xl` is a number for padding.
- `type LocationOption` from `../../booking/data/bookingApi` (line 13): the shape of a place (address, latitude, longitude). `import type` means it is used only for type checking and vanishes at run time.
- `authService` from `../../auth/services/authService` (line 14): login/session helper. Here only `clearSession()` is used.
- `HomeDrawer`, `type DrawerDestination` from `../components/HomeDrawer` (lines 15-16): the side menu and the allowed menu targets (such as `'addresses'`, `'rides'`).
- `ImagePlaceholder` (17), `LocationCard` (18), `RideOptionCard` (19): local components.
- `type RecentRide, SavedPlace` from `../domain/homeTypes` (20): data shapes from the backend home response.
- `usePassengerHome` from `../state/usePassengerHome` (21): the data hook (see its own walkthrough).
- Four `.png` imports (22-25): Metro, the React Native bundler, turns an image file import into an image source. Example: `<Image source={carImage} />`.

## 3. Walk through the code, top to bottom
**`PassengerHomeScreenProps`** (lines 27-41). A TypeScript **type** (a description of an object's shape; the compiler checks it). `pickup` and `destination` may be a place or `null`. The `on...` fields are **callbacks** (functions the parent gives the screen to call on an event). `activeRideId?` and `onResumeRide?` are optional (the `?`).

**`PassengerHomeScreen`** (lines 44-190). A function **component** (a function that returns UI). It receives props by destructuring (line 45-58).
- Line 59: `menuVisible` state, starts `false`.
- Line 60: `selectedCategoryId` state, `number | null`.
- Line 61: `usePassengerHome()` returns `data`, `error`, `loading`, `refresh`.
- Lines 62-66 `logout`: waits for `authService.clearSession()` (deletes stored tokens), closes the drawer, then calls `onLogout()` so the parent shows the login screen.
- Lines 67-72: **early return** while loading. Shows a full screen spinner (`DsLoading`).
- Lines 73-83: on error or no data shows `DsEmptyState` with a "Try again" button. `void refresh()` calls refresh and ignores the returned promise on purpose.
- Line 84: `canContinue` is true only if pickup, destination and a category are all set. `!!x` turns a value into true/false.
- Lines 89-105 header: avatar, a hard-coded greeting "Good Morning, Dishant" (lines 94-98), and two `HeaderAction` buttons (bell opens notifications, menu opens drawer).
- Lines 106-111: `LocationCard` shows pickup/destination and calls the select callbacks.
- Line 112: if `activeRideId` is set, shows a "Continue active ride" card; pressing calls `onResumeRide`.
- Lines 113-125: saved places. `['Home','Work'].map(...)` makes two `SavedPlaceCard`s. For each label it looks for the matching item in `data.saved_places` with `.find`. `.find` returns the first match or `undefined`. Press calls `onEditSavedPlace(place)` only if the place exists.
- Lines 126-139: ride categories. For each one, `RideOptionCard` gets an ETA text, a fare, and an image. `base_fare_paise / 100` converts **paise** (1/100 of a rupee; 5000 paise = 50 rupees) to rupees, then `.toString()`. `vehicleImages[category.code]` picks the image by code `car`, `bike` or `auto`. Pressing sets the selected id.
- Lines 140-145: when `canContinue`, shows "View fare estimate". `selectedCategoryId` is typed `number | null`, but `canContinue` guarantees a number; TypeScript may not see that (see section 6).
- Lines 146-171: two cards, "Book instant ride" (calls support) and "Outstation ride booking". Each has accessibility labels (text that screen readers read).
- Lines 172-177: recent rides, one `RecentRide` per item, keyed by `ride.id`. `key` helps React track list items.
- Lines 179-188: `HomeDrawer`. On navigate it closes the menu first, then calls `onMenuNavigate`.

**`HeaderAction`** (193-199): a square icon button. `accessibilityLabel={icon}` reads the raw icon name to screen readers (e.g. "bell-outline"), which is not friendly.

**`vehicleImages`** (200): lookup table `{ car, bike, auto }`.

**`SavedPlaceCard`** (201-217): chooses icon `briefcase` for Work, else `home`. Shows `place?.label ?? 'Add place'`. The `?.` stops errors if `place` is undefined; `??` gives a default only for null/undefined. Address is limited to 2 lines.

**`SectionTitle`** (218-225): a title with an optional action link on the right.

**`RecentRide`** (226-265): a separate component with its own `active` state for press/hover highlight (lines 227, 241-246). Date uses `toLocaleDateString('en-IN', ...)` (example output `5 Mar 2026`), or "Recently". Duration is seconds / 60 rounded, or an em dash. Fare shows `ride.fare_paise / 100` with a rupee sign. Note: this local function has the same name as the imported type `RecentRide` (line 20). TypeScript allows it because a type and a value live in different spaces, but it is confusing.

**`styles`** (267-346): `StyleSheet.create` makes the styles. `flex: 1` means "take all free space". `gap` is space between children. `...shadows.card` spreads another object's keys in. `marginBottom: -spacing.sm` is a negative margin to pull the next block closer.

## 4. How data flows
```
Parent navigator --props--> PassengerHomeScreen
PassengerHomeScreen --usePassengerHome()--> homeApi.getHome() --HTTP--> backend
        <-- data {saved_places, ride_categories, recent_rides} --
user taps a ride card -> setSelectedCategoryId -> canContinue true
user taps "View fare estimate" -> onContinueToFare(id) -> parent navigates
user taps Log out in drawer -> authService.clearSession() -> onLogout()
```

## 5. Try it
Not directly runnable alone. Start the app and open Home:
```
cd passenger-app && npx react-native start
```
`npx` runs a locally installed tool; `react-native start` starts the Metro bundler. Then run the app on a device. Expected: Metro prints a ready message and Home appears after the spinner.

## 6. Can it be better?
- Good: early returns for loading and error; list items have keys; accessibility roles are present.
- Weak:
  - The name "Dishant" and "Good Morning" are hard-coded (lines 94-98). Use the profile name and the real time of day.
  - `onContinueToFare(selectedCategoryId)` (line 143) may fail strict type checks because the type is `number | null`. Before: `onPress={() => onContinueToFare(selectedCategoryId)}`. After: `onPress={() => selectedCategoryId && onContinueToFare(selectedCategoryId)}`.
  - Lines 112, 146, 160 and 222 are very long single lines. Split them into small components.
  - Name clash between type `RecentRide` and component `RecentRide`. Rename the component `RecentRideRow`.
  - `onHoverIn` does nothing on phones; only press matters.
  - `accessibilityLabel={icon}` is not human text.
  - Fare `(paise/100).toString()` can show `49.5` instead of `49.50`.
  - `vehicleImages[category.code]` gives `undefined` for unknown codes.
- Security: logout clears the session locally only (line 63). That is fine for the client; server-side token revoke is not done here. I am not sure whether `clearSession` calls the server; check `authService`.

## 7. Check yourself
1. Why does `RecentRide` keep its own `useState` instead of the parent holding it?
2. What does `base_fare_paise / 100` do, and why is money stored in paise?
