# `backend/app/db.py`

## 1. Purpose
This file sets up the connection to the database and gives the rest of the backend three things: an `engine` (the connection), `SessionLocal` (a factory for sessions), `Base` (the parent of all table classes), plus `get_db` (hands a session to a route) and `initialize_database` (runs migrations). It is imported by `backend/app/main.py:11` and by the three files in `api/dependencies/` (`get_db`). The table classes in `app/models/` inherit `Base`.

## 2. Imports, one by one
Standard library:
- `from pathlib import Path` (`db.py:1`). Gives file paths as objects. *Example:* `Path('a') / 'b'` is `a/b`. Used at line 35 to find the backend folder.

Third party:
- `from alembic import command` (`db.py:3`). **Alembic** is the migration tool for SQLAlchemy (it applies versioned scripts that change tables). `command` holds its actions. *Example:* `command.upgrade(cfg, 'head')` brings the database to the newest version. It can also `downgrade` or `revision` (make a new script).
- `from alembic.config import Config` (`db.py:4`). A class that holds Alembic settings, normally read from `alembic.ini`. *Example:* `Config('alembic.ini')`.
- `from sqlalchemy import create_engine` (`db.py:5`). **SQLAlchemy** is an **ORM** (Object-Relational Mapper: lets you use Python classes instead of writing SQL. *Example:* `db.get(Driver, 3)` instead of `SELECT * FROM drivers WHERE id=3`). `create_engine` builds the **engine** (the object that knows how to talk to one database).
- `from sqlalchemy.orm import DeclarativeBase, sessionmaker` (`db.py:6`). `DeclarativeBase` is the parent class for table classes. `sessionmaker` makes a factory that creates **sessions** (a session is one conversation with the database: you read, change, then commit or roll back. *Example:* `db = SessionLocal(); db.add(row); db.commit()`).

Project import:
- `from app.core.config import get_settings` (`db.py:8`), from `backend/app/core/config.py`. Gives the cached settings.

## 3. Walk through the code, top to bottom

**`settings = get_settings()`** (`db.py:10`) reads the settings once when this file is first imported.

**`engine = create_engine(...)`** (`db.py:11-15`)
- First argument: `settings.database_url`, the address of the database.
- `connect_args={'check_same_thread': False} if ... startswith('sqlite') else {}` (line 13). SQLite by default refuses to be used from a thread other than the one that opened it. FastAPI runs routes in several threads, so for SQLite the check is turned off. Other databases get an empty dictionary.
- `pool_pre_ping=not ...startswith('sqlite')` (line 14). The **connection pool** keeps connections open for reuse. "Pre-ping" tests a connection before use and replaces it if dead. Turned on for non-SQLite (for example PostgreSQL), off for SQLite (a file has no network to break).

**`SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`** (`db.py:16`)
- A factory. Calling `SessionLocal()` returns a new session tied to `engine`.
- `autocommit=False`: changes are saved only when you call `db.commit()`.
- `autoflush=False`: SQLAlchemy does not send pending changes to the database before each query. You must `flush()` or `commit()` yourself. (*Example:* after `db.add(x)` without commit, a query will not see `x`.)

**`class Base(DeclarativeBase): pass`** (`db.py:19-20`)
An empty class. Every table class (for example `Driver`) inherits from it, and SQLAlchemy collects all of them in `Base.metadata`. `pass` means "no extra body".

**`def get_db()`** (`db.py:23-28`)
- A **generator** (a function that uses `yield` to hand out a value and then pauses; it resumes later). FastAPI treats it as a **dependency** (a function FastAPI runs before a route and passes the result in. *Example:* `db: Session = Depends(get_db)`).
- Flow: open a session (line 24), `yield db` (line 26) to give it to the route, then after the route finishes the `finally` block runs `db.close()` (line 28) to release the connection, even if the route raised an error.
- Input: none. Output: one `Session`.

**`def initialize_database() -> None`** (`db.py:31-38`)
- The docstring says: run versioned migrations locally; production runs the same command by hand.
- Line 33: if `auto_migrate` is false, return and do nothing.
- Line 35: `Path(__file__).resolve().parent.parent` is the `backend` folder (`db.py` is in `backend/app`, so one `.parent` is `app`, two is `backend`).
- Line 36: `Config(str(backend_root / 'alembic.ini'))` loads Alembic's settings file.
- Line 37: `set_main_option('script_location', ...)` tells Alembic the migration scripts are in `backend/app/database/migrations`.
- Line 38: `command.upgrade(alembic_config, 'head')` runs every migration not yet applied, up to the newest ("head").
- Errors: Alembic raises if a script fails or the database is unreachable.

## 4. How data flows
```
HTTP request -> FastAPI route
                  |  Depends(get_db)
                  v
            get_db(): SessionLocal() --> Session  --yield--> route code uses db
                                                              |
            finally: db.close() <-----------------------------+ (after response)

App start: main.py -> initialize_database() -> Alembic upgrade head -> tables ready
```

## 5. Try it
```bash
cd backend
uv run python -c "from app.db import SessionLocal; db=SessionLocal(); print(db.execute(__import__('sqlalchemy').text('select 1')).scalar()); db.close()"
```
- Opens a session, runs the SQL `select 1`, prints the single value, closes the session.
- Expected output: `1`.
Migrate by hand: `uv run alembic upgrade head` (run inside `backend`).

## 6. Can it be better?
- Good: the session is always closed; SQLite and other databases are handled separately; migrations are real Alembic scripts.
- Weak:
  - `settings` and `engine` are created at import time (lines 10-15), so importing `app.db` has side effects and tests cannot easily swap the database.
  - `autoflush=False` surprises beginners (see line 16).
  - `initialize_database` runs on every app start, including when several server workers start together; two workers could try to migrate at once.
  - No rollback on error in `get_db`; SQLAlchemy rolls back on `close()` for uncommitted work, so this is acceptable (simplified).
- Cleaner way (opinion): run migrations as a separate deploy step and set `AUTO_MIGRATE=false` in production.
- Security: no secrets here. The database URL may contain a password in production; it comes from the environment, not this file.

## 7. Check yourself
1. What does the `finally` block in `get_db` guarantee, and why does that matter?
2. Why is `check_same_thread` set to `False` only for SQLite?
