# 05. Improvements, ordered by impact

Effort: S = under a day, M = a few days, L = a week or more. These are my opinions, with evidence.

## Must fix before real users

| # | Problem | Why it matters | Fix | Effort |
|---|---|---|---|---|
| 1 | Ride start OTP is the last 4 digits of the passenger's phone (`ride_lifecycle_service.py:145`) | A driver (or anyone who knows the number) can start the ride without the passenger. | Generate a random 4-digit code per ride, store its hash on the ride, show it to the passenger. | S |
| 2 | Default JWT secret `change-this-development-secret-before-production` (`core/config.py:17`) | If production forgets to set it, anyone can forge tokens. | Refuse to start when `ENVIRONMENT=production` and the secret is the default or shorter than 32 characters. | S |
| 3 | No document upload (`schemas/auth.py:81` takes only a text key) | Staff cannot see real documents. | Add an upload endpoint (`python-multipart` is already a dependency) and private storage (S3 or similar) with signed URLs. | M |
| 4 | Passenger refresh does not check the database (`auth_service.py:68-71`) | A deleted or blocked passenger can keep refreshing. | Load the passenger and check status, as the driver service does (`driver_auth_service.py:70`). | S |
| 5 | Realtime hub is in-process (`realtime_service.py`) | Cannot run two servers or restart without dropping live trips. | Use Redis pub/sub (`redis` is already listed). | M |
| 6 | No payments | A ride business needs money flow. | Pick a gateway (for example Razorpay), build the `payments` table flow, add app screens. | L |
| 7 | Cleartext HTTP allowed in both apps (`AndroidManifest.xml:14`) | Traffic can be read on public Wi-Fi. | Put it in the debug manifest only. Use HTTPS in release. | S |

## Fix soon

| # | Problem | Fix | Effort |
|---|---|---|---|
| 8 | `API_BASE_URL` differs: driver ends in `/api/v1`, passenger does not (`.env.example` files) | Make both the same and add the path in code. | S |
| 9 | No app tests (jest installed, no test files) | Test the API clients and navigators first. | M |
| 10 | Backend `tests/integration` and `tests/e2e` folders are empty | Add API tests with FastAPI `TestClient`. | M |
| 11 | Unused dependencies: `redis`, `psycopg`, `python-multipart`; `react-native-maps`, redux, react-hook-form, netinfo | Remove or use. | S |
| 12 | Repositories only for passenger and driver; other services query directly | Pick one style. Simplest: drop repositories, or add them everywhere. | M |
| 13 | Windows-only helper scripts (`.ps1`, `set "GRADLE_USER_HOME=C:\tmp..."`) | Add `Makefile` or `justfile`, or cross-platform npm scripts. | S |
| 14 | README mentions `documentation/` and `api-docs/` folders that do not exist | Fix the README. | S |
| 15 | `MAPS_CONTACT_EMAIL` defaults to a personal email | Make it required, no default. | S |
| 16 | `graphify-out/` and `project-guide/` are not in `.gitignore` | Add them if you do not want them in Git. | S |
| 17 | **Service area is hard-coded to Dharwad–Hubballi, Karnataka, but the product is for Imphal, Manipur.** Places: the 150 km centre and error text (`services/map_provider_service.py:14,61`), city coordinates for matching (`services/ride_matching_service.py:30-36`), demo places and addresses (`services/booking_service.py:34-38`, `services/home_seed_service.py:19-20,63-65`), a demo ride (`services/driver_menu_service.py:22-23`), and tests (`tests/test_booking_policy.py:10`, `tests/test_ride_matching.py:55-72`, `tests/test_outstation_booking.py:37-38`). | Put the city centre, radius, city list and demo places in settings (`core/config.py`) instead of code. Then set them for Imphal. Replace the Karnataka seed data and fix the tests. Check that Geoapify has good map data for Imphal. | M |

## Clean-code observations

- Many backend files use very long lines (for example `routes/booking.py:9` imports a dozen names on one line; `admin-app/app.js` has whole pages in single lines). Ruff says line length 100 (`pyproject.toml:29`), so run `ruff format` and `ruff check`.
- The same Firebase error-handling block is copy-pasted in `auth_service.py:105-126` and `driver_auth_service.py:151-179`. Move it to `firebase_service.py` as one function.
- `RideMatchingService()` is created inside functions in `realtime_events.py` to avoid a circular import. A **circular import** is two files that need each other. Moving the shared helper into a third file removes the need.
- Route files create service objects at import time (`booking.py:16-18`). FastAPI prefers `Depends(get_service)`, which makes testing and replacing services easier.
- `admin-app/app.js` builds HTML with template strings. It escapes values with `esc()`, which is good, but one missed call becomes **XSS** (attacker script runs in the admin's browser). A small framework or a templating helper would be safer.
- `PostLoginPlaceholderScreen.tsx` is an empty file that nothing imports. Delete it.

## Better tech choices (opinions)

1. **PostgreSQL + PostGIS** for "nearest driver": use a spatial index instead of looping in Python.
2. **Rate limiting** (`slowapi` or a gateway) on login and OTP routes.
3. **Structured logging** and error tracking (Sentry).
4. **Background jobs** (Celery or arq) instead of asyncio timers for offer expiry. Timers die when the process restarts.
5. **OpenAPI-generated TypeScript client** so the apps cannot drift from the API.

## Suggested next 10 tasks

1. Random ride-start OTP (#1).
2. Refuse weak JWT secret in production (#2).
3. Passenger refresh checks the database (#4).
4. Cleartext only in debug (#7).
5. Remove unused dependencies (#11).
6. Same `API_BASE_URL` rule in both apps (#8).
7. Write app tests for the two `apiClient.ts` files (#9).
8. Write API tests for booking and matching with `TestClient` (#10).
9. Document upload and private storage (#3).
10. Redis-backed realtime hub (#5), then start payments (#6).

Next: `06-security.md`
