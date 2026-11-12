# admin-app/README.md

## 1. Purpose
The short readme of the Admin console. It tells you two facts: where the admin site lives and how the first admin account is created. The site files are `index.html`, `app.js`, `styles.css` in the same folder. FastAPI serves them: `backend/app/main.py:34-36` mounts the folder at `/admin`.

## 2. Imports, one by one
Not code, so there are no imports. This is a Markdown file (plain text with simple marks: `#` makes a heading, backticks make code).

## 3. Walk through the file
- Line 1 `# CabSure Admin`: the title.
- Line 3: the console is at `http://localhost:8000/admin`. *Why it works:* `app.mount("/admin", StaticFiles(directory=admin_app_directory, html=True))` (`main.py:36`). A **static file server** (sends files as they are, no computing) with `html=True` returns `index.html` when you open the folder URL.
- Line 5: set `ADMIN_BOOTSTRAP_EMAIL` and `ADMIN_BOOTSTRAP_PASSWORD` in `backend/.env` before the first start. **Bootstrap** (create the very first record so you can log in at all). `AdminAuthService().bootstrap(db)` runs at startup (`main.py:25`). Only the password **hash** (a one-way scrambled form of the password) is stored. Real values: write `<secret>` and never commit them.

## 4. How data flows
```
you edit backend/.env --> start backend --> create_app() --> AdminAuthService.bootstrap
   --> admin row (email + password hash) --> you open /admin and sign in
```

## 5. Try it
```zsh
cd backend
uv run uvicorn app.main:app --port 8000
```
`uvicorn` is the server program for FastAPI; `app.main:app` means "file app/main.py, object app"; `--port 8000` picks the port. Then open `http://localhost:8000/admin`. (Exact start command may differ in this repo; check `backend/` scripts.)

## 6. Can it be better?
- Good: very short and correct about the bootstrap step.
- Weak: no list of pages, no note that the API base is `/api/v1`, no password rules (new password needs 12 characters, `app.js`/`index.html`), no explanation of what happens if the bootstrap variables are missing.
- Cleaner way: add a "Run it" section with the command above and a short role/permission table.
- Security: good that only a hash is stored. Tell people to change the bootstrap password after first login.

## 7. Check yourself
1. Which code line makes `/admin` show this site?
2. Why must the bootstrap variables exist before the first start?
