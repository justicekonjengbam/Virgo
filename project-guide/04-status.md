# 04. Status: what is done and what is left

Status words: **done** (works end to end in code), **partial** (some parts exist), **missing** (not found in code), **broken/risky** (exists but has a known fault). Evidence is a file and line. "Not found in code" means I searched with `rg` and found no code for it. I did not run the apps, so "done" means the code is written, not that it was tested on a device.

| Feature | Status | Evidence | Notes |
|---|---|---|---|
| Passenger sign-up and login with Firebase phone OTP | done | `services/auth_service.py:73-99` | Also an older backend-OTP path (`request_otp`, line 31). |
| Passenger refresh token | partial | `auth_service.py:68-71` | Does not check that the passenger still exists. |
| Driver sign-up, login, refresh | done | `services/driver_auth_service.py:33-76` | Refresh checks status. |
| Driver registration with vehicle and documents | partial | `driver_auth_service.py:78-90`, `schemas/auth.py:81` | Documents are only a text `storage_key`. There is no upload endpoint or file storage. |
| Document review by staff | done | `services/driver_document_review_service.py` | Approve or reject in the admin site. |
| Driver becomes active automatically | done | `driver_readiness_service.py:14-36` | Needs 4 verified documents and a verified vehicle. |
| Admin accounts, roles, session version | done | `admin_auth_service.py`, `api/dependencies/admin_auth.py:22-25` | |
| Admin web console | partial | `admin-app/app.js` | Pages: overview, documents, drivers, support, outstation, account. No rides page, no payments page, no reports. |
| Maps: search, reverse lookup, route | done | `services/map_provider_service.py` | 150 km area limit (line 14, 61). |
| Fare estimate | done | `services/booking_service.py:40-64` | Toll and parking are 0. |
| Book a ride | done | `routes/booking.py:31`, `booking_service.py` | |
| Driver matching and 30-second offers | done | `services/ride_matching_service.py:29-32` | Picks the nearest driver; if none accepts, moves on. |
| Ride lifecycle (arrive, start, complete, cancel) | done | `services/ride_lifecycle_service.py` | Start OTP is the last 4 digits of the passenger phone (line 145). Not random. |
| Ratings | done | `routes/booking.py:63`, `ride_hailing.py:241` | |
| Live updates by WebSocket | done (one server only) | `routes/realtime.py`, `services/realtime_service.py` | Hub is in memory. |
| Live driver location on passenger map | done | `realtime_events.py:79` (`publish_driver_location`) | |
| Outstation booking (manual) | done | `services/outstation_service.py` | Staff assign drivers by hand. |
| Saved places, emergency contacts, profile | done | `routes/home.py`, `emergency_contacts.py`, `passenger_profile.py` | |
| Notifications | partial | `routes/notifications.py`, table `notifications` | In-app list only. No push messages (FCM) code found. |
| Support tickets | partial | table `support_tickets`, admin page | Passenger-side creation was not traced; admin can resolve. |
| Payments | **missing** | table `payments` (`ride_hailing.py:227`) | No service, route or app screen uses it. No payment gateway. |
| Driver earnings, payouts | missing | not found in code | `driver_dashboard_service.py` shows dashboard numbers only. |
| Promo codes, surge pricing | missing | not found in code | Only a fixed night surcharge. |
| Push notifications | missing | not found in code | |
| Ride history | partial | `features/rides/screens/MyRidesScreen.tsx` | |
| Production database (PostgreSQL), Redis | missing | `psycopg`, `redis` unused | |
| Deployment (Docker, CI) | missing | no files found | |
| Backend tests | partial | `backend/tests/` (9 test files; folders `integration/` and `e2e/` are empty) | Covers booking policy, matching, schema, driver auth, outstation, phone format, realtime. |
| App tests | **missing** | `jest` installed, zero test files | |

## Summary

**Finished work:** passenger and driver login, driver onboarding review, estimate → book → match → accept → ride → complete → rate, live updates, admin console basics, outstation manual flow, map service.

**Half finished:** document upload (no real storage), notifications (no push), support tickets, admin console reach.

**Not started:** payments, earnings and payouts, push notifications, deployment, app tests.

**Unclear (check by running):** whether every screen works against the real backend on a device. I read the code but did not run the apps.

Next: `05-improvements.md`
