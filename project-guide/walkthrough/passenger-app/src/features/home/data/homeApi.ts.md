# homeApi.ts

## 1. Purpose
Fetches the passenger's Home data (name, saved places, ride categories, recent rides) from the backend. The Home screen calls it. It calls `services/apiClient.ts`.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (1). The shared axios HTTP client (`passenger-app/src/services/apiClient.ts:43`). *Example:* `apiClient.get('/x')`.
- `import type { PassengerHome } from '../domain/homeTypes';` (2). A type only, from `homeTypes.ts`. It describes the answer shape.

## 3. Walk through the code, top to bottom
- Lines 4-9: object `homeApi` with `getHome()`, an async function returning `Promise<PassengerHome>`.
- Line 6: `apiClient.get<PassengerHome>('/api/v1/passengers/me/home')` sends GET and waits (`await`). `me` means "the logged-in passenger".
- Line 7: returns `response.data`, the JSON body.
- Errors: network or 4xx/5xx makes the Promise reject; the caller must catch.

Example result: `{ passenger_name: 'Asha', saved_places: [], ride_categories: [...], recent_rides: [] }`.

## 4. How data flows
```
Home screen -> homeApi.getHome() -> apiClient GET -> backend
Home screen <- PassengerHome <- response.data
```

## 5. Try it
Not directly runnable. Needs a login token. With a token: `curl -H "Authorization: Bearer <secret>" <backend>/api/v1/passengers/me/home` (the auth header format is my assumption; check `apiClient.ts`).

## 6. Can it be better?
- Good: tiny and typed.
- Weak: the type is trusted, not checked at runtime. The URL is a string literal.
- Security: depends on the token that `apiClient` adds.

## 7. Check yourself
1. What does `import type` do?
2. What does `me` in the URL mean?
