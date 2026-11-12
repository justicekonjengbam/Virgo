# driver-app/src/features/auth/components/DriverPhoneAuthForm.tsx

## 1. Purpose
A form that asks for a mobile number, sends an OTP (one-time password by SMS), and checks it. It serves both login and signup through the `intent` prop. Used by `DriverLoginScreen.tsx` and `DriverSignupScreen.tsx`. It calls `driverAuthService` and `driverAuthError`.

## 2. Imports, one by one
**Third-party**
- `import { useState } from 'react';` (line 1) A **hook** is a React function that gives a component a feature. `useState` makes a value that the screen remembers and redraws on change. *Example:* `const [n, setN] = useState(0); setN(1)` redraws with 1.
- `import { Alert, Pressable, StyleSheet, View } from 'react-native';` (2) `Alert.alert(title, text)` shows a native popup. `Pressable` is a tappable area. `View` is a box. `StyleSheet.create` makes styles.
- `import type { FirebaseAuthTypes } from '@react-native-firebase/auth';` (3) Type-only import for the `ConfirmationResult` type (the Firebase object used to check the OTP).

**Project**
- `DriverButton`, `DriverText`, `DriverTextField` from `src/components/` (lines 5-7): the app's own button, text and input.
- `colors, spacing` from `src/theme` (8): design values.
- `driverAuthService` and types `DriverAuthIntent`, `DriverRegistrationIdentity`, `DriverSession` from `../services/driverAuthService` (9).
- `driverAuthError` from `../utils/driverAuthError` (10).

## 3. Walk through the code
**Props type** (line 12): `intent` (`'login'` or `'signup'`), optional `onAuthenticated(session)` for login, optional `onPhoneVerified(identity)` for signup. The parent decides what happens next.

**State** (line 15): `fullName`, `phone`, `otp`, `confirmation` (Firebase object or `null`), `message` (error text), `loading`. `otpRequested = confirmation !== null` (line 16) decides if the OTP box shows.

**`validate(requireOtp)`** (17-22): returns an error text or `null`. Signup needs a name of 2+ letters. Phone must match `/^[6-9]\d{9}$/` (10 digits starting with 6-9, Indian mobile). OTP, if required, must be exactly 6 digits. *Example:* `phone='12345'` gives "Enter a valid 10-digit...".

**`requestOtp(restartChallenge = false)`** (23-36): validate; set loading; clear old OTP and confirmation; optionally `resetPhoneChallenge()`; call `driverAuthService.requestOtp(phone)` which asks Firebase to send the SMS and returns the confirmation; show an `Alert`. On error, `driverAuthError` turns it into text. `finally` always stops the loading spinner.

**`verify()`** (37-53): validate with OTP; stop if no confirmation. For signup, `verifySignupPhone` returns an identity and `onPhoneVerified?.(identity)` is called (`?.()` calls only if the prop exists). For login, `verifyOtp(..., 'login')` returns a session and `onAuthenticated?.(session)` is called.

**`changePhone()`** (54-60): ignores taps while loading; clears all phone state and resets the Firebase challenge.

**`editPhone(value)`** (61): keeps only digits (`replace(/\D/g, '')`), and drops the old confirmation so the user must request a new OTP.

**Render** (62): one `View` with: a name field (signup only); phone field with a `+91` prefix (`leading`), `maxLength` 10, numeric keyboard (`inputMode`); when `otpRequested`, an OTP field plus two links "Change number" and "Resend OTP"; the error `message` in red; and one button. The button label and action switch: before OTP it is "Send OTP" and calls `requestOtp()`, after it is "Verify & Login" or "Verify & Continue" and calls `verify()`. `void` marks that the returned promise is ignored on purpose. `<>...</>` is a fragment (group without extra box).

**Styles** (65): `gap: spacing.lg` spaces the children. `otpActions` puts the two links in a row.

## 4. How data flows
```
user types phone -> [Send OTP] -> requestOtp -> driverAuthService -> Firebase -> SMS
user types otp   -> [Verify]   -> verify
    signup: verifySignupPhone -> onPhoneVerified(identity) -> SignupScreen step 2
    login : verifyOtp (+backend) -> onAuthenticated(session) -> LoginScreen -> app
```

## 5. Try it
Not directly runnable alone. Run the app (`cd driver-app && npx react-native run-android`), open Login, enter a Firebase test number (no `+91`), tap Send OTP, enter the test code. Expect a popup "OTP sent", then the login completes.

## 6. Can it be better?
- Good: input checks before any network call, digits-only input, clear loading and error handling, one form for two flows.
- Weak: state and JSX are crammed onto very long lines (15 and 62), hard to read and review. The `Alert` text mentions Firebase test numbers, shown to real users. Validation message says "10-digit" but name/OTP errors are mixed. Many `useState` calls could be one `useReducer`. No countdown for Resend OTP, so users can spam it. No tests.
- Cleaner way: split the JSX into small pieces (`PhoneField`, `OtpField`) and format over many lines like `DriverVehicleVerificationForm.tsx`.
- Security: validation here is only for convenience. The backend must check everything again.

## 7. Check yourself
1. Which callback runs after a successful signup OTP, and which after a login OTP?
2. Why does `editPhone` set `confirmation` to `null`?
