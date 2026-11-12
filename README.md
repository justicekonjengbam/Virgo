# VIRGO – Happy Cabbing

Virgo is a modern full-stack ride-booking platform designed for convenient, accessible mobility across Imphal and regional cities. The repository contains separate Passenger and Driver Android applications, a FastAPI backend, and an operations Admin console.

> **VIRGO – Happy Cabbing**  
> *Imphal is changing. Change the way you travel in the city.*

## Applications

- **Passenger app** — Firebase phone authentication, location selection, fare estimates, local and outstation booking, live ride status, saved places, emergency contacts, notifications, support, and profile settings.
- **Driver app** — two-step onboarding, document review status, availability, live ride offers, ride lifecycle management, trip history, earnings, outstation schedules, and profile settings.
- **Admin console** — administrator authentication, Driver and document review, vehicle status, support operations, and outstation assignment management.
- **Backend** — FastAPI, SQLAlchemy, Alembic migrations, Firebase token verification, ride matching, WebSocket updates, fare calculation, and repository/service/API layering.

## Technology

- React Native 0.86 and TypeScript
- React Navigation, Axios, Firebase Authentication, and MapLibre
- FastAPI, SQLAlchemy, Alembic, Pydantic, and SQLite for local development
- pnpm workspaces
- Poppins typography and shared Virgo purple brand design language (`#952B7D`)

## Local setup

Install JavaScript dependencies from the repository root:

```cmd
pnpm install
```

Create local environment files from the committed examples:

```cmd
copy passenger-app\.env.example passenger-app\.env
copy driver-app\.env.example driver-app\.env
copy backend\.env.example backend\.env
```

Create the backend virtual environment and install dependencies:

```cmd
cd /d C:\path\to\cabApp\backend
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the backend:

```cmd
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Start Passenger Metro on port 8081 or Driver Metro on port 8082 from the corresponding application directory.

## Quality checks

```cmd
pnpm --filter passenger-app typecheck
pnpm --filter driver-app typecheck
cd backend
.venv\Scripts\python.exe -m pytest -q
```

## Security

Local `.env` files, databases, Python environments, dependency folders, signing keys, service-account credentials, APKs, logs, and build outputs are intentionally excluded from version control. Firebase Android client configuration files contain application identifiers but no private service-account keys.

Detailed API, architecture, database, and Driver foundation notes are available in the `docs`, `documentation`, and `api-docs` directories.
