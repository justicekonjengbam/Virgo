# `backend/app/core/config.py`

## 1. Purpose
This file holds every setting of the backend in one class, `Settings`. It reads values from environment variables or a `.env` file, and falls back to defaults written in the code. Almost every backend file calls `get_settings()` from here: `backend/app/db.py:8`, `backend/app/main.py:10`, and the three login files in `api/dependencies/`.

## 2. Imports, one by one
Standard library:
- `from functools import lru_cache` (`config.py:1`). **functools** is a built-in module of helper tools for functions. `lru_cache` is a **decorator** (a line starting with `@` placed above a function that wraps it with extra behavior) that remembers a function's result. *Example:* after `@lru_cache`, calling `get_settings()` twice runs the body once and returns the same object the second time. Used at line 33. It can also cache with arguments: `fib(30)` runs fast.
- `from pathlib import Path` (`config.py:2`). **pathlib** gives file paths as objects. *Example:* `Path('/tmp') / 'a.txt'` gives `/tmp/a.txt`. Used to find the backend folder. It can also read files: `Path('x').read_text()`.

Third party:
- `from pydantic_settings import BaseSettings, SettingsConfigDict` (`config.py:4`). **pydantic-settings** is a library that builds a settings object from environment variables and checks the types. `BaseSettings` is the class you inherit from. `SettingsConfigDict` is a typed dictionary for options. *Example:* with env var `DEBUG=true`, a field `debug: bool` becomes `True`. It can also read secrets files.

Project imports: none.

## 3. Walk through the code, top to bottom

**`BACKEND_ROOT = Path(__file__).resolve().parents[2]`** (`config.py:6`)
- `__file__` is the path of this file (`.../backend/app/core/config.py`).
- `.resolve()` turns it into a full absolute path and removes `..` parts.
- `.parents[2]` goes up: `[0]` is `core`, `[1]` is `app`, `[2]` is `backend`. So `BACKEND_ROOT` is the `backend` folder.

**`DEFAULT_DATABASE_URL = f"sqlite:///{(BACKEND_ROOT / 'cabapp.db').as_posix()}"`** (`config.py:7`)
- An **f-string** (a string where `{...}` is replaced by a value) builds a database address. **SQLite** (a database stored in one file) is the default. `.as_posix()` writes the path with `/`. Result looks like `sqlite:////home/rem/.../backend/cabapp.db` (three slashes then an absolute path starting with `/`).

**`class Settings(BaseSettings)`** (`config.py:10`)
A **class** (a blueprint for objects) whose fields are settings. Each line `name: type = default` means: look for an env var named `NAME` (case does not matter); if missing, use the default. Fields:
- `app_name`, `environment`, `debug`: display name, mode label, debug switch (lines 11-13).
- `api_v1_prefix = '/api/v1'`: URL start for all v1 routes, used in `main.py:33`.
- `database_url`: where the database is (line 15).
- `auto_migrate = True`: if true, the app upgrades database tables on start (used by `db.py:33`). **Migration** (a versioned script that changes the table layout. *Example:* "add column `status`").
- `jwt_secret_key`, `jwt_algorithm = 'HS256'`, `access_token_minutes = 15`, `refresh_token_days = 30` (lines 17-20): **JWT** (JSON Web Token, a signed text that proves who you are. *Example:* `eyJhbGci...`). The key signs the tokens. HS256 is the signing method. The default key is a placeholder text, `<secret>`-like; real deployments must override it.
- `otp_expiry_minutes = 10`: **OTP** (one-time password, a short code sent by SMS) lifetime.
- `firebase_credentials_path: str | None = None`: path to a Firebase key file; `str | None` means text or nothing.
- `admin_bootstrap_email/password/name/role` (lines 23-26): the first admin to create at start (see `main.py:27`). Email and password default to `None`, so no admin is created unless you set them.
- `geoapify_api_key`: key for the Geoapify map service, `None` by default.
- `maps_contact_email`: a contact email sent to map providers (line 28). It is a real personal-looking address in the code; see section 6.

**`model_config = SettingsConfigDict(env_file=BACKEND_ROOT / '.env', extra='ignore')`** (`config.py:30`)
- `env_file` tells pydantic to also read `backend/.env`. *Example line in it:* `DEBUG=true`.
- `extra='ignore'` means unknown names in `.env` are skipped, not errors.

**`@lru_cache def get_settings() -> Settings: return Settings()`** (`config.py:33-35`)
- Builds the `Settings` object once and reuses it. Input: none. Output: the same `Settings` every time. `Settings()` reads env vars and `.env` at that moment.
- Errors: pydantic raises a validation error if a value has the wrong type (for example `ACCESS_TOKEN_MINUTES=abc`).

## 4. How data flows
```
.env file / OS env vars
        |
        v
  Settings()  --(built once, cached by lru_cache)-->  get_settings()
                                                         |
          db.py, main.py, auth dependencies <------------+
```

## 5. Try it
```bash
cd backend
uv run python -c "from app.core.config import get_settings as g; s=g(); print(s.app_name, s.access_token_minutes, g() is s)"
ACCESS_TOKEN_MINUTES=5 uv run python -c "from app.core.config import get_settings as g; print(g().access_token_minutes)"
```
- `ACCESS_TOKEN_MINUTES=5 cmd` sets an env var for that one command only.
- Expected: `CabApp API 15 True`, then `5`. (`g() is s` is `True` because of the cache.)

## 6. Can it be better?
- Good: one typed place for all settings; defaults let a new developer start with no setup.
- Weak:
  - `jwt_secret_key` has a working default (`config.py:17`). If production forgets to set it, anyone who reads this public code can forge tokens.
  - `maps_contact_email` hard-codes a personal email (`config.py:28`).
  - `environment` is never checked, so nothing forces a safe config in production.
- Cleaner way (opinion): fail on start when unsafe.
```python
# after the class
if Settings().environment == 'production' and Settings().jwt_secret_key.startswith('change-this'):
    raise RuntimeError('Set JWT_SECRET_KEY')
```
Or give `jwt_secret_key` no default so it is always required.
- Security: the default signing key above is the main risk. Never commit a real `.env`.

## 7. Check yourself
1. If `DATABASE_URL` is not set anywhere, which database file does the app use and where is it?
2. Why does `get_settings()` use `lru_cache`, and what would change without it?
