# `backend/app/main.py`

## 1. Purpose
This is the entry point of the backend. It builds the FastAPI application: it runs migrations, creates the first admin, attaches all routes, and serves the admin web page. The server command points at the `app` object made on the last line. It calls `db.py`, `admin_auth_service.py`, `realtime_service.py` and the router in `api/v1/router.py`.

## 2. Imports, one by one
Standard library:
- `from contextlib import asynccontextmanager` (`main.py:1`). **Async context manager** (code that runs setup before a block and cleanup after it, in async code). The decorator turns a function with one `yield` into such a manager. *Example:* code before `yield` runs at start, code after runs at stop. Used for `lifespan`.
- `from pathlib import Path` (`main.py:2`). File paths as objects. *Example:* `Path('a') / 'b'`.

Third party:
- `from fastapi import FastAPI` (`main.py:4`). **FastAPI** is a web framework (it receives HTTP requests and calls your Python functions). `FastAPI(...)` is the application object. *Example:* `app = FastAPI()`.
- `from fastapi.staticfiles import StaticFiles` (`main.py:5`). Serves files from a folder (HTML, JS, CSS). *Example:* mount a folder `public` so `/public/a.png` returns the file.

Project:
- `import app.models  # noqa: F401` (`main.py:7`). Loads the models package (`backend/app/models/__init__.py`) so all table classes register with SQLAlchemy. The name is not used afterwards, so `# noqa: F401` tells the linter "unused import is on purpose".
- `from app.api.v1.router import api_router` (`main.py:8`), from `api/v1/router.py`. A bundle of all v1 routes.
- `from app.api.v1.routes.health import router as health_router` (`main.py:9`), from `api/v1/routes/health.py`. The health-check route; `as` renames it.
- `from app.core.config import get_settings` (`main.py:10`), from `core/config.py`.
- `from app.db import SessionLocal, initialize_database` (`main.py:11`), from `db.py`.
- `from app.services.admin_auth_service import AdminAuthService` (`main.py:12`). Admin login logic; here its `bootstrap` creates the first admin.
- `from app.services.realtime_service import realtime_hub` (`main.py:13`). The shared object that pushes live updates (for example WebSocket messages) to apps.

## 3. Walk through the code, top to bottom

**`@asynccontextmanager async def lifespan(_: FastAPI)`** (`main.py:16-19`)
- **Lifespan** (a function FastAPI runs when the server starts and stops). `async def` means an **async** function (it can pause while waiting, so one thread serves many users). The `_` parameter is the app, unused.
- Line 18: `realtime_hub.bind_running_loop()` tells the hub which **event loop** (the async engine running the server) is active, so other threads can later send live messages into it.
- Line 19: `yield` marks "server is running now". Nothing is done at shutdown.

**`def create_app() -> FastAPI`** (`main.py:22-37`)
- Line 23: read settings.
- Line 24: `initialize_database()` runs Alembic migrations (see `db.py:31`).
- Lines 25-29: open a session, call `AdminAuthService().bootstrap(db)` (creates the first admin from the `ADMIN_BOOTSTRAP_*` settings if set), and always close the session in `finally`.
- Line 30: `FastAPI(title=..., lifespan=lifespan)` builds the app and attaches the lifespan.
- Line 32: `include_router(health_router, tags=["health"])` adds the health route at its own path. **Router** (a group of routes). **Tags** group routes in the auto docs page.
- Line 33: `include_router(api_router, prefix=settings.api_v1_prefix)` adds all other routes under `/api/v1`. *Example:* a route `/auth/login` becomes `/api/v1/auth/login`.
- Line 34: `Path(__file__).resolve().parents[2] / "admin-app"` is the repo's `admin-app` folder (`main.py` is in `backend/app`; `parents[2]` is the repo root).
- Lines 35-36: if that folder exists, `app.mount("/admin", StaticFiles(directory=..., html=True), name="admin-app")` serves it at `/admin`. `html=True` makes `/admin/` return `index.html`.
- Line 37: return the app.

**`app = create_app()`** (`main.py:40`)
Runs everything at import time. A server such as uvicorn imports `app.main:app` and uses this object.

## 4. How data flows
```
uvicorn app.main:app
   -> import main.py -> create_app()
        -> initialize_database()  --> Alembic --> database file/server
        -> AdminAuthService().bootstrap(db) --> first admin row
        -> include routers, mount /admin
   -> server starts -> lifespan: realtime_hub.bind_running_loop()
Browser/App request -> /api/v1/... -> router -> route function
Browser            -> /admin/       -> static files from admin-app/
```

## 5. Try it
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```
- `uv run` uses the project environment. `uvicorn` is the server program. `app.main:app` means "module `app.main`, object `app`". `--reload` restarts on code change. `--port 8000` sets the port.
- Then open `http://127.0.0.1:8000/docs` (auto API docs) and `http://127.0.0.1:8000/admin/`.
- Expected: the server prints `Uvicorn running on http://127.0.0.1:8000`.

## 6. Can it be better?
- Good: small and readable; session always closed; admin page served by the same server.
- Weak:
  - Database migration and admin creation happen at import time inside `create_app()` (`main.py:24-29`). Simply importing this file touches the database, which makes tests harder.
  - Migration runs on every start and in every worker.
  - `lifespan` does nothing at shutdown.
  - The health router is added without the version prefix (line 32); that may be on purpose for load balancers (I am not sure; check `routes/health.py`).
- Cleaner way (opinion): move the database work into `lifespan` before `yield`.
```python
@asynccontextmanager
async def lifespan(_):
    initialize_database()
    with SessionLocal() as db:
        AdminAuthService().bootstrap(db)
    realtime_hub.bind_running_loop()
    yield
```
- Security: no CORS setup is visible here (not sure it is needed for the admin page on the same origin). `/admin` is public static files; real protection is the admin token checked in the API.

## 7. Check yourself
1. What happens, step by step, between `uvicorn app.main:app` and the first request being served?
2. Why does `main.py` import `app.models` even though it never uses the name?
