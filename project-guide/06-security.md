# 06. Security

**Security review** means looking for ways a bad person could read, change or break things. This list comes from reading code and searching with `rg`. I did not run attacks or tools like `pip-audit`. Run those yourself (commands at the end). I did not read any real `.env` file, and no secret appears here.

## Findings (real, with evidence)

### High

1. **Predictable ride-start OTP.** The code returns `digits[-4:]` of the passenger's phone number (`backend/app/services/ride_lifecycle_service.py:145`). The OTP (One-Time Password, a short code used once) exists to prove the passenger is in the car. Anyone who knows the number can guess it. *Fix:* random per-ride code, stored hashed.
2. **Weak default signing secret.** `jwt_secret_key` defaults to a public string (`core/config.py:17`). The secret signs all login tokens. If it is not overridden, tokens can be forged. *Fix:* fail at startup in production.
3. **Cleartext traffic enabled.** Both apps set `usesCleartextTraffic="true"` (`passenger-app/android/app/src/main/AndroidManifest.xml:14`, same in `driver-app`). Tokens would travel as plain text over HTTP. *Fix:* only in a debug build.

### Medium

4. **No rate limiting.** No limiter was found (`rg` for `rate`, `slowapi`, `limit` in `backend/app` found nothing relevant). Attackers can try many passwords or request many OTPs (SMS costs money). Applies to `/auth/passengers/*`, driver login, and `/admin/auth/login`.
5. **No CORS configuration** was found in `main.py`. This is safe by default (browsers block other sites) but you will need a strict allow-list if the admin site ever moves to another domain. Never use `*` with credentials.
6. **Passenger refresh skips the database** (`auth_service.py:68-71`). A removed passenger keeps access until the refresh token expires (30 days).
7. **Development OTP is returned in the API reply** when `environment == 'development'` (`routes/auth.py:17`). Fine locally. Make sure production sets `ENVIRONMENT=production`.
8. **Admin token kept in `sessionStorage`** (`admin-app/app.js:1,32`). Any XSS bug in the page could steal it. The code uses an `esc()` helper for values, which is good. Add a **Content-Security-Policy** header (a browser rule that blocks unknown scripts) when serving `/admin`.
9. **Document files are only text keys.** When upload is built, check file type and size, store privately, and give short-lived signed links.

### Low

10. `MAPS_CONTACT_EMAIL` has a personal email default.
11. Auth failure logging uses `logger.warning(..., exc_info=True)` (`auth_service.py:111`). Check that the logs never hold tokens.
12. WebSocket sends the token in the `Authorization` header (`routes/realtime.py:16`). Good. Tokens in URLs would end up in logs.

## What is done well

- Passwords and OTPs are hashed with **Argon2** (`pwdlib`), a slow hash that resists guessing.
- OTP generation uses `secrets.randbelow` (`auth_service.py:44`), a secure random source, not `random`.
- Firebase ID tokens are verified on the server (`verify_id_token`), with a 60-second clock allowance.
- JWT decode pins the algorithm list (`algorithms=[...]`), blocking the "none algorithm" trick.
- Driver and admin tokens have an `actor` claim; admin tokens have a revocable version number.
- The database has CHECK and UNIQUE constraints, so wrong statuses and duplicate ratings are blocked even if code is wrong.
- Ride lookups filter by `passenger_id` (`routes/booking.py:44,57,65`), so passenger A cannot read passenger B's ride. This is called an object-level check.
- `.gitignore` excludes `.env`, `*.db`, keystores and `backend/secrets/`.

## Recommended practices (not yet followed)

1. HTTPS everywhere, HSTS header, and a proxy such as Caddy or nginx in front of uvicorn.
2. Rate limits and lockout on login, OTP and admin login.
3. Secret management (not files): use environment variables from your host's secret store.
4. Dependency audit in CI on every push.
5. Docker image running as a non-root user.
6. Audit log review (`audit_logs` table exists; check it covers all admin actions).
7. Idempotency for booking and accept: ignore a repeated request instead of creating a second ride. Test the "two drivers accept at once" race.
8. Data protection: decide how long to keep location history and phone numbers, and add a delete-account path.
9. Android: enable code shrinking (R8) in release, keep the keystore out of Git (already ignored).
10. Add `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options` headers.

## Commands to run yourself

```bash
cd backend && source .venv/bin/activate
uvx pip-audit            # checks installed Python packages against known-vulnerability lists
cd .. && pnpm audit      # same for JavaScript packages
rg -n 'password|secret|token' -i --glob '!node_modules' --glob '!project-guide' --glob '!graphify-out' . | head -50   # look for hard-coded secrets
git log -p -S'PRIVATE KEY' --all | head   # was a private key ever committed?
```

- `uvx`: runs a Python tool without installing it. `pip-audit` reports packages with known holes.
- `pnpm audit`: asks the npm registry about known holes.
- `rg -n ... -i`: searches text, shows line numbers, ignores letter case. The `--glob '!x'` parts skip folders.
- `git log -p -S'text' --all`: shows every commit that added or removed that text in any branch.

Next: `07-reading-order.md`
