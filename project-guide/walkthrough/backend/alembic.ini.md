# backend/alembic.ini

## 1. Purpose
The settings file for **Alembic** (a tool that changes the database structure step by step. These steps are called **migrations**. *Example:* "add column `email` to table `passenger_profile`"). When you run `alembic ...` in `backend/`, Alembic reads this file first.

## 2. Imports, one by one
Not applicable: an INI config file, no imports. `[alembic]` is a **section header** that groups settings.

## 3. Walk through the file
- Line 1 `[alembic]`: the section Alembic reads.
- Line 2 `script_location = app/database/migrations`: the folder with the migration scripts (and `env.py`, which connects to the database). The path is relative to where you run the command, so run Alembic from `backend/`.
- Line 3 `prepend_sys_path = .`: adds the current folder to Python's import path, so migration scripts can `import app...`.
Missing here (the usual extras): there is no `sqlalchemy.url`, so the database address must come from `env.py` (probably from `DATABASE_URL`; check `backend/app/database/migrations/env.py`). There is also no logging section.

## 4. How data flows
```
alembic upgrade head -> reads alembic.ini -> loads app/database/migrations/env.py
   -> connects to DATABASE_URL -> runs each script in versions/ not yet applied
```

## 5. Try it
```
cd backend && uv run alembic current
```
`uv run` runs a tool inside the project environment. `alembic current` shows which migration the database is at. `uv run alembic upgrade head` applies all new migrations (`head` = the newest one). Expected for `current`: a revision id such as `abc123 (head)`, or nothing for a new database.

## 6. Can it be better?
- Good: very small; sets the path and import root correctly.
- Weak: no logging section, no file name template (migration file names are random hashes only), so history is harder to read.
- Cleaner: add `file_template = %%(year)d%%(month).2d%%(day).2d_%%(rev)s_%%(slug)s` for dated file names. (Opinion.)
- Security: no secret here, which is good: keep the database URL in `.env`, not in this file.

## 7. Check yourself
1. From which folder should you run `alembic`, and why?
2. Where does Alembic find the database address in this project?
