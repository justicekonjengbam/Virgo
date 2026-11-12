# passenger-app/src/navigation/PassengerNavigator.tsx

## 1. Purpose
This file is the map of the passenger app. It lists every screen, wires each screen's buttons to navigation actions, holds the half-finished booking (pickup, destination, vehicle) and shows the side menu on logged-in screens. `App.tsx` (the app root) renders `PassengerNavigator`. It calls all the screen files and `authService`, `bookingApi`. Types come from `navigation/types.ts`.

## 2. Imports, one by one
**Third party**
- `import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';` (line 1). **React** hooks. `useState` keeps a value (*Example:* `const [n,setN]=useState(0)`). `useEffect` runs code after drawing (*Example:* load data once). `useMemo` remembers a computed value until its inputs change. `createContext`/`useContext` share a value with all child components without passing props (**context**). `ReactNode` is the type of "anything React can draw".
- `import { NavigationContainer, type NavigationProp } from '@react-navigation/native';` (line 2). **React Navigation** (the library that moves between screens). `NavigationContainer` is the root wrapper. `NavigationProp` is the type of the `navigation` object.
- `import { createNativeStackNavigator, type NativeStackScreenProps } from '@react-navigation/native-stack';` (line 3). Makes a **stack** of screens using native animations. `NativeStackScreenProps` types the `{navigation, route}` props.

**Project imports** (lines 5-26): the screens `LoginScreen`, `SignupScreen`, `BookingStatusScreen`, `FareEstimateScreen`, `LocationSelectionScreen`, `EmergencyContactsScreen`, `PassengerHomeScreen`, `MyRidesScreen`, `SplashScreen`, `PassengerSupportScreen`, `FaqScreen`, `InstantRideScreen`, `OutstationBookingScreen`, `NotificationsScreen`, `SavedAddressesScreen`, `PassengerSettingsScreen`; `HomeDrawer` and type `DrawerDestination` (the side menu); `authService` (session helpers: `hasSession`, `clearSession`); `bookingApi` (`activeRide`, `updateSavedPlace`); types `LocationOption`, `RideStatus`; `DsLoading` (spinner); types `BookingDraft`, `PassengerStackParamList` from `./types`.

