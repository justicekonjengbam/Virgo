# 02. Architecture

**Architecture** means how the parts of a program are arranged and how they talk. *Example:* the plan of a house: which rooms exist and which doors join them.

## The big picture

```
┌────────────────┐   ┌────────────────┐   ┌──────────────┐
│ passenger-app  │   │  driver-app    │   │  admin-app   │
│ (React Native) │   │ (React Native) │   │ (HTML + JS)  │
└───────┬────────┘   └───────┬────────┘   └──────┬───────┘
        │ HTTP /api/v1 + WebSocket /api/v1/realtime  │ HTTP /api/v1/admin
        ▼                    ▼                      ▼
┌───────────────────────────────────────────────────────────┐
│ backend/app/main.py  → create_app() builds the FastAPI app │
│   routes (api/v1/routes)  ← only parse input, call below   │
│   services               ← the business rules               │
│   repositories           ← only for Driver and Passenger    │
│   models + schemas       ← DB tables / request-reply shapes │
│   RealtimeHub            ← keeps WebSocket connections      │
└──────┬───────────────────┬──────────────────┬─────────────┘
       ▼                   ▼                  ▼
   SQLite DB          Firebase Admin       Geoapify API
 (Alembic migrates)  (verify phone token)  (search, route)
```

The apps and the backend are separate programs. They only meet over the network. That is why code-graph tools show no link between them.

## Layers inside the backend

A **layer** is one level of code with one job.

1. **Routes** (`backend/app/api/v1/routes/*.py`): receive a web request, check the shape of the data, call a service, return a reply. 64 route functions exist.
2. **Dependencies** (`api/dependencies/auth.py`, `driver_auth.py`, `admin_auth.py`): code that runs before a route. *Example:* `Depends(get_current_passenger)` reads the token and gives the route the logged-in passenger, or stops with 401.
3. **Services** (`backend/app/services/`): the rules. *Example:* "a driver can only accept an offer that has not expired".
4. **Repositories** (`repositories/`): thin wrappers for database reads and writes. Only passengers and drivers have one; other services query the database directly. This is an inconsistency (see `05-improvements.md`).
5. **Models** (`models/user.py`, `models/ride_hailing.py`): Python classes that match database tables.
6. **Schemas** (`schemas/*.py`): **Pydantic** classes (they check and describe data. *Example:* `phone_number` must be a string of 10 digits). They define what comes in and goes out of the API.

## Startup order (`backend/app/main.py`)

1. `create_app()` (line 22) loads settings, builds `FastAPI(...)` (line 30), and runs a **lifespan** function (code that runs once at start and once at stop).
2. At start: run Alembic migrations (`db.py:33`, if `AUTO_MIGRATE` is true) and make the first admin from env values.
3. `include_router(health_router)` mounts `/health` (line 32). `include_router(api_router, prefix=...)` mounts everything else under `/api/v1` (line 33).
4. `/admin` is mounted as static files from `admin-app/` (line 36).
5. `app = create_app()` (line 40) is the object uvicorn runs.

## Route groups (`api/v1/router.py:19-32`)

| URL prefix | File | Who calls |
|---|---|---|
| `/auth/passengers` | `auth.py` | passenger app (signup, login, OTP, refresh) |
| `/drivers/...` auth | `drivers_auth.py` | driver app |
| `/drivers/me` | `driver_matching.py`, `driver_dashboard.py` | driver app (online, offers, trip steps) |
| `/drivers/menu` | `driver_menu.py` | driver app menu |
| `/passengers/me` | `booking.py`, `home.py` | passenger app (estimate, book, status) |
| `/passengers/me/profile`, `/emergency-contacts`, `/notifications` | matching files | passenger app |
| `/maps` | `maps.py` | both apps (search, reverse, route) |
| `/outstation` | `outstation.py` | passenger + admin |
| `/admin` | `admin.py` | admin site |
| `/realtime` | `realtime.py` | both apps (WebSocket) |

## Data model (`models/ride_hailing.py`, `models/user.py`)

26 tables. The important ones:

| Table | Meaning |
|---|---|
| `passengers`, `passenger_profiles` | A rider and their extra info. |
| `drivers`, `vehicles`, `driver_vehicle_assignments`, `driver_documents` | A driver, their car, which car they drive now, and their papers (status `pending/verified/rejected/expired`). |
| `ride_categories` | car / bike / auto. |
| `rides`, `ride_stops`, `ride_events` | A trip, its stops, and a log of what happened. |
| `ride_dispatch_offers` | One offer sent to one driver, with an expiry (30 s). |
| `fare_quotes`, `fare_line_items` | The price shown and its parts. |
| `payments` | **Table exists, but no code uses it** (no payment flow was found). |
| `ratings` | One rating per side per ride (unique key at line 241). |
| `driver_current_locations` | Last known GPS point of each driver. |
| `saved_places`, `location_catalog`, `service_areas` | Places and the allowed area. |
| `emergency_contacts`, `notifications`, `support_tickets`, `device_sessions` | Safety, messages, help, devices. |
| `outstation_bookings` | Long trips arranged by staff. |
| `audit_logs`, `outbox_events` | History of admin actions; planned event queue. |
| `admin_users` | Staff accounts with a `role` and `token_version`. |

