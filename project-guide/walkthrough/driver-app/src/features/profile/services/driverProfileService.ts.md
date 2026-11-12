# driverProfileService.ts

## 1. Purpose
A small "service" file: it holds the two network calls for the driver profile (read and update). Screens such as `DriverSettingsScreen.tsx` call it instead of calling the network directly. It calls `apiClient` from `driver-app/src/services/apiClient`.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (line 1). Project file `driver-app/src/services/apiClient`. `apiClient` is a pre-configured **axios** object (axios is an HTTP library. *Example:* `axios.get('/x')` fetches a URL). It already knows the server address and adds the login token (I did not read that file here; check it to confirm). Used here to send requests. It can also do `post`, `put`, `delete`.

## 3. Walk through the code

**Type** `export type DriverProfile = {...}` (line 3). A **type** describes the shape of data; it exists only for the compiler. Fields: `full_name` (text), `phone_number` (text), `operating_city` (text or `null`), `onboarding_completed` (true/false), `status` (text). *Example value:* `{ full_name: 'Ravi', phone_number: '+919876543210', operating_city: null, onboarding_completed: true, status: 'active' }`.

**Object** `export const driverProfileService = {...}` (line 5). A plain object with two methods.

- `async get(): Promise<DriverProfile>` (line 6). `Promise<X>` means "will give an X later". It calls `apiClient.get<DriverProfile>('/api/v1/auth/drivers/me')` (line 7): an HTTP GET (read request) to that path. `<DriverProfile>` tells TypeScript what the answer looks like. `response.data` (line 8) is the JSON body. Input: none. Output: the profile. Errors: axios throws if the server answers 4xx/5xx or is unreachable.
- `async update(payload: Pick<DriverProfile, 'full_name' | 'operating_city'>)` (line 10). `Pick<T, keys>` builds a smaller type with only those keys, so the caller may send only name and city. It sends `apiClient.patch(...)` (line 11): HTTP PATCH (change only some fields) with `payload` as the JSON body. Returns the updated profile.
*Example:* `await driverProfileService.update({ full_name: 'Ravi K', operating_city: 'Hubballi' })` returns the new profile.

## 4. How data flows
```
Screen --update({..})--> driverProfileService --PATCH JSON--> apiClient --> backend /api/v1/auth/drivers/me
Screen <--profile------- driverProfileService <--response.data-- apiClient <-- backend
```

## 5. Try it
Not directly runnable (needs the app and a login token). From a shell you could test the backend path with `curl -H "Authorization: Bearer <secret>" http://localhost:8000/api/v1/auth/drivers/me`. `-H` adds a header. Expected: JSON with the fields above.

## 6. Can it be better?
- Good: tiny, typed, one place for these URLs.
- Weak: the type is written by hand and can drift from the backend schema; URLs are repeated strings.
- Cleaner way (opinion): generate the type from the backend's OpenAPI file, or keep one `const PROFILE_URL = '/api/v1/auth/drivers/me'`.
- Security: the token is added by `apiClient`, not here. Nothing risky in this file.

## 7. Check yourself
1. What is the difference between GET and PATCH here?
2. What does `Pick<DriverProfile, 'full_name' | 'operating_city'>` allow and forbid?
