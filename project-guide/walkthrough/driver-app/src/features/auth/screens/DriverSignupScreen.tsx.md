# driver-app/src/features/auth/screens/DriverSignupScreen.tsx

## 1. Purpose
The two-step signup page for drivers. Step 1 verifies the phone with an OTP. Step 2 collects vehicle and document details. Nothing is saved on the backend until step 2 is submitted. Callers: the navigator. It uses `DriverPhoneAuthForm` and `DriverVehicleVerificationForm`.

## 2. Imports, one by one
- `import { useState } from 'react';` (line 1) hook that remembers values. *Example:* `useState<1 | 2>(1)` starts at step 1.
- `import { KeyboardAvoidingView, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (2) Same pieces as the login screen: safe area, keyboard moving, platform check, scroll, tap area, box, styles.
- Project: `DriverAuthHeader` (4), `DriverText` (5), `colors, spacing` (6), `DriverPhoneAuthForm` (7), `DriverVehicleVerificationForm` (8), and types `DriverRegistrationIdentity`, `DriverSession` (9) from `../services/driverAuthService`.

## 3. Walk through the code
**`Props`** (11): `onAuthenticated`, `onBack`, `onHelp`, `onLogin`.

**State** (14-15): `step` is 1 or 2. `identity` holds the verified phone data or `null`.

**`onBasicDetailsVerified(verifiedIdentity)`** (16): saves identity and moves to step 2. It is passed to the phone form as `onPhoneVerified`.

**Render** (17):
- Header back button: on step 1 it calls `onBack`; on step 2 it goes back to step 1 (`() => setStep(1)`).
- Title, `<StepIndicator activeStep={step}/>`.
- Step 1: an intro and `<DriverPhoneAuthForm intent="signup" onPhoneVerified=.../>`.
- Step 2: if `identity` exists, `<DriverVehicleVerificationForm identity={identity} onCompleted={onAuthenticated}/>`, else nothing. `cond ? a : b ? c : null` is a nested ternary.
- Footer: "Already have an account? Login".

**`StepIndicator({ activeStep })`** (20-22): draws circle "1", a line, circle "2", and the labels "Basic Details" and "Verify Documents". The active circle is filled with `colors.primary`; the other is an outline. Text colour and weight change with the step.

**`styles`** (24): circles are 32 by 32 with radius 16. `line` has `flex: 1` so it fills the space between circles.

## 4. How data flows
```
Step 1: PhoneAuthForm --identity--> onBasicDetailsVerified --> setIdentity, setStep(2)
Step 2: VehicleVerificationForm(identity) --> backend register --> session
        --> onAuthenticated(session) --> Navigator
```

## 5. Try it
Not directly runnable alone. Run the app and tap Sign Up. Expect the circle "1" active, then "2" after the OTP is verified.

## 6. Can it be better?
- Good: clear two-step flow; the app keeps the partly done data only in memory; back button logic is correct.
- Weak: if the user closes the app in step 2 they must verify the phone again. Firebase ID tokens expire (about one hour), so a slow step 2 may fail at the backend. Very long JSX lines (17, 21, 24). Layout is repeated from the login screen. The step indicator line is always colored as done.
- Cleaner way: move `StepIndicator` to its own file and use a shared auth layout.
- Security: the identity holds a Firebase ID token in memory only. Good. Do not log it.

## 7. Check yourself
1. When does the backend first learn about a new driver?
2. What does the header back button do on step 2?
