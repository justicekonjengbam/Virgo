# 01. Tech stack

A **library** is code written by other people that you add to your project. *Example:* instead of writing your own way to send web requests, you use the `axios` library. A **framework** is a bigger library that sets the shape of your whole program. *Example:* FastAPI decides how you write web routes.

Versions come from `backend/pyproject.toml`, `passenger-app/package.json` and `driver-app/package.json`. "Used in N files" was counted by searching the source with `rg`.

## Languages

| Language | Where | Why |
|---|---|---|
| Python 3.12+ | `backend/` | Easy to read, strong web and database libraries. `pyproject.toml:6` demands 3.12 or newer. |
| TypeScript | both phone apps | **TypeScript** (JavaScript with types. *Example:* you say `price: number`, and the editor warns if you pass text). It catches mistakes before the app runs. |
| JavaScript | `admin-app/` | No build step. The browser runs it directly. |
| Kotlin / Swift | `android/`, `ios/` folders | Small native entry files that React Native generates. You rarely edit them. |
| SQL | migrations | The language of databases. |

## Backend (Python)

**Python package** list in `backend/pyproject.toml:9-20`:

| Package | What it is | Why CabSure uses it | Used in |
|---|---|---|---|
| `fastapi` | Web framework. It turns Python functions into web routes and checks input automatically. | The whole API. | `main.py`, all of `api/v1/routes/` |
| `uvicorn[standard]` | A server program that runs a FastAPI app. *Example:* FastAPI is the recipe, uvicorn is the cook. | Starts the server. | start command only |
| `pydantic-settings` | Reads settings from environment variables and `.env`, with types. | `core/config.py` | 1 file |
| `sqlalchemy` (2.x) | An **ORM** (Object-Relational Mapper: lets you use Python classes instead of writing SQL. *Example:* `db.get(Driver, 5)` instead of `SELECT * FROM drivers WHERE id=5`). | All database access. | models, services, repositories |
| `alembic` | Database **migrations** (versioned scripts that change the table layout step by step. *Example:* "add column `document_number`"). | 12 migration files. | `database/migrations/` |
| `psycopg[binary]` | Driver to talk to PostgreSQL. | Planned for production. **Not imported anywhere.** | 0 files |
| `redis` | Client for the Redis in-memory store. | Planned (probably for shared real-time). **Not imported anywhere.** | 0 files |
| `firebase-admin` | Google's server library. | Verifies the phone-login proof from the apps. | `firebase_service.py`, 2 auth services |
| `httpx` | A modern HTTP client. | Calls the Geoapify map API. | `map_provider_service.py` |
| `python-multipart` | Lets FastAPI read form and file uploads. | No upload endpoint exists yet. **Not imported.** | 0 files |
| `PyJWT` | Creates and checks **JWTs** (JSON Web Tokens: signed text that proves who you are. *Example:* a tamper-proof wristband). | Login tokens. | 8 files |
| `pwdlib[argon2]` | Password hashing with the **Argon2** algorithm (a slow, safe way to scramble secrets). | Hashes passwords and OTP codes. | 2 files |

Dev tools (`pyproject.toml:23`): `pytest` (runs tests), `pytest-asyncio` (tests for async code), `ruff` (checks style and mistakes; line length 100 at `pyproject.toml:29`).

**Database.** SQLite in development (one file, no setup). PostgreSQL is planned for production (see `.env.example`). Rule of thumb: SQLAlchemy lets you swap the two.

## Phone apps (TypeScript)

Both apps share almost the same dependency list.

