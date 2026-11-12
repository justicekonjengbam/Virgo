# LoginScreen.tsx

File: `passenger-app/src/features/auth/screens/LoginScreen.tsx` (152 lines)

## 1. Purpose
The login screen. The passenger types a phone number, gets an SMS code (OTP = One-Time Password), types it, and is logged in. It is a **React component** (a function that returns what to draw on screen). A parent navigator (not read here) renders it and gives it four callbacks. It calls `authService.ts`, `authErrorMessage.ts`, `authValidation.ts`, and shared UI components.
Note: the comment on line 31 says "Authentication is intentionally not wired yet". That is out of date, because `submit` does call `authService`.

## 2. Imports, one by one
Third-party:
- `import { useState } from 'react';` **useState** is a React **hook** (a special function that gives a component memory. *Example:* `const [n, setN] = useState(0)`; calling `setN(1)` redraws the screen with `n = 1`).
- `from 'react-native'`: React Native is a framework that draws real phone widgets from JavaScript. Items used: `Alert` (system popup. *Example:* `Alert.alert('Hi','text')`), `KeyboardAvoidingView` (moves content up when the keyboard opens), `Platform` (tells iOS from Android), `SafeAreaView` (keeps content out of notches), `ScrollView` (scrollable area), `StyleSheet` (builds style objects), `View` (a box, like a div), `useWindowDimensions` (hook that returns the screen `width` and `height`).
- `import { FirebaseAuthTypes } from '@react-native-firebase/auth';` used only for a type on line 38.

Project (all paths under `passenger-app/src/`):
- `AuthHeader`, `AuthInput`, `AuthPrompt`, `RememberMe` from `components/auth/*`: the top bar with back/help, a labelled text field, the "Don't have an account? Sign Up" line, and a checkbox.
- `DsButton`, `DsText` from `components/design-system`: the app's own button and text (Ds = design system).
- `colors`, `spacing` from `theme`: colour and size constants.
- `authService` from `../services/authService`; `authErrorMessage` from `../utils/authErrorMessage`; `validateIndianMobile`, `validateOtp` from `../validation/authValidation`.

## 3. Walk through the code, top to bottom

### `LoginScreenProps` (24-29)
A TypeScript type for the props (inputs): `onBack`, `onAuthenticated`, `onHelp`, `onSignup`, each a function with no arguments.

### The component (32)
`export function LoginScreen({ onBack, onAuthenticated, onHelp, onSignup }: LoginScreenProps)` receives the props and **destructures** them (pulls named values out of an object).

### State (33-44)
- `width` from `useWindowDimensions()`.
- `phone`, `otp`, `rememberMe`: the form values.
- `otpRequested`: `true` after the SMS was requested.
- `confirmation`: the Firebase object needed later to check the OTP; starts `null`.
- `submitting`: shows the spinner on the button.
- `errorMessage`, `phoneError`, `otpError`: texts to show.
- Line 45: `pagePadding = Math.max(spacing.xl, Math.min(42, width * 0.055))` makes side padding 5.5% of the width, but never below `spacing.xl` and never above 42.

### `submit` (47-75)
`async` means the function can `await` (pause until a Promise finishes).
1. Validate (48-54). Phone is always checked; OTP only after it was requested. If any error exists, show the general message and stop.
2. `setSubmitting(true)` and clear the error.
3. **First press** (`!otpRequested`): `authService.requestOtp(phone, 'login')` returns the confirmation. Save it, set `otpRequested`, and show an `Alert` popup.
4. **Second press** (`else if (confirmation)`): `authService.verifyOtp(confirmation, otp, 'login')` checks the code and saves the session. Then `onAuthenticated()` tells the parent to move on.
5. `catch` turns any error into text with `authErrorMessage(error)`. `finally` always stops the spinner.

### JSX (77-142)
**JSX** is HTML-like syntax inside JavaScript. Key parts:
- `behavior={Platform.OS === 'ios' ? 'padding' : undefined}`: padding only on iOS.
- Phone `AuthInput` (94-111): `onChangeText` runs on every key press. `value.replace(/\D/g, '')` removes every non-digit (`\D` = non-digit, `g` = all matches). It also resets `otp`, `otpRequested` and `confirmation`, so changing the number forces a new OTP.
- OTP input (112-123) shows only when `otpRequested` is true (`cond ? <X/> : null`).
- `DsButton` label changes: "Send OTP" or "Verify & Sign In" (128).
- `{errorMessage ? <DsText .../> : null}` shows red text only if there is a message.
- `Welcome{`\n`}Login Now!` puts a line break inside the title.

### `styles` (145-152)
`StyleSheet.create({...})` defines layout: `flex: 1` fills space, `gap` is spacing between children, `maxWidth: 560` stops the form from becoming too wide on tablets.

## 4. How data flows
```
tap "Send OTP" -> submit() -> validateIndianMobile -> authService.requestOtp -> Firebase sends SMS
   -> setConfirmation, setOtpRequested(true) -> OTP field appears
tap "Verify & Sign In" -> submit() -> validateOtp -> authService.verifyOtp -> Backend tokens saved
   -> onAuthenticated() -> parent shows the home screen
error at any step -> authErrorMessage -> red text
```

## 5. Try it
Not directly runnable alone. Run the app and use a Firebase test number:
```zsh
cd passenger-app && npx react-native run-android
```
`npx` runs a locally installed tool; `run-android` builds and starts the app on an emulator. Expect the login screen; after "Send OTP" you should see the popup "OTP requested".

## 6. Can it be better?
- Good: validation before network calls; the OTP resets when the phone changes; the spinner always stops (`finally`).
- Weak: stale doc comment (line 31); `rememberMe` is stored in state but never used; line 50 and 119 put several statements on one line; the OTP-sent message is long and mentions Firebase Console (dev wording); login and signup repeat almost the same code; Alert text says "For a real number" which is a developer note; no resend-OTP or cooldown button; no tests.
- Cleaner way (opinion): move the shared logic into a `usePhoneAuth` custom hook used by both screens.
- Security: OTP is never logged here (good). A cooldown would reduce SMS abuse.

## 7. Check yourself
1. Why does changing the phone text reset `confirmation` and `otpRequested`?
2. What decides whether `submit` requests an OTP or verifies one?
