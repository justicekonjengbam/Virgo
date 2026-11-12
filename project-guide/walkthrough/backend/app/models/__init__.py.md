# backend/app/models/__init__.py

## 1. Purpose
This file has one job. When any code runs `import app.models`, Python runs this file. The file then imports every model class, so every database table is known to SQLAlchemy. It sits at `backend/app/models/__init__.py:1`. The startup code and the migration tools import `app.models`. This file calls `app/models/ride_hailing.py` and `app/models/user.py`.

**`__init__.py`** (a special file name. Python treats a folder as a *package* when it holds this file, and it runs the file the first time the folder is imported. *Example:* `import app.models` runs `app/models/__init__.py`.)

## 2. Imports, one by one
Standard library: none. Third party: none.

Project imports:
- `from app.models.ride_hailing import (...)` at `__init__.py:3-9`. It comes from `backend/app/models/ride_hailing.py`. It brings in 25 classes such as `Driver`, `Ride`, `Payment`. Each class is a table.
- `from app.models.user import AdminUser, Passenger` at `__init__.py:10`. It comes from `backend/app/models/user.py`.

**Package** (a folder of Python files that can be imported together. *Example:* `app.models` is a package; `app.models.user` is a file inside it.)

## 3. Walk through the code, top to bottom
- `__init__.py:1` is a docstring (a text in triple quotes that explains the file). It says that importing the package registers every model with SQLAlchemy *metadata*.
  **Metadata** (SQLAlchemy's list of all tables it knows. *Example:* `Base.metadata.tables` is a dict like `{'drivers': Table(...)}`.) A class only enters this list when its file is run. So a class that nobody imports would have no table created.
- `# noqa: F401` at lines 3 and 10 tells the linter *flake8/ruff* to be quiet. Rule F401 means "imported but unused". The names are indeed unused here. The import itself is the goal, because it has the side effect of registering the tables.
  **Linter** (a tool that reads code and warns about style problems. *Example:* `ruff check .`).
- The names are also re-exported. So other code can write `from app.models import Driver` instead of the longer path. This is a convenience.

No functions, no errors raised here. If one name is misspelled, Python raises `ImportError` when the package is first imported.

## 4. How data flows
```
alembic / app startup
   |  import app.models
   v
models/__init__.py --runs--> ride_hailing.py (25 classes) --> Base.metadata
                  \--runs--> user.py (2 classes)          --> Base.metadata
   v
create_all() or migration sees every table
```

## 5. Try it
```zsh
cd backend
uv run python -c "import app.models; from app.db import Base; print(sorted(Base.metadata.tables))"
```
- `uv run python -c "..."` runs one line of Python inside the project's environment.
- The line imports the package, then prints all table names, sorted.
Expected: a sorted list of 27 table names (25 plus 2), starting with `'admin_users'`, `'audit_logs'`.

## 6. Can it be better?
- Good: one clear place that guarantees all tables are registered. The comment explains why the odd imports exist.
- Weak: the list is typed by hand. A new model that is forgotten here will silently have no table. Also the import lines are long and uneven (opinion).
- Cleaner way: add a small test that compares `Base.metadata.tables` with the tables in the database. Or use `__all__` so the names are deliberate.
- Security: nothing risky.

## 7. Check yourself
1. Why does this file import classes that it never uses?
2. What does `# noqa: F401` do, and what could go wrong if you removed an import line from this file?
