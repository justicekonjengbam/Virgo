# driver-app/src/features/auth/screens/DriverOnboardingScreen.tsx

## 1. Purpose
A screen where an already logged-in driver adds the city and vehicle details. It is the older, simpler flow: it has no document step (its own alert says "Document verification will be added next"). The newer signup flow (`DriverVehicleVerificationForm.tsx`) does this together with documents. It is referenced by `navigation/DriverNavigator.tsx`. It calls `driverAuthService.completeOnboarding`.

## 2. Imports, one by one
- `import { useState } from 'react';` (line 1) remembered values.
- `import { Alert, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (2) popup, safe area, scroll, box, styles.
- Project: `DriverButton`, `DriverText`, `DriverTextField` (4-6); `colors, spacing` (7); `driverAuthService`, type `DriverSession` (8); `driverAuthError` (9).

## 3. Walk through the code
**Props** (11): `onCompleted(session)`.

**State** (13): city (default "Hubali"), registration, make, model, year, color, category (`'car' | 'bike' | 'auto'`), seats (default '4'), message, loading.

**`submit`** (14), all on one line:
1. If city, registration, make or model is empty, year is not 4 digits, or seats not digits, `return setMessage('Complete every required vehicle field.')`.
2. `setLoading(true)`, clear the message.
3. `completeOnboarding({...})` posts to `/api/v1/auth/drivers/onboarding` and updates the saved session. Values are sent un-trimmed and registration is not uppercased (compare with the verification form).
4. On success: `Alert.alert(...)` then `onCompleted(session)`.
5. On error: `setMessage(driverAuthError(error))`. `finally` sets loading false.

**Render** (15): heading text, then text fields for city, registration, make, model, year (numeric, max 4), color; three buttons for the vehicle type (selected one is `primary`); a seats field with `maxLength={1}`; an error message; and the button "Save & continue" (label changes to "Saving…" while loading).

**Styles** (17): `safe` uses `colors.background`. Other screens use `colors.surface`.

## 4. How data flows
```
Fields -> submit -> completeOnboarding -> POST /api/v1/auth/drivers/onboarding (Bearer token via apiClient)
       <- DriverProfile -> merged into saved session -> Alert -> onCompleted(session)
```

## 5. Try it
Not directly runnable alone. Only reachable if the navigator shows it for a logged-in driver with `onboarding_completed` false (check `DriverNavigator.tsx` to confirm).

## 6. Can it be better?
- Good: simple, validates before the request, shows readable errors.
- Weak: the button never gets `loading={loading}` (line 15), so a user can tap twice and only the label changes. `maxLength={1}` for seats blocks values over 9. Values are not trimmed or uppercased. Heavy duplication with `DriverVehicleVerificationForm.tsx`. The alert text promises a future feature. May be dead code now that signup registers everything at once (I am not sure; search with `rg DriverOnboardingScreen driver-app/src`).
- Cleaner way: reuse one vehicle form component, or delete this screen if not needed.
- Security: none special. The backend must validate again.

## 7. Check yourself
1. How does this screen differ from `DriverVehicleVerificationForm` in what it sends?
2. Why can the user tap Save twice quickly?
