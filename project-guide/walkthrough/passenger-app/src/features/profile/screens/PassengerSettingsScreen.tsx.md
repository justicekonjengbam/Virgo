# PassengerSettingsScreen.tsx

## 1. Purpose
A settings form where the passenger edits name, email and preferred language. The phone number is shown but locked. It lives in `features/profile/screens/`. The navigator opens it. It calls `passengerProfileApi` (`../data/passengerProfileApi`).

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` Memory and run-after-draw hooks.
- `import { SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` Safe box, scroll box, style builder, plain box.
- `AppPageHeader` from `../../../components/navigation/AppPageHeader` (header with back and menu).
- `DsButton, DsCard, DsEmptyState, DsLoading, DsText, DsTextField` from `../../../components/design-system`: button, card, empty/error box, spinner, text, input field.
- `colors, spacing` from `../../../theme`.
- `passengerProfileApi, type PassengerProfile` from `../data/passengerProfileApi`.

## 3. Walk through the code, top to bottom
**`PassengerSettingsScreen({ onBack, onMenuPress })`** (lines 9-16).
- Line 10: six states: `profile`, `name`, `email`, `language` (default `'en'`), `saving`, `message`.
- Line 11: on first draw, `passengerProfileApi.get()` loads the profile. `.then` stores it and fills the form fields (`value.email ?? ''` turns null into empty). `.catch` sets "Unable to load your profile."
- Line 12 `save`:
  - `if (name.trim().length < 2) return setMessage(...)` rejects short names. `return setMessage(...)` returns early.
  - `if (email && !/^\S+@\S+\.\S+$/.test(email))` checks the email with a **regular expression** (a text pattern; this one means "no spaces, an @, a dot"). `.test` returns true or false.
  - Then sets `saving`, clears message, calls `update` with trimmed name, `email.trim() || null` (empty becomes null), and language or `'en'`. On success stores the new profile and shows "Profile saved successfully." On failure shows a general error. `finally` ends saving.
- Line 13: no profile and no message yet -> loading spinner.
- Line 14: no profile but a message -> error box with a "Back" button.
- Line 15: the form. The phone field is `editable={false}` and shows only the last 10 digits: `phone_number.replace(/\D/g,'').slice(-10)` removes non-digits (`\D`, global) and keeps the last 10. *Example:* `+91 98765-43210` becomes `9876543210`. The message colour is green if it contains "success", else red. A note says other data cannot be edited.
- Line 17: styles.

## 4. How data flows
```
mount -> GET profile -> fill name/email/language
user edits -> taps Save -> validate -> PATCH profile -> backend
   <- updated profile -> setProfile + "Profile saved successfully."
```

## 5. Try it
Not directly runnable alone. Run the app, open Settings, change the name, save. Expected: a green success line. Enter `a@b` as email: expected a red "Enter a valid email address."

## 6. Can it be better?
- Good: client-side checks; locked phone; clear states.
- Weak: success detection with `message.includes('success')` is fragile; keep a separate `status` state. Language is free text; use a picker with known codes. The initial load error blocks the whole form with only a Back button (no retry). The `catch` hides the real cause. Line 10 and 12 are crammed. The email regex is basic. The `save` return type mixes `void` and a value from `setMessage`.
- Cleaner way: `const [status, setStatus] = useState<{type:'ok'|'error'; text:string}|null>(null)`.
- Security: the server must validate again; client checks are only for comfort. Do not log email or phone.

## 7. Check yourself
1. Why is `email.trim() || null` used when saving?
2. How does the screen decide between spinner, error box and form?
