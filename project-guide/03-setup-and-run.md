# 03. Setup and run (Arch Linux, zsh)

Do these steps by hand once. After that you will know what every piece needs.

## 1. Install tools

```bash
sudo pacman -S --needed git python nodejs pnpm jdk17-openjdk android-tools
```

- `sudo`: run as administrator.
- `pacman`: the Arch package manager. `-S` means "install". `--needed` skips what you already have.
- `python`: the language for the backend (need 3.12 or newer). `nodejs` + `pnpm`: for the phone apps. `jdk17-openjdk`: Java, needed by Android builds. `android-tools`: gives `adb`, a program that talks to a phone or emulator.

Your machine already gets Node, Python and pnpm from `mise`, so you can skip those. Check:

```bash
python --version   # expect Python 3.12.x or newer
node --version     # React Native 0.86 needs a recent Node; the repo does not pin one (no "engines" field)
pnpm --version
```

For the Android emulator, install Android Studio and create a virtual phone. This is a big download and cannot be done in one command.

## 2. Backend

All commands run in `backend/`.

```bash
cd backend
uv venv .venv
source .venv/bin/activate
uv pip install -e '.[dev]'
```

- `uv`: a fast Python tool. `uv venv .venv` makes a **virtual environment** (a private folder of Python packages for this project only. *Example:* a toolbox that belongs to one job).
- `source .venv/bin/activate`: switches your shell to use that toolbox. Your prompt gets `(.venv)`.
- `uv pip install -e '.[dev]'`: installs the project. `-e` means "editable" (code changes apply without reinstalling). `'.[dev]'` means "this folder, plus the `dev` extras" (pytest, ruff). Quotes stop zsh from treating `[` as a pattern.

### Environment file

The backend reads `backend/.env` only (see `core/config.py`). Copy the example and fill it.

```bash
cp ../.env.example .env
```

Variables (names only; see `.env.example` for placeholders):

| Name | Meaning |
|---|---|
| `ENVIRONMENT` | `development` or `production`. |
| `DATABASE_URL` | Where data lives. Dev default is a local SQLite file. |
| `AUTO_MIGRATE` | If `true`, the app updates the database layout at startup. |
| `JWT_SECRET_KEY` | Secret that signs login tokens. Use a long random value (`openssl rand -hex 32`). |
| `FIREBASE_CREDENTIALS_PATH` | Path to the Firebase service-account JSON file. Keep it out of Git. |
| `ADMIN_BOOTSTRAP_EMAIL/PASSWORD/NAME/ROLE` | Makes the first admin account on startup. |
| `GEOAPIFY_API_KEY` | Key for map search and routing. |
| `MAPS_CONTACT_EMAIL` | Contact sent to map services. |

### Start

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- `uvicorn`: the server program.
- `app.main:app`: "in the file `app/main.py`, use the variable named `app`" (it is created at `backend/app/main.py:40`).
- `--reload`: restart when you save a file. Dev only.
- `--host 0.0.0.0`: accept connections from other machines, so the emulator can reach it. `127.0.0.1` would block the emulator.
- `--port 8000`: the door number.

Expected output ends with `Uvicorn running on http://0.0.0.0:8000`.

Check it:

```bash
curl http://127.0.0.1:8000/health
```

- `curl`: sends a web request from the terminal.
- The health route is mounted at the top level, not under `/api/v1` (`backend/app/main.py:32`). Expect a small JSON reply.
- Open `http://127.0.0.1:8000/docs` too. FastAPI builds this page for you. It lists every route and lets you try them. All other routes start with `/api/v1` (`main.py:33`).

The admin site is at `http://127.0.0.1:8000/admin`.

### Tests and lint

```bash
pytest          # runs tests in backend/tests (config at pyproject.toml:32-35)
ruff check .    # finds mistakes
ruff format .   # formats code
```

## 3. Phone apps

From the repo root:

```bash
pnpm install
cp passenger-app/.env.example passenger-app/.env
cp driver-app/.env.example driver-app/.env
```

Open both `.env` files and set the API address. The Android emulator sees your computer as `10.0.2.2`, so use `http://10.0.2.2:8000`. **Warning:** the driver app expects the value to end in `/api/v1`, the passenger app expects it without (see `05-improvements.md`).

Firebase also needs `google-services.json` in each `android/app/` folder. It is not in the repo. Download it from your Firebase console.

Start one app (two terminals if you run both):

```bash
cd passenger-app
pnpm start                 # starts Metro on port 8081
pnpm exec react-native run-android --port 8081 --no-packager
```

- `pnpm start`: runs Metro, the program that bundles JavaScript for the phone.
- `run-android`: builds the Android app and installs it on the emulator.
- `--no-packager`: do not start a second Metro, because you started one.

The `pnpm android` script in `package.json` will fail on Linux because it uses Windows `set "GRADLE_USER_HOME=C:\tmp..."`. Use the command above.

Driver app: same steps in `driver-app/` with port 8082 (`pnpm start --port 8082`, then `--port 8082` in the run command).

Checks:

```bash
pnpm typecheck   # tsc --noEmit: checks types, writes nothing
pnpm lint        # eslint
pnpm test        # jest (no tests exist yet)
```

## 4. Common problems

| Problem | Likely cause | Fix |
|---|---|---|
| App cannot reach backend | Server bound to `127.0.0.1`, or wrong URL | Use `--host 0.0.0.0` and `10.0.2.2` in the emulator. |
| `cleartext HTTP not permitted` | Real devices on newer Android | Both manifests allow cleartext now (`AndroidManifest.xml:14`). Remove it in production. |
| Phone login fails | Missing `google-services.json`, or SHA-1 key not added in Firebase | Add both in the Firebase console. |
| Backend crashes at start | `FIREBASE_CREDENTIALS_PATH` wrong, or migration error | Read the first traceback line. Check `backend/.env`. |
| `no matches found` in zsh | Unquoted `[` or `*` | Put quotes around it. |

Next: `04-status.md`
