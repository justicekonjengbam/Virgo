# SignupScreen.tsx

File: `passenger-app/src/features/auth/screens/SignupScreen.tsx` (83 lines)

## 1. Purpose
The account creation screen. The passenger enters a name and phone number, accepts the terms, gets an OTP (One-Time Password, an SMS code) and verifies it. It is a **React component** (a function that returns what to draw). It is very close to `LoginScreen.tsx`, with a name field and a terms checkbox added. It calls `authService.ts`, `authErrorMessage.ts`, `authValidation.ts`.

## 2. Imports, one by one
- `import { useState } from 'react';` the **hook** (special function giving memory to a component. *Example:* `const [a, setA] = useState('')`).
- `from 'react-native'`: `Alert` (popup), `KeyboardAvoidingView` (lifts content over the keyboard), `Platform` (iOS or Android), `Pressable` (any tappable area), `SafeAreaView`, `ScrollView`, `StyleSheet`, `View`, `useWindowDimensions` (screen width).
- `MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons'`: an icon set. *Example:* `<MaterialCommunityIcons name="phone" size={24}/>`. Used for the checkbox icon.
- `FirebaseAuthTypes` from `@react-native-firebase/auth`: type of the pending OTP check.
- Project: `AuthHeader`, `AuthInput`, `AuthPrompt` (`components/auth`), `DsButton`, `DsText` (`components/design-system`), `colors`, `spacing` (`theme`), `authService`, `authErrorMessage`, `validateFullName`, `validateIndianMobile`, `validateOtp`.

## 3. Walk through the code, top to bottom

### Props type (15)
`onAuthenticated`, `onBack`, `onHelp`, `onLogin`: callbacks from the parent.

### State (19-31)
`fullName`, `phone`, `otp`, `termsAccepted`, `confirmation` (Firebase object, `null` at first), `submitting`, `errorMessage`, and three field errors. Line 31: `otpRequested = confirmation !== null` is computed, not stored. This is simpler than `LoginScreen`, which keeps a separate flag.

### `submit` (33-50)
1. Validate name, phone, and OTP (OTP only when requested) (34-36).
2. Check `termsAccepted` (37). Terms are required even at the OTP step.
3. If no `confirmation`: `authService.requestOtp(phone, 'signup')` sends the SMS; store the result; show an `Alert`.
4. Else: `authService.verifyOtp(confirmation, otp, 'signup', fullName)` verifies and creates the backend account (the name goes to the backend). Then `authService.saveProfileName(fullName)` saves the name on the phone. Then `onAuthenticated()`.
5. `catch` maps errors with `authErrorMessage`; `finally` stops the spinner.

### JSX (52-77)
- Name input (61): `onChangeText` stores the text and clears errors.
- Phone input (62): removes non-digits with `replace(/\D/g, '')`, clears `otp` and `confirmation` so a new number needs a new OTP.
- OTP input (63) only when `otpRequested`.
- Terms `Pressable` (65-68): `accessibilityRole="checkbox"` and `accessibilityState` tell screen readers it is a checkbox. The icon changes between `checkbox-marked` and `checkbox-blank-outline`. The nested `DsText` parts are the coloured links. They are only coloured text, not real links.
- `DsButton` label is "Send OTP" or "Verify & Create Account".

### `styles` (79-83)
`StyleSheet.create` with many rules packed on a few lines.

## 4. How data flows
```
name+phone+terms -> "Send OTP" -> submit -> requestOtp -> Firebase SMS -> setConfirmation
OTP typed -> "Verify & Create Account" -> verifyOtp -> Backend creates passenger, token saved
   -> saveProfileName -> onAuthenticated() -> parent navigates
```

## 5. Try it
Not directly runnable alone. Run the app (`cd passenger-app && npx react-native run-android`), tap Sign Up, use a Firebase test number. Expected: after "Send OTP" an OTP field appears.

## 6. Can it be better?
- Good: terms checkbox is accessible; `otpRequested` is derived, so it cannot go out of sync.
- Weak: very dense lines (34, 36, 61-63, 80-82) are hard to read; the terms words look like links but do nothing; duplicate of LoginScreen; the "Terms" check happens before the OTP is requested, which is fine but the message is only shown as general text; no resend OTP.
- Cleaner way (opinion): one statement per line, and a shared `usePhoneAuth` hook. Also run Prettier (`npx prettier --write`) to format.
- Security: the real consent record should be stored by the backend, not only checked in the app.

## 7. Check yourself
1. How is `otpRequested` found here, and why is that safer than a separate `useState`?
2. What two `authService` calls run after the OTP is typed?
