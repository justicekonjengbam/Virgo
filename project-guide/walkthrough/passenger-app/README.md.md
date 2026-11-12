# passenger-app/README.md

## 1. Purpose
The README is the human guide for the Passenger app: what it does, how to install it and how to run it. People and GitHub read it. No code calls it.

## 2. Imports, one by one
Markdown has no imports. It has links to folders and code blocks only.

## 3. Walk through the code, top to bottom
- Intro (`passenger-app/README.md:3-5`): the app is a React Native client for CabSure, a ride-booking platform for Tier 2 and Tier 3 cities (smaller Indian cities). Features listed: Firebase phone login, passenger home, saved addresses, emergency contacts, support content, static ride selection, fare estimates, ride requests, recent ride history.
- `## Stack` (lines 7-14): React Native + TypeScript, React Navigation native stack, Firebase Phone Authentication (login with an SMS code), Axios (HTTP client), FastAPI backend with PostgreSQL-ready SQLAlchemy models, Poppins fonts.
- `## Prerequisites` (lines 16-22): Node.js LTS, pnpm 11, Android Studio with an emulator, a running backend, Firebase Android configuration (the `google-services.json` file; the build file applies the `google-services` plugin at `android/app/build.gradle:4`).
- `## Install` (lines 24-38):
  - `pnpm install` from the repo root downloads all libraries.
  - `copy passenger-app\.env.example passenger-app\.env` is a Windows CMD command. On Arch/zsh use `cp passenger-app/.env.example passenger-app/.env`.
  - Emulator backend host is `http://10.0.2.2:8000` (see `.env.example`).
- `## Run on Android` (lines 40-54): terminal 1: `pnpm start --port 8081 --reset-cache` starts Metro on port 8081 and clears the cache. Terminal 2: `pnpm android --port 8081` builds and installs the app. `cd /d C:\path\to\cabApp\passenger-app` is CMD for "change drive and folder"; on zsh use `cd passenger-app`.
- `## Quality checks` (lines 56-61): `pnpm --filter passenger-app typecheck` and `... lint`. The `--filter` flag picks the package.
- `## Project structure` (lines 63-69): `src/components`, `src/features`, `src/navigation`, `src/services`, `src/theme`.
- `## Important notes` (lines 71-73): Firebase test phone numbers work without SMS. Do not commit `.env`, Firebase secrets, local databases, Gradle caches or build output.

## 4. How data flows
```
reader -> README -> pnpm install -> copy .env -> pnpm start (Metro) -> pnpm android (build+install) -> app calls backend
```

## 5. Try it
```zsh
pnpm install
cp passenger-app/.env.example passenger-app/.env
pnpm --filter passenger-app typecheck
```
Install libraries, make your env file, run the type check. Expect no errors from the last command.

## 6. Can it be better?
- Good: short and ordered. It states the notes about secrets.
- Weak: all commands are Windows CMD, but the reader is on Arch Linux. It does not mention the backend start command, Firebase `google-services.json` placement, or `pnpm test`. The "Run on Android" paths use a placeholder.
- Cleaner way: add a zsh block next to each CMD block, and a link to the backend README.
- Security: it correctly warns not to commit secrets.

## 7. Check yourself
1. Which two terminals do you need to run the app, and what runs in each?
2. What is the zsh version of the `copy` command?
