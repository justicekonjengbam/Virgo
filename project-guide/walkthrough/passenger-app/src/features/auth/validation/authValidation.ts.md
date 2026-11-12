# authValidation.ts

File: `passenger-app/src/features/auth/validation/authValidation.ts` (3 lines)

## 1. Purpose
This file holds three small check functions for the login and signup forms. Each one gets the text a user typed and returns an error message, or `undefined` if the text is fine. `LoginScreen.tsx` and `SignupScreen.tsx` call them before they talk to Firebase. The file calls nothing else.

## 2. Imports, one by one
There are no imports. The file uses only built-in JavaScript: regular expressions (regex) and `String.trim()`.

**Regular expression** (a pattern that describes what text is allowed. *Example:* `/^\d{3}$/.test('123')` is `true`, `/^\d{3}$/.test('12a')` is `false`.)

## 3. Walk through the code, top to bottom

### `validateIndianMobile` (line 1)
```ts
export const validateIndianMobile = (phone: string): string | undefined => (/^[6-9]\d{9}$/.test(phone) ? undefined : 'Enter a valid 10-digit Indian mobile number.');
```
- **What it does:** checks that `phone` is exactly 10 digits and the first digit is 6, 7, 8 or 9. These are the starting digits of Indian mobile numbers.
- **Pattern parts:** `^` means "start of text". `[6-9]` means one digit from 6 to 9. `\d{9}` means exactly 9 more digits. `$` means "end of text".
- **`.test(phone)`** is a regex method. It returns `true` or `false`.
- **`cond ? a : b`** is the ternary operator (short if/else). If the test passes it returns `undefined`, otherwise the message.
- **Type `string | undefined`:** the result is either text (an error) or nothing (no error).
- Example: `validateIndianMobile('9876543210')` returns `undefined`. `validateIndianMobile('1234567890')` returns `'Enter a valid 10-digit Indian mobile number.'`.
- **`export const name = (...) => ...`** is an arrow function saved in a constant and exported so other files can import it.

### `validateOtp` (line 2)
Same idea. `/^\d{6}$/` means exactly 6 digits. OTP = One-Time Password, the code sent by SMS. Example: `validateOtp('123456')` gives `undefined`; `validateOtp('12')` gives `'Enter the six-digit OTP.'`.

### `validateFullName` (line 3)
`name.trim().length >= 2`. `trim()` removes spaces at both ends, so `'  A '` becomes `'A'` (length 1, fails). Example: `validateFullName('Ravi')` gives `undefined`; `validateFullName(' ')` gives `'Enter your full name.'`.

Errors: none are thrown. Failures are returned as text.

## 4. How data flows
```
user types phone -> LoginScreen.submit() -> validateIndianMobile(phone)
                                                  |
                       undefined (ok) <-----------+-----------> "Enter a valid..." (shown under the field)
```

## 5. Try it
Not directly runnable, but you can test it in a Node REPL from `passenger-app/`:
```zsh
node -e "console.log(/^[6-9]\d{9}\$/.test('9876543210'))"
```
Expected output: `true`. (`\$` is only escaped for zsh.)

## 6. Can it be better?
- Good: tiny, pure (no side effects), easy to test.
- Weak: the message language is fixed English. The name rule accepts `'12'` as a name. There are no tests (I did not find a test for it; check with `rg -l authValidation passenger-app`). The backend must also validate, because the app can be bypassed.
- Cleaner way (opinion): name the regex as a constant, e.g. `const INDIAN_MOBILE = /^[6-9]\d{9}$/;`, so it can be reused and tested.
- Security: client checks are for user comfort only, not protection.

## 7. Check yourself
1. What does `validateOtp('12345')` return, and why?
2. Why does the function return `undefined` for success instead of `true`?
