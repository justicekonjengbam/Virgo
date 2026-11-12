# DriverSettingsScreen.tsx

## 1. Purpose
This is the "Settings" page of the driver app. It lets the driver change two things: full name and city of operation. Phone, vehicle and documents are shown as read-only (`driver-app/src/features/profile/screens/DriverSettingsScreen.tsx:29`).
It is opened by the app's navigation (a parent screen passes `onBack`). It calls `driverProfileService` (`../services/driverProfileService.ts`) to talk to the backend, and `driverAuthError` to turn errors into text.

## 2. Imports, one by one

Third-party:
- `import { useEffect, useState } from 'react';` (line 1). **React** is the UI library. A **hook** (a special function that gives a component memory or side effects. *Example:* `const [n, setN] = useState(0)`). `useState` stores a value that, when changed, redraws the screen. `useEffect` runs code after the screen appears (for example, to load data). Other hooks: `useMemo`, `useRef`.
- `import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 2). **React Native** draws real phone widgets from JavaScript.
  - `ActivityIndicator`: a spinning wheel. *Example:* `<ActivityIndicator size="large"/>`.
  - `SafeAreaView`: a box that avoids the phone notch and edges.
  - `ScrollView`: a box that scrolls when content is tall.
  - `StyleSheet`: a helper to define styles. `StyleSheet.create({a:{flex:1}})`.
  - `View`: a plain box, like `<div>` on the web.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (line 3). An icon font. *Example:* `<MaterialCommunityIcons name="home" size={20}/>`. Used here for the lock icon (line 29).

Project imports (lines 5-12):
- `DriverButton`, `DriverCard`, `DriverPageHeader`, `DriverText`, `DriverTextField` from `driver-app/src/components/*`: the app's own styled button, card box, top bar with back arrow, text, and input field.
- `colors, spacing` from `driver-app/src/theme`: shared colour values and gap sizes.
- `driverAuthError` from `features/auth/utils/driverAuthError`: turns an error object into a message the driver can read.
- `driverProfileService` and the type `DriverProfile` from `../services/driverProfileService`. `type` in the import means "only used for type checking, removed at build".

## 3. Walk through the code

**Component** `export function DriverSettingsScreen({ onBack }: { onBack: () => void })` (line 14). A **component** is a function that returns UI. Input: `onBack`, a function to call when the back arrow is pressed. Output: the screen.

**State** (lines 15-17). `useState` returns a pair: the value and a setter.
- `profile`: the loaded profile or `null` while loading.
- `fullName`, `city`: text in the two inputs.
- `error`: message or `null`. `isSaving`: true while the request runs. `saved`: true after a good save.
Several statements share one line with `;` (a style choice).

**Load on open** (lines 18-20). `useEffect(fn, [])` with an empty list runs `fn` once, when the screen first appears.
`driverProfileService.get()` asks the server for the profile. `.then(next => ...)` runs when data arrives: it stores the profile and fills the inputs (`operating_city ?? ''` means "use empty text if null"). `.catch(cause => setError(driverAuthError(cause)))` shows an error message if the call fails. `void` tells the code "I know this promise is not awaited".

**`save()`** (lines 21-28). `async` means it can wait for the network with `await`.
1. `trim()` removes spaces at both ends. `" Ravi "` becomes `"Ravi"`.
2. If name or city is shorter than 2 characters, show a message and stop (lines 23-24).
3. Set `isSaving` true and clear old messages (line 25).
4. `driverProfileService.update({...})` sends a PATCH to the server. On success it saves the returned profile, refills inputs and sets `saved` (line 26).
5. `catch` shows the error. `finally` always sets `isSaving` false (line 27).

**The returned UI** (line 29), in plain words:
- Header with back arrow and title "Settings".
- A `ScrollView` with `keyboardShouldPersistTaps="handled"` (a tap on the button works even when the keyboard is open).
- If `!profile && !error`: spinner and "Loading your profile...".
- Else: a card with two `DriverTextField`s (each `onChangeText` updates state and clears `saved`), a Save button (`loading={isSaving}` shows a spinner on it), the error text, and a green "saved" text.
- Second card: lock icon, and `profile?.phone_number.replace(/\D/g,'').slice(-10) ?? '—'`. `?.` stops if `profile` is null. `replace(/\D/g,'')` removes every non-digit (`"+91 98765-43210"` becomes `"919876543210"`). `slice(-10)` keeps the last 10 digits (`"9876543210"`).

**Styles** (line 33). `StyleSheet.create` builds the style table. `flex: 1` means "fill all space". `gap` is space between children.

## 4. How data flows
```
screen opens -> useEffect -> driverProfileService.get()
   -> apiClient GET /api/v1/auth/drivers/me -> backend -> JSON profile
   -> setProfile/setFullName/setCity -> redraw

press Save -> save() -> validate -> driverProfileService.update()
   -> PATCH /api/v1/auth/drivers/me -> updated profile -> state -> "saved" text
```

## 5. Try it
Not directly runnable alone. Run the driver app (`cd driver-app && npx react-native start`, then run on a device) and open Settings. Expected: spinner, then your name and city in the inputs. Type one letter as the name and press Save: you see "Enter your full name using at least 2 characters."

## 6. Can it be better?
- Good: input checks before the network call; `finally` resets the loading flag; clear loading, error and success states.
- Weak: very long lines (line 29 is one huge line) are hard to read and to review; several statements per line. The 2-character rule is only in the app, so check that the backend also checks it. The `profile` null check mixes with `error`: if loading fails, the form is shown with empty fields (opinion: show a retry button instead).
- Cleaner way: split the JSX into small components, one statement per line.
```tsx
// before: <DriverCard>...everything on one line...</DriverCard>
// after
return (
  <SafeAreaView style={styles.safe}>
    <DriverPageHeader onBack={onBack} title="Settings" />
    <ProfileForm ... />
    <VerifiedDetails phone={profile?.phone_number} />
  </SafeAreaView>
);
```
- Security: phone is shown only as last 10 digits; no secrets here.

## 7. Check yourself
1. Why does `useEffect` have `[]` as the second argument, and what would happen without it?
2. What does `finally` guarantee in `save()`?