| Library | What it is | Why | Used in (passenger / driver) |
|---|---|---|---|
| `react` 19 | UI library. You describe screens as functions that return pieces of UI. | Base of everything. | all |
| `react-native` 0.86 | Builds real Android and iOS apps from React code. | Cross-platform apps. | all |
| `@react-navigation/native`, `native-stack`, `bottom-tabs` | Screen switching. A **stack** is screens piled on top of each other (back button removes the top one). **Tabs** are the bottom bar. | Navigation. | navigators |
| `react-native-screens`, `react-native-safe-area-context`, `react-native-gesture-handler`, `@react-native-masked-view/masked-view` | Helpers that React Navigation needs (fast native screens, notch-safe areas, touch handling). | Required peers. | indirect |
| `axios` | HTTP client with interceptors (code that runs on every request). | Calls the backend. | 1 / 3 files |
| `@react-native-firebase/app`, `auth` | Phone-number login with SMS code. | Login. | few files |
| `@react-native-async-storage/async-storage` | Small key-value storage on the phone. | Saves tokens and the session. | 3 / 3 files |
| `@maplibre/maplibre-react-native` | Draws maps using open **MapLibre** and Geoapify tiles (map pictures). | Maps. | 2 / 3 files |
| `react-native-vector-icons` | Icon fonts. | Icons. | 22 / 15 files |
| `react-native-svg` | Draws SVG vector images. | Logos. | 1 / 1 files |
| `react-native-config` | Reads `.env` values into the app at build time. | `API_BASE_URL` etc. | 2 / 2 files |
| `@react-native-documents/picker` | Lets the user choose a file. | Driver documents. | driver only, 1 file |
| `react-native-maps` | Another map library (Google/Apple maps). | **Not imported anywhere.** Duplicate of MapLibre. | 0 / 0 |
| `@reduxjs/toolkit`, `react-redux` | **Redux** (one shared store of app data). | **Not imported anywhere.** State is handled with React's own tools. | 0 / 0 |
| `react-hook-form` | Form helper. | **Not imported anywhere.** | 0 / 0 |
| `@react-native-community/netinfo` | Detects online/offline. | **Not imported anywhere.** | 0 / 0 |

Dev tools: `typescript`, `eslint` + `typescript-eslint` + `eslint-plugin-react(-hooks)` (find mistakes), `prettier` (formats code), `jest` + `react-test-renderer` (tests; **no test files exist**), `@react-native/*` (Metro bundler, Babel preset, Gradle plugin; **Metro** packs your JS files into one file for the phone).

**Package manager:** pnpm with a **workspace** (one install shared by several folders; `pnpm-workspace.yaml:1-3` lists `passenger-app` and `driver-app`).

## Admin site

Plain HTML, CSS and JavaScript in `admin-app/`. No framework. It calls the backend with `fetch` (the browser's built-in request function) and stores the token in `sessionStorage` (browser memory that clears when the tab closes).

## External services

| Service | Role | Where |
|---|---|---|
| Firebase Authentication | Sends the SMS code and proves the phone number. | apps + `firebase_service.py` |
| Geoapify | Address search, reverse lookup (point → address), routing, map tiles. | `map_provider_service.py` |

## Infrastructure and tooling

- **Alembic** auto-runs on startup (`db.py:33`, setting `AUTO_MIGRATE=true`).
- **PowerShell scripts** (`backend/scripts/*.ps1`) and Windows-style npm scripts (`set "GRADLE_USER_HOME=C:\tmp..."`) mean the author used Windows. On Arch Linux you run the plain commands instead (see `03-setup-and-run.md`).
- No Docker, no CI, no deployment files were found.

## Recommendations on tech choices

1. **Keep** FastAPI, SQLAlchemy 2, Alembic, Pydantic. Good, current, popular.
2. **Remove or use** the unused packages: `redis`, `psycopg`, `python-multipart` (backend); `react-native-maps`, `@reduxjs/toolkit`, `react-redux`, `react-hook-form`, `netinfo` (apps). Unused code adds weight and attack surface.
3. **Choose one map library.** MapLibre is the one actually used.
4. **For production:** PostgreSQL (with PostGIS for "nearest driver" queries) and Redis (shared real-time messages). Both are already hinted by the dependencies.
5. **Add** a rate limiter (for example `slowapi`) and a payments provider (for example Razorpay for India) when you build those features.

Next: `02-architecture.md`
