# passengerProfileApi.ts

## 1. Purpose
Two backend calls for the passenger profile: read it and update it. Used by `PassengerSettingsScreen.tsx`. It calls `apiClient` (`src/services/apiClient`).

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (line 1) The shared HTTP client. *Example:* `apiClient.get('/x')` returns an object with `.data`.

## 3. Walk through the code, top to bottom
**`PassengerProfile`** (line 3): `full_name`, `phone_number`, `email` (string or null), `preferred_language`.

**`passengerProfileApi`** (lines 4-7):
- `get` (5): GET `/api/v1/passengers/me/profile`; returns the profile. `(await ...).data` waits for the reply and takes the body.
- `update(payload)` (6): PATCH the same path. `payload` has the type `Partial<Pick<PassengerProfile, 'full_name'|'email'|'preferred_language'>>`. `Pick` keeps only those three fields (the phone cannot be changed). `Partial` makes each optional. *Example:* `update({ email: null })` is valid; `update({ phone_number: '1' })` is a type error. Returns the saved profile.
Errors from `apiClient` (network, 4xx, 5xx) are thrown to the caller.

## 4. How data flows
```
Settings screen -> update({full_name:'Asha'}) -> PATCH /api/v1/passengers/me/profile -> backend
   <- full profile <- screen stores it
```

## 5. Try it
Not directly runnable alone. In app code: `const p = await passengerProfileApi.get(); console.log(p.full_name);`. Expected: the logged-in passenger's name.

## 6. Can it be better?
- Good: tiny; the type blocks edits to the phone number.
- Weak: the type is only compile-time; the backend must also refuse such fields. No tests.
- Security: relies on the auth token that `apiClient` adds (I believe; check `apiClient.ts`). Profile data includes phone and email, so do not log it.

## 7. Check yourself
1. Why is `phone_number` missing from the update type?
2. What do `Partial` and `Pick` do?
