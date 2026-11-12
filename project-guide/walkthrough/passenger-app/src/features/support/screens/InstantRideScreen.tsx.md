# passenger-app/src/features/support/screens/InstantRideScreen.tsx

## 1. Purpose
This screen lets a passenger book a ride by phone with CabSure support. It lists what to prepare and has a "Call CabSure Support" button. Home opens it through `onBookInstantRide` (`navigation/PassengerNavigator.tsx:53`) and `InstantRideRoute` (line 63).

## 2. Imports, one by one
- `import { Alert, Linking, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 1).
  - **Alert** (a native pop-up message box. *Example:* `Alert.alert('Title', 'Text')`).
  - **Linking** (talks to the phone's other apps. *Example:* `Linking.openURL('https://x.com')` opens the browser; `tel:123` opens the dialer).
  - `SafeAreaView`, `ScrollView`, `StyleSheet`, `View`: notch-safe area, scrolling area, style helper, plain box.
- `MaterialCommunityIcons` (line 2): icon pictures by name.
- `DsButton, DsCard, DsText` (line 4): shared button, card, text.
- `AppPageHeader` (line 5): top bar with back and menu.
- `colors, radius, spacing` (line 6): style values from `theme/tokens.ts`.

## 3. Walk through the code, top to bottom
- Line 10: `supportNumber = '18007645037'`. A toll-free support number (public, not a secret).
- Lines 11-15: `bookingDetails`, three `[title, description]` pairs.
- `InstantRideScreen({ onBack, onMenuPress })` (line 18).
  - `callSupport` (lines 19-27) is an **async function** (a function that can wait for slow things with `await`).
    1. Builds `tel:18007645037`. A `tel:` URL tells the phone to start a call.
    2. `await Linking.canOpenURL(phoneUrl)` asks the phone if something can handle this URL. Returns true or false. A tablet without a phone app returns false.
    3. If false, `Alert.alert('Calling unavailable', ...)` shows a message with the number written out, then `return` stops.
    4. Otherwise `await Linking.openURL(phoneUrl)` opens the dialer with the number filled in.
  - JSX (lines 29-75): header, a hero card with headset icon, a "Keep these details ready" block, then `bookingDetails.map(([title, description], index) => ...)` which draws numbered cards (`index + 1` in a round badge), an info note, the call button, and a small phone line.
  - Line 71: `onPress={() => void callSupport()}`. The arrow function calls `callSupport` and `void` ignores its promise. `leading` puts a phone icon before the label. `accessibilityLabel` is the text a screen reader speaks.
- Styles (lines 78-92): `radius.pill` (999) makes the step badge a circle; `flex: 1` lets texts wrap.

## 4. How data flows
```
User taps "Call CabSure Support"
 -> callSupport()
 -> Linking.canOpenURL('tel:...') -> true -> Linking.openURL -> phone dialer
                                   -> false -> Alert 'Calling unavailable'
```

## 5. Try it
Not directly runnable alone. Run the app on a phone, open the menu, Support, Book instant ride, tap the button. The dialer opens with 18007645037. On an emulator without calling you should see the alert.

## 6. Can it be better?
- Good: handles "no phone" case, accessible label, clear steps.
- Weak: the number is written twice (line 10 and in text on lines 23 and 72); change one and the others go stale. On Android 11 and newer, `canOpenURL` may need a `<queries>` entry in the manifest; I am not sure it is set (check `android/app/src/main/AndroidManifest.xml`). `openURL` can throw and is not caught. No test.
- Cleaner way: one constant `SUPPORT_NUMBER_DISPLAY` and a `try/catch` around `openURL`.
- Security: the number is public. No secrets.

## 7. Check yourself
1. What happens if `canOpenURL` returns false?
2. Why does the code write `void callSupport()` in `onPress`?
