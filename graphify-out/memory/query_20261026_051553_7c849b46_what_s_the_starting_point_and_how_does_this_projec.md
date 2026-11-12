---
type: "query"
date: "2026-10-26T05:15:53.261250+00:00"
question: "what's the starting point and how does this project works and how they are connected to each other?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["main.py", "router.py", "RealtimeHub", "RideMatchingService", "BookingService", "PassengerNavigator.tsx", "App()"]
---

# Q: what's the starting point and how does this project works and how they are connected to each other?

## Answer

Expanded from original query via vocab: [main, app, create, navigator, router, backend, fastapi, realtime, hub, ride, matching, booking]. Backend entry is backend/app/main.py (create_app) which includes api/v1/router.py and imports realtime_service.RealtimeHub. Mobile entries are App() in passenger-app/driver-app, which mount PassengerNavigator/DriverNavigator. Core backend flow: routes/booking.py -> BookingService -> RideMatchingService -> RideLifecycleService, with realtime_events publishing via RealtimeHub. Apps and backend have no graph edges: they connect only at runtime via HTTP and WebSocket (bookingApi.ts, passengerRealtimeService.ts).

## Outcome

- Signal: useful

## Source Nodes

- main.py
- router.py
- RealtimeHub
- RideMatchingService
- BookingService
- PassengerNavigator.tsx
- App()