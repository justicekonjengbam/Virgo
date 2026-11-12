# passenger-app/src/features/splash/screens/SplashScreen.tsx

## 1. Purpose
This is the first screen a passenger sees: logo, name "Cab Sure", and one "Continue" button. It sits in the splash feature. `PassengerNavigator.tsx:49` renders it inside `SplashRoute` and decides what happens after the button press. It calls `BrandMark`, `DsButton`, `DsText`.

## 2. Imports, one by one
- `import { SafeAreaView, StyleSheet, View } from 'react-native';` (line 1). **React Native** (library that draws native phone screens from React code). `SafeAreaView` keeps content away from the notch. `StyleSheet` defines styles. `View` is a box (like `<div>`).
- `import { BrandMark } from '../../../components/auth/BrandMark';` (line 3). Project component that draws the logo. `size={112}` makes it 112 units wide.
- `import { DsButton, DsText } from '../../../components/design-system';` (line 4). Shared button and text parts ("Ds" = design system).
- `import { colors, spacing } from '../../../theme';` (line 5). Colours and gap sizes from `theme/tokens.ts`.

## 3. Walk through the code, top to bottom
- Line 7: `type SplashScreenProps = { onContinue: () => void };`. A **prop** is an input to a component. This one is a function the screen calls when the user taps Continue.
- Line 10: `export function SplashScreen({ onContinue })`. A **component** (a function that returns what to draw). Input: `onContinue`. Output: the JSX (HTML-like code) tree.
- Lines 12-22: safe area, then a `content` box, then a `hero` box with logo, big blue title "Cab Sure" (`variant="display"` is the largest text style), grey subtitle "Made in IIT-DH", then the button `<DsButton label="Continue" onPress={onContinue} size="large" />`. `onPress` is called on tap.
- Lines 25-30 styles: `content` uses `justifyContent: 'space-between'` so the hero is on top and the button is at the bottom. `marginTop: '45%'` pushes the hero down by 45 percent of the parent height. `subtitle` centers text.

The screen has no state and no network call. The comment on line 9 says this is on purpose.

## 4. How data flows
```
User taps Continue
  -> DsButton.onPress -> onContinue (given by SplashRoute)
  -> authService.hasSession() -> navigation.replace('Home' or 'Login')
```

## 5. Try it
Not directly runnable alone. Start the app: `cd passenger-app && npx react-native run-android`. You see this screen first because `initialRouteName="Splash"` (`PassengerNavigator.tsx:74`).

## 6. Can it be better?
- Good: tiny, only one job, easy to test.
- Weak: the user must tap even if already logged in; the session check could run on its own and skip the screen. The text "Cab Sure" is hard coded (the rest of the app writes "CabSure"). `'45%'` is a magic number.
- Cleaner way (opinion): check the session in the background and auto-continue after a short delay.
- Security: none.

## 7. Check yourself
1. Who decides where the user goes after Continue, this file or the navigator?
2. What does `justifyContent: 'space-between'` do here?
