# Virgo Passenger App – Happy Cabbing

The Passenger app is the React Native client for Virgo, a modern ride-booking platform designed for convenient, accessible mobility across Imphal and regional cities.

It currently supports Firebase phone authentication, a responsive passenger home, saved addresses, emergency contacts, support content, static ride selection, fare estimates, ride requests, and recent ride history.

## Stack

- React Native and TypeScript
- React Navigation native stack
- Firebase Phone Authentication
- Axios API client
- FastAPI backend with PostgreSQL-ready SQLAlchemy models
- Poppins-based design system

## Prerequisites

- Node.js LTS
- pnpm 11
- Android Studio with an emulator
- A running Virgo backend
- Firebase Android configuration for phone authentication

## Install

From the repository root:

```cmd
pnpm install
```

Copy the Passenger environment example and set the backend URL appropriate for your Android emulator:

```cmd
copy passenger-app\.env.example passenger-app\.env
```

For the standard Android emulator, the backend host is normally `http://10.0.2.2:8000`.

## Run on Android

Start Metro:

```cmd
cd /d C:\path\to\cabApp\passenger-app
pnpm start --port 8081 --reset-cache
```

In another CMD window, build and install the Android app:

```cmd
cd /d C:\path\to\cabApp\passenger-app
pnpm android --port 8081
```

## Quality checks

```cmd
pnpm --filter passenger-app typecheck
pnpm --filter passenger-app lint
```

## Project structure

- `src/components` — shared design-system and navigation components
- `src/features` — feature-owned screens, API clients, state, and domain types
- `src/navigation` — typed route definitions and the Passenger navigation stack
- `src/services` — cross-feature HTTP client and infrastructure code
- `src/theme` — colors, typography, spacing, elevation, and shadows

## Important notes

Firebase test phone numbers work without SMS. Real SMS authentication requires a Firebase project configured for production use. Do not commit `.env`, Firebase secrets, local databases, Gradle caches, or generated build output.