The database itself blocks wrong values with **CHECK constraints** (rules on a column. *Example:* ride `status` must be in a fixed list, `ride_hailing.py:137`).

## Authentication and permissions

```
Phone app ──► Firebase SDK sends SMS ──► user types code ──► Firebase gives an ID token
Phone app ──► POST backend with ID token
Backend  ──► firebase_admin.verify_id_token() (services/*_auth_service.py)
Backend  ──► finds or creates the user ──► returns our own access + refresh JWT
```

- **Access token** lasts 15 minutes. **Refresh token** lasts 30 days (`core/config.py`). The refresh token gets a new access token without a new SMS.
- Driver and admin tokens carry an `actor` field (`driver` or `admin`) so one kind cannot be used as another (`driver_auth_service.py:198`, `admin_auth.py:22`). Passenger tokens have no `actor`.
- Admin tokens also carry `ver`. If it differs from `token_version` in the database, the token is rejected. This lets staff be logged out everywhere (`admin_auth.py:25`).
- Staff permissions come from `ROLE_PERMISSIONS` in the admin auth service.
- WebSocket auth uses the `Authorization` header (`routes/realtime.py:16`).

## Main flow: book and complete a ride

```
1 Passenger app  POST /passengers/me/ride-estimates   → BookingService.estimate()
2 Passenger app  POST /passengers/me/rides            → BookingService.book()  → Ride.status='searching'
3 BookingService → RideMatchingService.dispatch()
      picks nearest online active driver with a verified vehicle of the right category within 40 km
      creates RideDispatchOffer (30 s) → publish_driver_offer()
4 RealtimeHub    → WebSocket /realtime/drivers/me  → driver app shows the offer
5 Driver app     POST accept → status 'driver_assigned' → publish_passenger_status()
6 RealtimeHub    → WebSocket /realtime/passengers/rides/{id} → passenger sees driver
7 Driver steps:  driver_arriving → driver_arrived → in_progress (needs 4-digit start OTP) → completed
8 Both rate each other (one rating per side).
Timeout: if no accept in 30 s → expire_offer_and_publish() → next driver.
```

Files: `routes/booking.py`, `services/booking_service.py`, `ride_matching_service.py`, `ride_lifecycle_service.py`, `realtime_events.py`, `realtime_service.py`.

Fare rule (`booking_service.py:40-64`): base + km × rate (car 1500, auto 1200, bike 800 paise per km) + 20% at night (22:00–05:00 India time).

## Driver readiness flow

All four documents (`driving_licence`, `vehicle_registration`, `aadhaar`, `vehicle_insurance`) must be `verified` and the vehicle `verified`. Then `DriverReadinessService.reconcile()` sets the driver to `active` (`driver_readiness_service.py:14-36`). Only active drivers get offers.

## Outstation flow

Passenger requests (4 hours to 180 days ahead, trip 150 km or more, max 3 open requests) → staff confirm and estimate → staff choose a driver → driver is notified over WebSocket → staff mark complete. Statuses at `ride_hailing.py:304`.

## Realtime hub

`RealtimeHub` (`services/realtime_service.py`) keeps a dictionary of channel name → list of open WebSockets in memory. Channels: `passenger:{id}:ride:{id}` and `driver:{id}` (`realtime_events.py:11-16`). Offer expiry uses asyncio timers inside the same process. **Limit:** one process only. Two copies of the server would not see each other's connections. Redis publish/subscribe is the usual fix (`redis` is already a dependency).

## Apps

- Entry: `index.js` registers `App` (`AppRegistry.registerComponent`). `App.tsx` mounts the navigator.
- Passenger: `PassengerNavigator.tsx` shows login → `AuthenticatedShell()` → home, booking, rides, profile.
- Driver: `DriverNavigator.tsx` shows login, registration, document upload, dashboard.
- Both apps keep code by **feature** folder: `src/features/<name>/{screens,data,services,domain}`. `data/` holds API calls (for example `bookingApi.ts`); `services/` holds WebSocket clients.
- Each app has its own `apiClient.ts` (axios) that adds the token and refreshes it.

Next: `03-setup-and-run.md`
