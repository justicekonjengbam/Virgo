# backend/scripts/lint.ps1

## 1. Purpose
A Windows PowerShell shortcut that checks the backend code for mistakes and style problems with ruff. It does not change files. It reads the rules from `backend/pyproject.toml:34-35`. Not directly runnable on Linux.

## 2. Imports, one by one
No imports.

## 3. Walk through the code, top to bottom
Line 1: `$backendRoot = Resolve-Path (Join-Path $PSScriptRoot '..')` (`backend/scripts/lint.ps1:1`)
- `$PSScriptRoot` is the script's own folder. `Join-Path` adds `..` (parent folder). `Resolve-Path` makes it a clean absolute path, here the `backend` folder. It is stored in `$backendRoot`.

Line 2: `& (Join-Path $backendRoot '.venv\Scripts\python.exe') -m ruff check $backendRoot` (`backend/scripts/lint.ps1:2`)
- `&` runs the program in parentheses: the venv Python.
- `-m ruff check` runs the ruff linter module. It reports problems such as unused imports (rule F401) or wrong import order (rule I).
- Example output: `app/main.py:3:8: F401 'os' imported but unused`. Exit code is non-zero when problems exist.

## 4. How data flows
```
lint.ps1 -> backend/ path -> venv python -> ruff check (reads pyproject.toml rules) -> prints problems
```

## 5. Try it
Not directly runnable on Linux. Equivalent:
```zsh
cd backend && uv run ruff check .      # report
uv run ruff check . --fix              # also fix what is safe to fix
```

## 6. Can it be better?
- Good: tiny, clear, location independent.
- Weak: Windows-only; no venv-exists check; does not stop a CI job clearly if ruff fails (add `exit $LASTEXITCODE`).
- Cleaner way (opinion): one cross-platform command in a `Makefile`/`justfile`.
- Security: none.

## 7. Check yourself
1. Does `ruff check` change your files?
2. Where are the lint rules chosen?
