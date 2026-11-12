# b7d9d0e0f001_add_driver_document_number.py

## 1. Purpose
This is a **migration** (a small script that changes the database layout step by step. *Example:* "add one new column to one table"). It adds a `document_number` column to the `driver_documents` table. It sits in the chain of migrations under `backend/app/database/migrations/versions/`. Alembic (the migration tool) runs it. It does not call any other project file.

## 2. Imports, one by one
Third-party:
- `from alembic import op` (`b7d9d0e0f001_add_driver_document_number.py:2`). **Alembic** is the migration tool for SQLAlchemy. `op` is its set of database actions. *Example:* `op.drop_table("x")` deletes table x. This file uses `op.add_column` and `op.drop_column`.
- `import sqlalchemy as sa` (`:3`). **SQLAlchemy** is a Python library that describes tables and columns as Python objects (an ORM = Object Relational Mapper). *Example:* `sa.String(length=10)` means a text column of at most 10 characters. This file uses it to describe the new column.

No standard library or project imports.

## 3. Walk through the code, top to bottom
- Docstring `"""add driver document number"""` (`:1`). A human note. Alembic shows it in `alembic history`.
- `revision = "b7d9d0e0f001"` (`:5`). The id of this migration. Alembic stores the id of the last applied migration in a table called `alembic_version`.
- `down_revision = "841c1f195299"` (`:6`). The id of the migration that must run before this one. This builds a chain, like a linked list. `841c1f195299` is `841c1f195299_add_static_location_catalog.py`.
- `branch_labels = None`, `depends_on = None` (`:7-8`). Unused options. Branch labels name a side branch. `depends_on` lists extra migrations needed first. `None` means "not used".
- `def upgrade() -> None:` (`:10`). Runs when you move forward. It calls
  `op.add_column("driver_documents", sa.Column("document_number", sa.String(length=128), nullable=False, server_default=""))` (`:11`). This asks the database to add a text column of up to 128 characters. `nullable=False` means the value may never be empty (NULL). `server_default=""` means the database fills every old row with an empty string, so old rows do not break the `NOT NULL` rule. Input: none. Output: none. It changes the database.
- `def downgrade() -> None:` (`:13`). Runs when you move back. `op.drop_column("driver_documents", "document_number")` (`:14`) removes the column and its data.

Errors: if the table `driver_documents` does not exist yet, the database raises an error. It exists after `e4ffba93f4c4`.

## 4. How data flows
```
you: alembic upgrade head
  -> Alembic reads alembic_version table (current id)
  -> finds this file (down_revision matches current)
  -> calls upgrade()
       -> op.add_column -> SQL: ALTER TABLE driver_documents ADD COLUMN document_number VARCHAR(128) NOT NULL DEFAULT ''
  -> writes new id into alembic_version
```

## 5. Try it
```zsh
cd backend
uv run alembic upgrade b7d9d0e0f001   # go forward up to this migration
uv run alembic downgrade -1           # go back one step
```
`uv run` runs a tool inside the project's Python environment. `alembic upgrade X` moves forward to id X. `downgrade -1` moves back one step. You should see lines like `Running upgrade 841c1f195299 -> b7d9d0e0f001`. I did not run this; the exact working folder for `alembic.ini` may differ, so check where `alembic.ini` is with `fd alembic.ini`.

## 6. Can it be better?
- Good: very small. Has a working `downgrade`. Safe default for old rows.
- Weak: no check that the column already exists (other migrations here, like `e3f8a2b60001`, do check). An empty-string default is a weak "no value" marker; a nullable column would be clearer. The default stays forever in the schema.
- Cleaner way (opinion): add the column, then remove the server default:
```python
op.add_column(..., server_default="")
op.alter_column("driver_documents", "document_number", server_default=None)
```
- Security: none here. The document number itself is personal data, so the app must not log it.

## 7. Check yourself
1. What does `down_revision` do, and what happens if it is wrong?
2. Why is `server_default=""` needed when `nullable=False`?
