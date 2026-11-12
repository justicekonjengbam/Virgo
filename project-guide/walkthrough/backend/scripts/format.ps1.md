# backend/scripts/format.ps1

## 1. Purpose
A PowerShell script (PowerShell = the Windows shell language; `.ps1` files are its scripts) that auto-formats all backend Python code with ruff. It is a shortcut for Windows developers. It calls the venv Python, which calls ruff. On your Arch/zsh machine it is not directly runnable; use the zsh equivalent in section 5.

## 2. Imports, one by one
No imports. PowerShell commands used are explained below.

## 3. Walk through the code, top to bottom
Line 1: `$backendRoot = Resolve-Path (Join-Path $PSScriptRoot '..')` (`backend/scripts/format.ps1:1`)
- `$PSScriptRoot` is a built-in variable: the folder that holds this script (`backend/scripts`).
- `Join-Path A B` glues paths: gives `backend/scripts/..`.
- `Resolve-Path` turns that into a clean absolute path: `backend`.
- `$backendRoot = ...` stores it in a variable (all variables start with `$`).

Line 2: `& (Join-Path $backendRoot '.venv\Scripts\python.exe') -m ruff format $backendRoot` (`backend/scripts/format.ps1:2`)
- `&` is the *call operator*: it runs the program whose path is in the parentheses.
- `.venv\Scripts\python.exe` is the Python inside the virtual environment on Windows. (On Linux it is `.venv/bin/python`.)
- `-m ruff` means "run the module ruff". `format` is its sub-command: rewrites files to a standard style. `$backendRoot` is the folder to format.
- Output example: `12 files reformatted, 40 files left unchanged`.

## 4. How data flows
```
.\format.ps1 -> finds backend/ -> .venv python -> ruff format backend/ -> files rewritten on disk
```

## 5. Try it
Not directly runnable on Linux. Equivalent in zsh:
```zsh
cd backend && uv run ruff format .
```
`uv run` runs a command inside the project venv. `.` means the current folder.

## 6. Can it be better?
- Good: works from any current folder because it uses `$PSScriptRoot`.
- Weak: Windows-only path `Scripts\python.exe`; fails with an unclear error if the venv is missing (`start-dev.ps1` checks, this one does not). No `$LASTEXITCODE` pass-through.
- Cleaner way (opinion): use one cross-platform task runner (`uv run ruff format`, or a `Makefile`).
- Security: none.

## 7. Check yourself
1. What does `$PSScriptRoot` hold?
2. What would you change to run this on Linux?
