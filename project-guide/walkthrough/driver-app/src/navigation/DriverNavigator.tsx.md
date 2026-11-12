# driver-app/src/navigation/DriverNavigator.tsx

## 1. Purpose
This file builds the screen map of the Driver app. It decides which screen shows first, how the driver moves from one screen to another, and wraps everything in the driver session state. It sits between the app root and the feature screens (`driver-app/src/features/...`). It calls every Driver screen and `driverAuthService`.

## 2. Imports, one by one

**Third-party**
- `import { NavigationContainer } from '@react-navigation/native';` (`DriverNavigator.tsx:1`). **React Navigation** (a library that moves between screens in a React Native app. *Example:* tap "Login" and the Login screen slides in). `NavigationContainer` is the outer box that stores the navigation state. Every app needs exactly one. It can also handle deep links (links that open a certain screen).
- `import { createNativeStackNavigator, type NativeStackScreenProps } from '@react-navigation/native-stack';` (`:2`). `createNativeStackNavigator` makes a **stack** (screens piled like cards; a new screen goes on top and "back" removes it). It uses the real Android/iOS screen system, so it is fast. `NativeStackScreenProps` is a **type** (a TypeScript-only label, erased when the app runs) that describes the props one screen receives, such as `navigation`. The word `type` before it means "import only for type checking".

**Project imports** (all from `driver-app/src/features/...`, lines 4-17)
- `DriverLoginScreen`, `DriverSignupScreen`, `DriverOnboardingScreen`: the auth screens (`features/auth/screens`).
- `driverAuthService`: the object that saves and clears the login session (`features/auth/services/driverAuthService`).
- `DriverHomeScreen`, `DriverSessionProvider`: the dashboard and the **context provider** (a React box that shares data with all child components. *Example:* "is the driver online?") from `features/dashboard`.
- `DriverEarningsScreen`, `DriverTripHistoryScreen`, `RideRequestScreen`, `DriverActiveRideScreen`, `DriverOutstationScreen`: money and ride screens.
- `DriverSplashScreen`, `DriverHelpScreen`, `DriverSettingsScreen`: start, support and profile screens.
- `import type { DriverStackParamList } from './types';` (`:18`): the list of screen names, from `navigation/types.ts`.

## 3. Walk through the code, top to bottom

**`const Stack = createNativeStackNavigator<DriverStackParamList>();`** (`:20`). Makes the stack object. The `<...>` part is a **generic** (a type given to a function so it can check names. *Example:* `Stack.Screen name="Hom"` becomes a compile error). It returns an object with two parts: `Stack.Navigator` and `Stack.Screen`.

**Route wrapper functions** (`:22-68`). Each screen has a small function named `XxxRoute`. A **route** here means "one entry in the stack". The wrapper receives `{ navigation }` from React Navigation and turns navigation actions into plain callback props (`onBack`, `onContinue`...). This way the screens themselves do not know about React Navigation. Navigation calls used:
- `navigation.replace('Login')` swaps the current screen for Login (no back to the old one).
- `navigation.navigate('Help')` pushes Help on top.
- `navigation.goBack()` pops the top screen.
- `navigation.reset({ index: 0, routes: [{ name: 'Home' }] })` throws away the whole history and starts again with only Home. Used after login/logout so "back" cannot return to the wrong place.

Per wrapper:
- `SplashRoute` (`:22`): when splash finishes, replace with Login.
- `LoginRoute` (`:26`): on success it gets `session`. If `session.driver.onboarding_completed` is true it resets to `Home`, else to `Onboarding`. It also wires back, help and signup. Example: a new driver has `onboarding_completed = false`, so lands on Onboarding.
- `SignupRoute` (`:30`): same success rule as Login.
- `HelpRoute` (`:34`): back button only.
- `OnboardingRoute` (`:38`): when done, reset to Home.
- `HomeRoute` (`:42`): defines `logout` (an `async` function, so it can `await`, meaning wait for a slow step). It waits for `driverAuthService.clearSession()` (deletes the saved tokens), then resets to Login. `void logout()` (`:47`) starts it and ignores the returned promise so no lint warning appears. Home gives seven buttons to other screens.
- `RideRequestRoute` (`:50`): when the driver accepts a ride, replace with ActiveRide.
- `ActiveRideRoute` (`:54`): back, and when the ride is finished reset to Home.
- `EarningsRoute`, `TripHistoryRoute`, `OutstationRoute`, `SettingsRoute` (`:56-68`): back only.

**`export function DriverNavigator()`** (`:70-72`). Returns the tree: `DriverSessionProvider` > `NavigationContainer` > `Stack.Navigator` > twelve `Stack.Screen`. `initialRouteName="Splash"` means Splash opens first. `screenOptions={{ animation: 'slide_from_right', headerShown: false }}` slides screens in from the right and hides the default top bar (each screen draws its own). Each `Stack.Screen` links a `name` to a `component`. All on one long line (`:71`), which is hard to read.

## 4. How data flows
```
Driver taps Login
  -> DriverLoginScreen calls onAuthenticated(session)
  -> LoginRoute checks session.driver.onboarding_completed
  -> navigation.reset(... 'Home' or 'Onboarding')
  -> Stack shows that screen
```

## 5. Try it
Not directly runnable alone. Start the app: `cd driver-app && pnpm start` (starts Metro, the JS bundler), then open it on an Android device. You should see Splash first.

## 6. Can it be better?
- Good: screens do not import React Navigation; the type list catches wrong names; `reset` stops back-button bugs.
- Weak: line 71 and lines 27, 31, 47, 54, 64 are very long one-liners. The login/signup success code is duplicated. There is no check at start-up for an already saved session (it always shows Splash then Login). I am not sure whether Splash checks it; read `DriverSplashScreen`.
- Cleaner (opinion): put the success rule in one helper.
```tsx
const goAfterAuth = (nav, session) => nav.reset({ index: 0, routes: [{ name: session.driver.onboarding_completed ? 'Home' : 'Onboarding' }] });
```
- Security: logout clears the session locally only; it does not tell the server to cancel the refresh token.

## 7. Check yourself
1. What is the difference between `navigate`, `replace` and `reset`?
2. Why does `LoginRoute` choose `Home` or `Onboarding` after login?
