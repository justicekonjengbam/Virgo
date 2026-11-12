# backend/pyproject.toml

## 1. Purpose
This file is the project card of the backend. It tells Python tools the project name, the Python version, the libraries to install, and the settings for the test tool (pytest) and the lint tool (ruff). It sits at the root of `backend/`. `pip` or `uv` read it when you install. `pytest` and `ruff` read it when they run. It is TOML (a simple `key = value` config format, with `[sections]`). It is not code, so it is not runnable.

## 2. Imports, one by one
There are no imports. Instead, the file lists *dependencies* (libraries to install). They are explained in section 3.

## 3. Walk through the config, top to bottom

### `[build-system]` (`backend/pyproject.toml:1-3`)
- **Build system** (the tool that turns your folder into an installable package. *Example:* `setuptools` packs the `app` folder so `pip install -e .` works).
- `requires = ["setuptools>=69"]` means: before building, install setuptools version 69 or newer.
- `build-backend = "setuptools.build_meta"` names the Python entry point that does the build.

### `[project]` (`backend/pyproject.toml:5-8`)
- `name = "cabapp-api"` is the package name. `version = "0.1.0"` is its version.
- `requires-python = ">=3.12"` means Python 3.11 or older is refused at install time.

### `dependencies` (`backend/pyproject.toml:9-22`)
Each line is `name>=min,<max`. This is a **version range** (allowed versions. *Example:* `fastapi>=0.115,<1.0` allows 0.115 up to, but not including, 1.0). The upper limit protects you from a breaking major version.
- `fastapi` is the web framework. It turns Python functions into HTTP endpoints.
- `uvicorn[standard]` is the server that runs the FastAPI app. `[standard]` is an **extra** (optional bundle of helper libraries, like faster event loop and websocket support).
- `pydantic-settings` reads settings from environment variables and `.env` into typed Python objects.
- `sqlalchemy` is the ORM (Object-Relational Mapper: lets you use Python classes instead of SQL text. *Example:* `db.get(Driver, 1)`).
- `alembic` runs database migrations (versioned scripts that change table shapes).
- `psycopg[binary]` is the PostgreSQL driver. `[binary]` ships a prebuilt copy so you need no C compiler.
- `redis` is the client for the Redis in-memory store (used for fast, short-lived data).
- `firebase-admin` lets the server check Firebase login tokens.
- `httpx` is an HTTP client for calling other web services.
- `python-multipart` lets FastAPI read file uploads and form data.
- `PyJWT` creates and checks JWT (JSON Web Token: a signed text that proves who you are).
- `pwdlib[argon2]` hashes passwords with the Argon2 algorithm.

Note the odd layout at lines 19-21: the commas for the last two items start the next line (`,"PyJWT..."`). TOML accepts this. It only looks like someone added lines by hand.

### `[project.optional-dependencies]` (`backend/pyproject.toml:24-25`)
`dev = [...]` is a named group installed only when you ask: `pip install -e .[dev]`.
- `pytest` runs tests. `pytest-asyncio` lets tests use `async def`. `ruff` is a very fast linter and formatter.

### `[tool.setuptools]` (`backend/pyproject.toml:27-28`)
`packages = ["app"]` tells setuptools to include only the `app` folder. Without it, setuptools may find several top-level folders (`tests`, `scripts`) and stop with an error.

### `[tool.ruff]` and `[tool.ruff.lint]` (`backend/pyproject.toml:30-35`)
- `line-length = 100` and `target-version = "py312"` set the format width and the Python level.
- `select = ["E","F","I","B","UP"]` turns on rule groups: E = style errors, F = unused/undefined names, I = import order, B = likely bugs, UP = use newer Python syntax.

### `[tool.pytest.ini_options]` (`backend/pyproject.toml:37-40`)
- `testpaths = ["tests"]` makes bare `pytest` look only in `tests/`.
- `pythonpath = ["."]` adds `backend/` to the import path, so `from app.db import Base` works.
- `addopts = "-p no:cacheprovider"` always adds a flag that turns off the `.pytest_cache` folder.

## 4. How data flows
```
you: pip install -e ".[dev]"
   -> pip reads pyproject.toml
   -> [build-system] installs setuptools
   -> [project] dependencies + dev group downloaded
   -> package "app" linked into the venv (editable)

you: pytest
   -> reads [tool.pytest.ini_options]
   -> runs files in tests/ with backend/ on sys.path
```

## 5. Try it
```zsh
cd backend
uv venv && uv pip install -e '.[dev]'   # make venv, install app + dev tools
uv run pytest                           # runs tests/ using the settings above
uv run ruff check .                     # lint with the rules above
```
`-e` means *editable*: code changes apply without reinstalling. Quote `'.[dev]'` because zsh treats `[ ]` as a glob. Expected: pytest prints a line of dots and "passed".

## 6. Can it be better?
- Good: version ranges with upper limits; dev tools separated; one file configures all tools.
- Weak: no lock file is visible here, so two installs months apart can get different versions (check for `uv.lock`). The stray leading commas (lines 20-21) are untidy. `redis>=5.2,<7.0` is a wide range.
- Cleaner way (opinion): put one dependency per line with a trailing comma.
```toml
"python-multipart>=0.0.20,<1.0",
"PyJWT>=2.10,<3.0",
```
- Security: no secrets here. Pin or lock versions and audit them (`uv pip audit` style tools) to reduce supply-chain risk.

## 7. Check yourself
1. What is the difference between `dependencies` and the `dev` group?
2. Why does `pythonpath = ["."]` matter for the tests?
