# 00. Start here

Virgo (formerly CabSure) is a ride-booking system ("VIRGO – Happy Cabbing"), like a regional Uber or Ola tailored for Imphal, Manipur and regional cities. A passenger books a ride, a nearby driver accepts it, and both see the trip live.

## What the project is

The repo is a **monorepo** (one Git repository that holds several programs. *Example:* one folder with the backend and two phone apps inside it).

It has four programs:

| Folder | What it is | Who uses it |
|---|---|---|
| `backend/` | The server. It is written in Python with FastAPI. It stores data and applies the rules. | The three apps below talk to it. |
| `passenger-app/` | An Android and iOS phone app, written in React Native. | Passengers. |
| `driver-app/` | A second phone app, also React Native. | Drivers. |
| `admin-app/` | A small website made of plain HTML and JavaScript. The backend serves it at `/admin`. | Virgo operations staff. |

Other folders: `docs/` (a few notes), `project-guide/` (this guide), `graphify-out/` (a map of the code made by another tool).

## The goal

The owner says the service is for **Imphal, Manipur, India**.

**Warning: the code does not match this yet.** Nothing in the repo mentions Imphal or Manipur. The code is hard-coded for a demo area around Dharwad–Hubballi in Karnataka. A comment in `backend/app/services/ride_matching_service.py:30` calls it a "demo dispatch region". The places that must change are listed in `05-improvements.md` (item 17).

The service area is a 150 km circle around one fixed point (`backend/app/services/map_provider_service.py:14`). Today that point is Dharwad–Hubballi, not Imphal.

The finished product should let a passenger:
1. Sign up with a phone number and a one-time code.
2. Pick a pickup and a destination on a map.
3. See a price before booking.
4. Book, wait for a driver, watch the driver come, ride, and rate.

It should let a driver:
1. Register with a vehicle and documents.
2. Wait for staff to approve them.
3. Go online, receive ride offers, and accept them.
4. Run the trip and complete it.

It should let staff:
1. Review driver documents.
2. Handle support tickets.
3. Manually arrange long **outstation** trips (trips of 150 km or more, planned days ahead).

## How the parts talk

```
 passenger-app ──HTTP + WebSocket──┐
 driver-app    ──HTTP + WebSocket──┼──►  backend (FastAPI)  ──►  database (SQLite now)
 admin-app     ──HTTP──────────────┘            │
                                                ├──► Firebase  (checks phone-login proof)
                                                └──► Geoapify  (map search, routes, address lookup)
```

**HTTP** (the normal web request. *Example:* the app asks "give me the fare" and gets one answer back). **WebSocket** (a connection that stays open so the server can push news at any time. *Example:* "your driver is 2 minutes away" arrives without the app asking).

Full detail is in `02-architecture.md`.

## How to read this guide

Read in this order. Each file ends with a "Next" link.

1. `00-start-here.md` (this file).
2. `01-tech-stack.md`: every tool and library, and why it is used.
3. `02-architecture.md`: how the pieces fit, data tables, main flows.
4. `03-setup-and-run.md`: install and start everything by hand.
5. `04-status.md`: what is done and what is not.
6. `05-improvements.md`: what to fix or build next.
7. `06-security.md`: risks and good practice.
8. `07-reading-order.md`: the list of source files in the order to read them. Each has a page in `walkthrough/`.

## The three things to know first

1. **Money is stored as integers in paise.** 100 paise = 1 rupee. This avoids rounding errors that decimals cause.
2. **A ride moves through fixed statuses.** `searching` → `driver_assigned` → `driver_arriving` → `driver_arrived` → `in_progress` → `completed` (or `cancelled`). The database enforces the list (`backend/app/models/ride_hailing.py:137`).
3. **Real-time updates live inside one server process.** If you run two backend copies, live updates will break. See `05-improvements.md`.

Next: `01-tech-stack.md`