## 3. Walk through the code, top to bottom
- Line 28: `Stack = createNativeStackNavigator<PassengerStackParamList>()`. Gives typed `Stack.Navigator` and `Stack.Screen`.
- Line 29: `DraftStore = BookingDraft & { setPickup, setDestination, setCategoryId, setOutstationPickup, setOutstationDestination }`. The draft values plus their setter functions. `&` joins two types.
- Line 30: `BookingDraftContext = createContext<DraftStore | null>(null)`. The shared box, empty at first.
- Line 32 `useBookingDraft()`: reads the context; if `null` (used outside the provider) it throws "Booking draft is unavailable." Returns the draft store.
- Line 33 `resetToHome(navigation)`: `navigation.reset({index:0, routes:[{name:'Home'}]})` clears the stack so Back cannot return to Login.
- Lines 34-41 `navigateToDestination(navigation, destination)`: maps menu keys (`home`, `rides`, `addresses`, `emergency`, `support`, otherwise settings) to route names. `navigation.navigate('Rides')` opens or returns to that screen.
- Lines 43-47 `AuthenticatedShell`: wraps a screen with the side menu. Props: `activeDestination` (which menu row is highlighted), `children` (a **render function** that receives `openMenu` and returns the screen), `navigation`. State `menuVisible` (line 44). `logout` (45): `await authService.clearSession()` deletes the saved login, closes the menu, and resets to Login. It returns the screen plus `<HomeDrawer .../>`. `<>...</>` is a fragment (a wrapper that draws nothing).
- Lines 49-68 are **route components**, one per screen. Each receives `navigation` (and `route` for params) and renders the real screen with callbacks:
  - `SplashRoute` (49): on continue, `authService.hasSession()` returns true or false; then `navigation.replace('Home' or 'Login')`. `replace` swaps the current screen so Back does not return to Splash.
  - `LoginRoute` (50): on success `resetToHome`; help opens `Faq`; signup opens `Signup`. `SignupRoute` (51) mirrors it with `replace('Login')`. `FaqRoute` (52).
  - `HomeRoute` (53): reads the draft, keeps `activeRide` in state, and `useEffect` calls `bookingApi.activeRide()` once to find a ride in progress (errors ignored by `.catch(() => undefined)`). `resume` opens `Booking` with that ride. It passes many callbacks: book instant ride, outstation, continue to fare (stores `categoryId` then opens `Fare`), edit saved place, notifications, pickup, destination, menu.
  - `PickupRoute` / `DestinationRoute` (54-55): a location picker; on select it saves to the draft then `goBack()`.
  - `SavedPlaceRoute` (56): picker that calls `bookingApi.updateSavedPlace(route.params.place.id, location)` then goes back. `route.params.place` is typed by `types.ts`.
  - `FareRoute` (57): `ready` is true when pickup, destination and categoryId all exist. If not ready, an effect resets to Home and a spinner shows. The `!` after values tells TypeScript "not null". On booked: `navigation.replace('Booking', { ride })`.
  - `BookingRoute` (58), `RidesRoute` (59), `AddressesRoute` (60), `EmergencyRoute` (61), `SupportRoute` (62), `InstantRideRoute` (63), `NotificationsRoute` (67), `SettingsRoute` (68): shell plus screen.
  - `OutstationRoute`, `OutstationPickupRoute`, `OutstationDestinationRoute` (64-66): same idea with the separate outstation draft values and `scope="outstation"`.
- Lines 70-75 `PassengerNavigator`: five `useState` values hold the draft. `useMemo` builds the context `value` and rebuilds it only when a draft value changes (setters from `useState` never change). Returns `BookingDraftContext.Provider` > `NavigationContainer` > `Stack.Navigator` (`initialRouteName="Splash"`, slide animation, no header) > 20 `Stack.Screen` entries `component={XRoute} name="X"`.

## 4. How data flows
```
App -> PassengerNavigator
  Provider(draft) -> NavigationContainer -> Stack
Splash --hasSession?--> Login | Home
Home: pick pickup -> PickupRoute -> draft.setPickup -> goBack -> Home shows it
Home: Continue -> draft.setCategoryId -> Fare -> onBooked(ride) -> Booking
Menu tap -> navigateToDestination -> navigation.navigate(name)
Logout -> authService.clearSession -> reset to Login
```

## 5. Try it
Not directly runnable alone. `cd passenger-app && npx react-native run-android`, then walk Splash, Login, Home, pick places, Fare, Booking. Type check: `cd passenger-app && npx tsc --noEmit`.

## 6. Can it be better?
- Good: typed routes, a guard on `FareRoute`, one shell for the menu, draft in context.
- Weak: very long one-line functions (lines 53, 64-66, 74) and inconsistent spacing; hard to read and review. Much repeating of `AuthenticatedShell` code. The draft is never cleared after booking. Login state is not kept in the navigator, so a 401 does not send the user to Login. In `resume` (53) `requested_at: new Date()` is made up. `HomeRoute` ignores errors silently. No tests. Eight `useState`-like setters in one context re-render all consumers.
- Cleaner way: split route components into `routes/*.tsx`, run Prettier, and add a `BookingDraftProvider` file. Before: one 700-character line. After: multi-line JSX.
- Security: logout clears the session (good). Routes themselves are not protected: deep links to authenticated screens depend on screens/API failing on 401. Opinion: add an auth guard.

## 7. Check yourself
1. Why does `FareRoute` reset to Home when the draft is incomplete?
2. What is the difference between `navigation.navigate`, `replace` and `reset`?
