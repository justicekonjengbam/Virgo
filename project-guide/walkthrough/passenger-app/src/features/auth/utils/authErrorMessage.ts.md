# authErrorMessage.ts

File: `passenger-app/src/features/auth/utils/authErrorMessage.ts` (21 lines)

## 1. Purpose
Firebase and the backend throw errors with technical codes. This file turns any error into one friendly sentence for the user. `LoginScreen.tsx:71` and `SignupScreen.tsx:48` call it inside `catch`. The codes `auth/*-timeout` come from `authService.ts`.

## 2. Imports, one by one
Project import:
```ts
import { ApiError } from '../../../services/apiClient';
```
- `ApiError` is a class defined at `passenger-app/src/services/apiClient.ts:8`. It extends the built-in `Error` and adds an optional `status` (HTTP status number such as 404). *Example:* `new ApiError('Not found', 404)`.
- This file needs it to tell backend errors apart from Firebase errors, using `instanceof`.

## 3. Walk through the code, top to bottom

### `authErrorMessage(error: unknown): string` (line 4)
- **Input:** anything. In `catch`, TypeScript gives `unknown`, because JavaScript lets you throw any value.
- **Output:** a message string.
- Line 5: `error instanceof ApiError` asks "was this made by the ApiError class?". If yes, the message already came from the backend (for example "Phone number not registered"), so it is returned as is.
- Line 6: `typeof error === 'object' && error && 'code' in error ? String(error.code) : ''`. Step by step: it checks the value is an object, is not `null`, and has a property `code`. If so it converts the code to a string. Otherwise the code is empty. This is "type narrowing": it proves to TypeScript that `error.code` is safe to read.
- Lines 7-19: one `if` per known Firebase code. Examples: `auth/invalid-verification-code` gives "The OTP is incorrect. Try again."; `auth/too-many-requests` and `auth/quota-exceeded` share one message.
- Lines 12-15: codes starting with `auth/` and ending in `-timeout` are made by this app, not by Firebase (see `authService.ts:21-32`).
- Line 20: the fallback message.

Example: `authErrorMessage({ code: 'auth/session-expired' })` returns `'The OTP has expired. Request a new one.'`.

## 4. How data flows
```
Firebase / apiClient throws -> catch(error) in screen -> authErrorMessage(error)
      -> ApiError? yes -> error.message
      -> else read error.code -> matching sentence -> setErrorMessage(...) -> red text on screen
```

## 5. Try it
Not directly runnable alone (it imports React Native code through apiClient). Read the code and trace the example above by hand.

## 6. Can it be better?
- Good: all error text lives in one place; safe against odd error values.
- Weak: a long chain of `if` lines. Some messages mention "emulator" and "SHA-1" (line 12, 17), which end users cannot act on. No tests.
- Cleaner way (opinion):
```ts
const MESSAGES: Record<string, string> = {
  'auth/invalid-phone-number': 'Enter a valid Indian mobile number.',
  // ...
};
return MESSAGES[code] ?? 'Unable to continue. Please try again.';
```
- Security: showing raw backend messages (line 5) is fine only if the backend never puts secrets in them.

## 7. Check yourself
1. Why does the function check `error instanceof ApiError` before reading `code`?
2. Which codes are created by the app itself and not by Firebase?
