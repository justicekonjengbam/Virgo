# README.md (repo root)

## 1. Purpose
The front page of the project. It says what CabSure is, which parts exist, how to start it, and how to run checks. It is documentation only; no code reads it.

## 2. Imports, one by one
None. It is Markdown (text with simple marks like `#` for titles).

## 3. Walk through the content (`README.md` line numbers)
- Intro (`README.md:1-3`): CabSure is a ride-booking platform for Tier 2 and Tier 3 cities (smaller Indian cities). It has Passenger and Driver Android apps, a FastAPI backend and an Admin console.
- Applications (`:5-10`): what each part does. Passenger: Firebase phone login, fare estimate, booking. Driver: onboarding, availability, ride offers, earnings. Admin: reviews drivers and documents. Backend: FastAPI, SQLAlchemy, Alembic, WebSocket, fare logic.
- Technology (`:12-18`): React Native 0.86, TypeScript, React Navigation, Axios, Firebase Auth, MapLibre, FastAPI, SQLite for local work, pnpm workspaces, Poppins font.
- Local setup (`:20-50`): `pnpm install` at the root installs all JS packages. Copy three `.env.example` files to `.env` (`copy` is a Windows command). Make a Python virtual environment (`py -m venv .venv`, an isolated folder of Python packages), install `requirements.txt`, then start the server with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`. `uvicorn` is the program that serves the FastAPI app; `--host 0.0.0.0` lets phones on your network connect; `--port 8000` is the port number.
- Metro ports (`:50`): Passenger on 8081, Driver on 8082. **Metro** is the React Native JS bundler.
- Quality checks (`:52-59`): `pnpm --filter <app> typecheck` runs TypeScript checks for one workspace package; `pytest -q` runs backend tests quietly.
- Security (`:61-65`): `.env`, databases, keys, APKs and logs are not committed. It also points to folders `docs`, `documentation`, `api-docs`.

## 4. How data flows
```
Reader -> README -> pnpm install -> copy .env -> start backend -> start Metro -> run app
```

## 5. Try it on Arch/zsh
The README uses Windows commands. On Arch use:
```
pnpm install
cp passenger-app/.env.example passenger-app/.env
cp driver-app/.env.example driver-app/.env
cp backend/.env.example backend/.env
cd backend && uv venv && uv pip install -r requirements.txt
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
`cp` copies a file; `uv venv` makes `.venv`; `uv run` runs a command inside it. Expected: "Uvicorn running on http://0.0.0.0:8000". (Not run by me.)

## 6. Can it be better?
- Good: clear parts list, security note.
- Weak: Windows-only commands and a made-up path `C:\path\to\cabApp`; no Linux/macOS steps; no mention of the Firebase setup details; the three doc folders may not all exist (check with `fd -t d 'docs|documentation|api-docs' -d 1`).
- Cleaner: add a Linux section and a table of ports.
- Security: good; it says no secrets are committed.

## 7. Check yourself
1. Which ports do Passenger and Driver Metro use?
2. What does `--host 0.0.0.0` change?
