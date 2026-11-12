# healthService.ts

## 1. Purpose
Asks the backend if it is alive. `HealthCheckScreen.tsx` calls it. It calls `services/apiClient.ts`.

## 2. Imports, one by one
- `import { apiClient } from '../../../services/apiClient';` (line 1). **apiClient** is the shared axios HTTP client (`passenger-app/src/services/apiClient.ts:43`). *Example:* `apiClient.get('/health')`. It can also post, put and delete.

## 3. Walk through the code, top to bottom
- Lines 3-7: type `HealthStatus` = `{ status, version, environment }`, all strings. *Example:* `{ status: 'ok', version: '0.1.0', environment: 'dev' }` (example values are mine).
- Lines 9-14: `healthService.check()` is async and returns `Promise<HealthStatus>` (a result that arrives later). Line 11: `apiClient.get<HealthStatus>('/health')` sends GET to `/health` and waits. Line 12 returns `response.data`, the JSON body. If the request fails, the Promise rejects (the caller handles it).

## 4. How data flows
```
Screen -> healthService.check() -> apiClient GET /health -> backend
Screen <- HealthStatus <- response.data <- JSON
```

## 5. Try it
Not directly runnable. With the backend on, `curl <backend-url>/health` shows the same JSON this function returns.

## 6. Can it be better?
- Good: tiny and typed.
- Weak: `/health` has no `/api/v1` prefix, unlike other endpoints; that is fine if the backend does it on purpose. No runtime check that the data really has these fields.
- Security: low risk; do not expose secrets in the health response.

## 7. Check yourself
1. What does `response.data` hold?
2. What happens to the Promise if the server is down?
