# driver-app/src/features/auth/components/DriverVehicleVerificationForm.tsx

## 1. Purpose
Step 2 of driver signup. The driver enters vehicle details and four document numbers, picks a file for each document, and submits everything at once. It is shown by `DriverSignupScreen.tsx` after the phone is verified. It calls `driverAuthService.completeRegistration` and `driverAuthError`.

## 2. Imports, one by one
**Third-party**
- `import { useState } from 'react';` (line 1) hook for remembered values. *Example:* `const [city, setCity] = useState('Hubali')`.
- `import { Pressable, StyleSheet, View } from 'react-native';` (2) tappable area, styles, box.
- `import { errorCodes, isErrorWithCode, pick, types } from '@react-native-documents/picker';` (3) A library that opens the phone's file chooser. `pick({type:[types.pdf]})` opens it and returns the chosen files. `types.images` and `types.pdf` limit the kinds. `isErrorWithCode` and `errorCodes.OPERATION_CANCELED` let us tell "user pressed back" from a real error.
- `import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';` (4) Icon font. *Example:* `<MaterialCommunityIcons name="check-circle" size={25}/>`.

**Project**
- `DriverButton`, `DriverCard`, `DriverText`, `DriverTextField` (lines 6-9) from `src/components/`.
- `colors, spacing` from `src/theme` (10).
- `driverAuthService` and types from `../services/driverAuthService` (11-15). `driverAuthError` from `../utils/driverAuthError` (16).

## 3. Walk through the code
**Props** (18-21): `identity` (token, name, phone from step 1) and `onCompleted(session)`.

**`DocumentType`** (22) and **`documents`** (23-28): four document kinds, each a tuple `[key, title, input label]`. The form loops over this list, so adding a document is one line.

**`seatsByVehicleType`** (29): default seats: car 4, bike 2, auto 3. `as const` makes it read-only.

**State** (32-48): city (default "Hubali"), registration, make, model, year, color, category, seats, `numbers` (one text per document), `files` (the picked file address per document), `message`, `loading`. `Record<DocumentType, string>` means an object with exactly those four keys.

**`choose(type)`** (49-57): opens the picker (`allowMultiSelection: false`). `const [file] = ...` takes the first item. `setFiles(current => ({...current, [type]: file.uri}))` copies the old object and sets one key (`[type]` is a computed key). If the user cancels, no message; other errors show a text.

**`submit()`** (58-95): the `if` (59-70) stops when something is empty, year is not 4 digits, seats not a number, or any document has a number shorter than 4 or no file (`documents.some(...)`). Otherwise it sets loading and calls `completeRegistration(identity, {...})`. It trims text, uppercases the registration, converts year and seats with `Number()`, sends `undefined` for empty colour, and maps documents to `{document_type, document_number, storage_key}`. `files[type]!` says "trust me, not undefined" (safe because of the check above). `storage_key` here is just the local file address `file.uri`.

**Render** (96-203): a title, a note, then for each document a text field plus an upload `Pressable` showing a check icon once chosen. Then vehicle fields, three vehicle-type buttons (`['car','bike','auto'] as const`; the selected one is `primary`, others `secondary`; tapping also sets default seats), seats field, an info card, the error `message`, and the submit button.

**Styles** (206-228): layout via `gap`, outline for the upload button, soft coloured notice card.

## 4. How data flows
```
pick() -> file.uri --> files state
text fields --------> numbers/other state
[Submit] -> validate -> completeRegistration(identity, payload)
   -> POST /api/v1/auth/drivers/firebase/register -> DriverSession
   -> onCompleted(session) -> SignupScreen -> app
```

## 5. Try it
Not directly runnable alone. Run the app, sign up, verify the phone, then fill step 2. Expect the button to show a spinner and then the dashboard on success, or a red message on failure.

## 6. Can it be better?
- Good: clean multi-line formatting, data-driven document list, cancel handled, all-or-nothing submit.
- Weak: the file is not uploaded. Only the local `uri` is sent as `storage_key` (line 86), so the backend cannot read it unless an upload step exists elsewhere. Please check how the backend uses `storage_key`. Year and seats only checked by regex (no range, e.g. year 1000). Aadhaar number length is not checked. `maxLength={2}` seats but any number passes. The "document selected" text does not show the file name. No tests.
- Cleaner way: upload the file first, then send the returned storage key.
- Security: Aadhaar and licence images are sensitive personal data. They need a private storage bucket, access control and encryption. Do not log them.

## 7. Check yourself
1. What exactly is sent as `storage_key`, and why can that be a problem?
2. What happens when the user presses back inside the file picker?
