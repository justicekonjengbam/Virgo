# VIRGO Development Tools & Service Manager

Centralized PowerShell development environment management for VIRGO.

## Services Managed

| Service | Port | Health Endpoint | Working Directory | Console Title |
|---|---:|---|---|---|
| **FastAPI Backend** | 8000 | `http://127.0.0.1:8000/health` | `backend` | VIRGO - Backend (Port 8000) |
| **Passenger Metro** | 8081 | `http://127.0.0.1:8081/status` | `passenger-app` | VIRGO - Passenger Metro (Port 8081) |
| **Driver Metro** | 8082 | `http://127.0.0.1:8082/status` | `driver-app` | VIRGO - Driver Metro (Port 8082) |

---

## Daily Workflow

Open PowerShell and navigate to `dev-tools`:

```powershell
cd "C:\Users\JUSTICE\Documents\Projects\CabSure-Ride-Booking-Application-main\dev-tools"
```

### 1. Start VIRGO (One Command)
Starts all missing services in their own visible console windows, verifies health endpoints, and configures ADB reverse port forwarding for the connected Samsung tablet:

```powershell
.\start-virgo.ps1
```

*Note: If any service is already running and healthy, `start-virgo.ps1` preserves it and does not create duplicate processes.*

### 2. Check System Status & Health
Displays real-time status of all services, process IDs, HTTP health check responses, log file sizes, and Samsung tablet ADB reverse mappings:

```powershell
.\status-virgo.ps1
```

### 3. Restart an Individual Service
Restarts a single service without disturbing other running services:

```powershell
.\restart-virgo-service.ps1 -Service Driver
.\restart-virgo-service.ps1 -Service Passenger
.\restart-virgo-service.ps1 -Service Backend
```

### 4. Stop Managed Services
Safely terminates managed service windows and process trees while protecting external/unmanaged processes:

```powershell
.\stop-virgo.ps1
```
*(Or stop a single service: `.\stop-virgo.ps1 -Service Driver`)*

---

## Directory Structure

```
dev-tools/
├── scripts/
│   └── virgo-common.ps1          # Shared configurations, health checks, ADB, process helpers
├── logs/
│   ├── backend.log               # Backend output log (rotated at 5 MB)
│   ├── passenger-metro.log       # Passenger Metro bundler log
│   ├── driver-metro.log          # Driver Metro bundler log
│   └── launcher.log              # Manager operational log
├── pids/                         # Process tracking metadata
├── start-virgo.ps1               # Central startup script
├── status-virgo.ps1              # Health & diagnostics dashboard
├── restart-virgo-service.ps1     # Targeted single-service restarter
└── stop-virgo.ps1                # Safe process termination
```

