# passenger-app/src/features/rides/screens/MyRidesScreen.tsx

## 1. Purpose
This file draws the "My Rides" page. It shows the list of completed rides of the passenger. It sits in the passenger app, in the rides feature folder. `PassengerNavigator.tsx` (`navigation/PassengerNavigator.tsx:59`) creates it. It calls the hook `usePassengerHome` (`features/home/state/usePassengerHome`) to get data, and uses shared UI parts from `components/design-system`.

## 2. Imports, one by one

**React Native (third party)**
- `import { SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 1)
  - **React Native** (a library that draws real phone screens from React code. *Example:* `<View>` becomes an Android or iOS box.)
  - `SafeAreaView` (a box that keeps content away from the notch and the status bar). `ScrollView` (a box that scrolls when content is long). `StyleSheet` (a helper to define styles). `View` (a plain box, like `<div>` on the web).
  - It can also draw text, images, and lists. *Example:* `<Text>Hello</Text>`.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (line 2)
  - **Vector icons** (a set of small icon pictures drawn from a font. *Example:* `<MaterialCommunityIcons name="car" />` draws a car).
  - Used to draw the vehicle icon on each card (line 19).

**Project imports**
- `import { DsCard, DsEmptyState, DsLoading, DsText } from '../../../components/design-system';` (line 3). "Ds" means design system, the app's own shared parts. `DsCard` is a card box. `DsEmptyState` shows a title and message when there is nothing or an error. `DsLoading` shows a spinner. `DsText` is styled text.
- `import { AppPageHeader } from '../../../components/navigation/AppPageHeader';` (line 4). The top bar with back and menu buttons.
- `import { colors, radius, spacing } from '../../../theme';` (line 5). Colour, corner and gap values from `theme/tokens.ts`.
- `import type { RecentRide } from '../../home/domain/homeTypes';` (line 6). `import type` brings only a type (a description of data shape). It disappears when the app is built.
- `import { usePassengerHome } from '../../home/state/usePassengerHome';` (line 7). **Hook** (a function whose name starts with `use` that gives a component data and memory. *Example:* `useState(0)`). This one loads the home data.

## 3. Walk through the code, top to bottom

**Props type, line 9**
`type MyRidesScreenProps = { onBack: () => void; onMenuPress: () => void };` A **prop** (an input passed to a component, like a function argument) list. `onBack` runs when the user taps back. `onMenuPress` opens the side menu. Both return nothing.

**`rideDetails`, line 10**
A fixed list of three fake records: driver name, vehicle text, icon name. The comment on line 11 says these are demo data. The API does not send driver or vehicle here, so the screen fills them in by position.

**`MyRidesScreen`, lines 12-17**
- Line 13: `usePassengerHome()` returns `{ data, error, loading, refresh }`. `data` is the home payload, `error` is a text or null, `loading` is true while fetching, `refresh` loads again.
- Line 14: if `loading`, return a full-screen spinner with the label "Loading your rides…".
- Line 15: if `error` or no `data`, show an empty state with a "Try again" button. `onAction={() => void refresh()}` calls `refresh` and ignores the promise (`void` says "I do not wait for it").
- Line 16: the normal view. A scroll area with the header, a grey subtitle, and then:
  - if `data.recent_rides.length` is more than 0, `.map` turns each ride into a `RideHistoryCard`. `detail={rideDetails[index % rideDetails.length]}` picks demo detail 0,1,2,0,1,2... (`%` is the remainder). `key={ride.id}` is a **key** (a unique label React uses to track list items).
  - otherwise a "No rides yet" empty state.

*Example:* 4 rides give details with indexes 0,1,2,0.

**`RideHistoryCard`, line 18**
Inputs: `ride` (one RecentRide) and `detail` (one demo record). `typeof rideDetails[number]` means "the type of one item of that list".
- `new Date(ride.completed_at).toLocaleDateString('en-IN', {day:'numeric', month:'short', year:'numeric'})` turns an ISO time like `2026-10-01T10:00:00Z` into `1 Oct 2026`. If there is no `completed_at`, the text is "Recently".
- It draws: an icon box, the title `pickup → destination`, the date, the fare `₹ {ride.fare_paise / 100}`, a divider line, then driver and vehicle.
- **paise** (the small money unit; 100 paise = 1 rupee). `fare_paise: 15050` shows `₹ 150.5`.

**`styles`, line 19**
`StyleSheet.create({...})` builds named style objects. `flex: 1` fills free space. `gap` is space between children. `flexDirection: 'row'` puts children side by side.

## 4. How data flows
```
Navigator --(onBack,onMenuPress)--> MyRidesScreen
MyRidesScreen --usePassengerHome()--> backend API (home data)
   data.recent_rides --map--> RideHistoryCard x N --> screen
rideDetails[index % 3] --> fake driver and vehicle on each card
```

## 5. Try it
Not directly runnable alone. Run the app (`cd passenger-app && npx react-native run-android`), log in, open the menu, tap "My Rides". For a type check: `cd passenger-app && npx tsc --noEmit`. Expect no output when all is fine.

## 6. Can it be better?
- Good: handles loading, error and empty cases clearly.
- Weak: driver and vehicle are fake, so a real ride shows wrong names (line 10). Very long one-line JSX on lines 14-18 is hard to read. `fare_paise / 100` can show `150.5` instead of `150.50`. `detail.icon` is a plain string, so the icon name is not type checked. It reuses the Home hook, so it loads more data than needed.
- Cleaner way: ask the backend for driver and vehicle, and format money with `(paise/100).toFixed(2)`. Split JSX over many lines. (Opinion.)
- Security: none here. No secrets.

## 7. Check yourself
1. Why does `rideDetails[index % rideDetails.length]` never go out of range?
2. What does `fare_paise: 25000` show on the card, and why divide by 100?
