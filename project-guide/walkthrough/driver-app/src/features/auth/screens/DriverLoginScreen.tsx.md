# driver-app/src/features/auth/screens/DriverLoginScreen.tsx

## 1. Purpose
The login page for drivers. It shows a title, the phone/OTP form, and a link to sign up. The navigator (`navigation/DriverNavigator.tsx`, probably) shows it and passes callbacks. It uses `DriverAuthHeader`, `DriverText` and `DriverPhoneAuthForm`.

## 2. Imports, one by one
**Third-party**: `import { KeyboardAvoidingView, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 1)
- `SafeAreaView`: keeps content away from notches and system bars.
- `KeyboardAvoidingView`: moves content up when the keyboard opens. *Example:* the OTP field stays visible.
- `Platform`: tells which phone system runs (`Platform.OS === 'ios'`).
- `ScrollView`: a scrollable area. `Pressable`: tap area. `View`: box. `StyleSheet`: styles.

**Project**
- `DriverAuthHeader` from `src/components/auth/DriverAuthHeader` (3): top bar with back and help.
- `DriverText` (4): the app's text component.
- `colors, spacing` from theme (5).
- `DriverPhoneAuthForm` from `../components/DriverPhoneAuthForm` (6).
- `type DriverSession` from `../services/driverAuthService` (7): type only.

## 3. Walk through the code
**`Props`** (9): four callbacks from the parent: `onAuthenticated(session)`, `onBack`, `onHelp`, `onSignup`.

**`DriverLoginScreen`** (11-13) returns one tree:
`SafeAreaView > KeyboardAvoidingView > [DriverAuthHeader, ScrollView > View(form)]`.
- `behavior={Platform.OS === 'ios' ? 'padding' : undefined}`: on iPhone add padding; on Android the system already handles the keyboard.
- `keyboardShouldPersistTaps="handled"`: a tap on a button works even while the keyboard is open.
- Title "Welcome / Login Now!" (`{'\n'}` is a new line), a short intro, then `<DriverPhoneAuthForm intent="login" onAuthenticated={onAuthenticated}/>`, which does all the real work. Below it, "Don't have a Driver account?" and a `Sign Up` link calling `onSignup`.

**`styles`** (15): `form` is centred with `maxWidth: 520` so tablets look fine. `paddingTop: 72` leaves room below the header.

## 4. How data flows
```
Navigator -> DriverLoginScreen -> DriverPhoneAuthForm -> driverAuthService
                                          |
                          session ---> onAuthenticated(session) ---> Navigator (go to dashboard)
```

## 5. Try it
Not directly runnable alone. Run the app (`cd driver-app && npx react-native run-android`) while logged out. Expect the login page.

## 6. Can it be better?
- Good: thin screen, logic lives in the form and service, keyboard and notch handled, tablet width capped.
- Weak: whole JSX is one 400-character line. `SafeAreaView` from `react-native` is deprecated in new React Native versions (opinion: use `react-native-safe-area-context`; check the RN version). Text is hard-coded English. Straight quote in "Don’t" is fine. Layout is duplicated with `DriverSignupScreen.tsx`.
- Cleaner way: a shared `AuthScreenLayout` component used by both screens.
- Security: none here. No secrets handled.

## 7. Check yourself
1. Which component sends the OTP?
2. What does `keyboardShouldPersistTaps="handled"` change?
