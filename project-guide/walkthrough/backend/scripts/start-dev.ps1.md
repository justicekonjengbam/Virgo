# backend/scripts/start-dev.ps1

## 1. Purpose
Starts the FastAPI backend in development mode on Windows. It checks that the virtual environment exists, moves into `backend/`, and runs the Uvicorn server for `app.main:app` (`backend/app/main.py`). Not directly runnable on Linux.

## 2. Imports, one by one
No imports.

## 3. Walk through the code, top to bottom
Line 1: `$backendRoot = Resolve-Path (Join-Path $PSScriptRoot '..')` (`backend/scripts/start-dev.ps1:1`). The script folder plus `..` gives the `backend` folder as an absolute path.

Line 2: `$python = Join-Path $backendRoot '.venv\Scripts\python.exe'` (`:2`). Builds the path of the venv Python (no run yet).

Lines 4-6: (`:4-6`)
```powershell
if (-not (Test-Path $python)) { throw '...' }
```
- `Test-Path` returns true if the path exists. `-not` flips it. `throw` stops the script with that message.
- The message tells the user how to create the venv and install: `python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e .[dev]`.

Line 8: `Set-Location $backendRoot` (`:8`) is `cd`. This matters because Uvicorn imports `app.main` relative to the current folder.

Line 9: `& $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` (`:9`)
- `-m uvicorn` runs the Uvicorn server module.
- `app.main:app` means: in file `app/main.py`, use the variable named `app` (the FastAPI object).
- `--reload` restarts the server when code files change (dev only).
- `--host 0.0.0.0` listens on all network cards, so a phone on the same Wi-Fi can reach it. The default `127.0.0.1` would only allow this computer.
- `--port 8000` is the door number. Open `http://localhost:8000/docs` for the FastAPI docs page.
- Output example: `INFO: Uvicorn running on http://0.0.0.0:8000`.

## 4. How data flows
```
start-dev.ps1 -> check venv -> cd backend -> uvicorn -> imports app/main.py -> serves HTTP :8000
phone/app --HTTP--> Wi-Fi --> your PC:8000 --> FastAPI route
```

## 5. Try it
Not directly runnable on Linux. Equivalent in zsh:
```zsh
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Can it be better?
- Good: friendly error when the venv is missing; works from any folder.
- Weak: the host `0.0.0.0` exposes the dev server to the whole local network. Port and host are fixed. Windows-only paths.
- Cleaner way (opinion): accept parameters: `param($Port = 8000)`.
- Security: `0.0.0.0` plus `--reload` is for development only. Never use it for production.

## 7. Check yourself
1. What does `app.main:app` point to?
2. Why does the script `Set-Location` before starting Uvicorn?
