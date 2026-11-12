# d2f7e1a50001_add_driver_document_review_metadata.py

## 1. Purpose
This **migration** (a script that changes the database layout one step at a time) adds three columns to `driver_documents`. They record who reviewed a driver's document, when, and a note. The admin app uses this when it approves or rejects documents. Alembic runs it. It calls no project file.

## 2. Imports, one by one
- `from alembic import op` (`d2f7e1a50001_add_driver_document_review_metadata.py:7`). Alembic is the migration tool; `op` holds the actions. *Example:* `op.add_column`.
- `import sqlalchemy as sa` (`:8`). SQLAlchemy describes column types in Python. *Example:* `sa.Text()` is a long text column.

## 3. Walk through the code, top to bottom
- Docstring (`:1-5`). Human note.
- `revision = 'd2f7e1a50001'` (`:11`), `down_revision = 'c1d6e1b40001'` (`:12`). This runs right after the online-status migration.
- `branch_labels`, `depends_on` = `None` (`:13-14`). Unused.
- `upgrade()` (`:17-20`) makes three `op.add_column("driver_documents", ...)` calls:
  - `review_note`, `sa.Text()`, nullable (`:18`). Free text reason.
  - `reviewed_by`, `sa.String(length=128)`, nullable (`:19`). Name or id of the admin. It is text, not a link to `admin_users`.
  - `reviewed_at`, `sa.DateTime(timezone=True)`, nullable (`:20`). `timezone=True` stores the time with its time zone. *Example:* `2026-10-26 09:00+00:00`.
  All three are `nullable=True` because old documents were never reviewed.
- `downgrade()` (`:23-26`) drops the three columns in reverse order.

Errors: fails if `driver_documents` is missing, or if a column already exists.

## 4. How data flows
```
alembic upgrade head
  -> upgrade(): 3 x ALTER TABLE driver_documents ADD COLUMN ...
  -> alembic_version = d2f7e1a50001
```

## 5. Try it
```zsh
cd backend
uv run alembic upgrade d2f7e1a50001
```
Expected line: `Running upgrade c1d6e1b40001 -> d2f7e1a50001, add driver document review metadata`. Not run by me.

## 6. Can it be better?
- Good: all new columns are nullable, so it is safe for old rows. Downgrade is complete.
- Weak: `reviewed_by` is a plain string, not a foreign key (a column that points to another table's row) to `admin_users.id`, so it can hold wrong names. No retry-safety check. Mixed quote style compared with other files (cosmetic).
- Cleaner way (opinion): `sa.Column('reviewed_by_admin_id', sa.Integer(), sa.ForeignKey('admin_users.id', ondelete='SET NULL'))`. But `admin_users` is created in the next migration, so this would need re-ordering.
- Security: the review note may hold private details; do not show it to the driver unless meant.

## 7. Check yourself
1. Why are all three columns nullable?
2. What does `timezone=True` change?
