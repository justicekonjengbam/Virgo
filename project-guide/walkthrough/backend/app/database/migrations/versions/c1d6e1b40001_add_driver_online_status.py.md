# c1d6e1b40001_add_driver_online_status.py

## 1. Purpose
This **migration** (a script that changes the database layout one step at a time) adds an `is_online` true/false column to the `drivers` table, so the server can remember if a driver is online. It also **merges** two migration branches into one. Alembic runs it. It calls no project file.

## 2. Imports, one by one
- `from alembic import op` (`c1d6e1b40001_add_driver_online_status.py:7`). Alembic is the migration tool. `op` holds its actions. *Example:* `op.add_column(...)`.
- `import sqlalchemy as sa` (`:8`). SQLAlchemy describes columns and types in Python. *Example:* `sa.Boolean()` is a true/false column. Used here for the type and for `sa.false()`.

## 3. Walk through the code, top to bottom
- Docstring (`:1-5`). Lists `Revises: b7d9d0e0f001, 28bc77a50115`. This is only a note for humans.
- `revision = "c1d6e1b40001"` (`:11`). The id of this migration.
- `down_revision = ("b7d9d0e0f001", "28bc77a50115")` (`:12`). A tuple with **two** parents. Before this change the history had two heads (two latest migrations at the same time): `b7d9d0e0f001` and `28bc77a50115`. Listing both makes this a **merge migration**. Alembic needs one head to run `upgrade head`.
- `branch_labels = None`, `depends_on = None` (`:13-14`). Not used.
- `upgrade()` (`:17`): `op.add_column("drivers", sa.Column("is_online", sa.Boolean(), nullable=False, server_default=sa.false()))` (`:18`). Adds a boolean column. `nullable=False` forbids NULL. `sa.false()` is a database-neutral "false" value, written correctly for each database (`0` in SQLite, `false` in PostgreSQL). Old rows become offline.
- `downgrade()` (`:21`): `op.drop_column("drivers", "is_online")` (`:22`) removes the column.

## 4. How data flows
```
alembic upgrade head
  -> needs both b7d9d0e0f001 and 28bc77a50115 applied
  -> runs this upgrade()
       -> ALTER TABLE drivers ADD COLUMN is_online BOOLEAN NOT NULL DEFAULT false
  -> alembic_version = c1d6e1b40001
```

## 5. Try it
```zsh
cd backend
uv run alembic heads      # should show one head at the end of the whole chain
uv run alembic history    # shows the merge as a fork joining here
```
`alembic heads` lists latest migrations. With the whole chain you see only `j8e3a7b10001`. Not directly tested by me.

## 6. Can it be better?
- Good: uses `sa.false()` so it works on SQLite and PostgreSQL. Merge is done cleanly.
- Weak: the merge migration also does real work, which mixes two jobs. No existence check (others in this folder have one). Plain `Revises:` in the docstring duplicates the variable and can go stale.
- Cleaner way (opinion): use `alembic merge -m "merge heads" b7d9d0e0f001 28bc77a50115` to make an empty merge file, and put the column in a separate file.
- Security: none.

## 7. Check yourself
1. Why is `down_revision` a tuple here?
2. What value do existing drivers get for `is_online` after this runs?
