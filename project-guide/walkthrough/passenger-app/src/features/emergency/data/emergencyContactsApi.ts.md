# emergencyContactsApi.ts

## 1. Purpose
This file fetches the passenger's emergency contacts from the backend. It sits in the "data" layer of the emergency feature. `EmergencyContactsScreen.tsx` calls it. It calls `services/apiClient.ts`.

## 2. Imports, one by one
Project import:
- `import { apiClient } from '../../../services/apiClient';` (line 1)
  - **apiClient** (a pre-configured HTTP client. *Example:* `apiClient.get('/x')` sends a GET request to the backend). It is made with `axios.create` in `passenger-app/src/services/apiClient.ts:43`.
  - This file needs it to talk to the backend with the right base URL.
  - It can also send `post`, `put`, `delete` requests.

## 3. Walk through the code, top to bottom
### Type `EmergencyContact` (lines 3-8)
**Type** (a TypeScript description of the shape of an object. It exists only while coding and is removed at build time. *Example:* `{ id: 1 }` matches `{ id: number }`).
Fields: `id`, `name`, `phone_number`, and `relationship`, which is `string | null` (text, or nothing). The names use snake_case because the backend sends them that way.

### Object `emergencyContactsApi` (lines 10-13)
- `list` is an **async function** (a function that waits for slow work, like the network, and returns a **Promise**, which is a "result later" box). *Example:* `await list()` gives an array.
- `apiClient.get<EmergencyContact[]>(url)` sends a GET request to `/api/v1/passengers/me/emergency-contacts`. The part in `< >` tells TypeScript the answer data is a list of contacts.
- `await` waits for the response. `.data` is the body of the response (the JSON turned into objects).
- Output: `EmergencyContact[]`, for example `[{ id: 1, name: 'Asha', phone_number: '+91 98765', relationship: null }]`.
- Errors: if the network fails or the server answers 4xx/5xx, the Promise rejects. The caller must catch it. The word `me` in the URL means the backend finds the passenger from the login token.

## 4. How data flows
```
Screen --list()--> emergencyContactsApi --GET--> apiClient --HTTP--> backend
Screen <-- array -- .data <------------------ JSON response -----------
```

## 5. Try it
Not directly runnable. It needs the app, a running backend and a login. From a screen: `emergencyContactsApi.list().then(console.log)`.

## 6. Can it be better?
- Good: very small, typed, one job.
- Weak: only `list` exists. No add, edit or delete. The URL is a string written inline.
- Cleaner way (opinion): put the shared URL prefix in one constant when more endpoints are added.
- Security: the phone numbers are personal data. They travel over whatever URL `apiClient` uses; use HTTPS in production.

## 7. Check yourself
1. Why is `relationship` typed `string | null`?
2. What does `me` in the URL tell the backend?
