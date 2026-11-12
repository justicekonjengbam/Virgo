# backend/scripts/test.ps1

## 1. Purpose
Windows PowerShell shortcut that runs all backend tests with pytest. It moves into `backend/` and runs pytest from the venv. Pytest then uses the settings in `backend/pyproject.toml:37-40`. Not directly runnable on Linux.

## 2. Imports, one by one
No imports.

## 3. Walk through the code, top to bottom
Line 1: `$backendRoot = Resolve-Path (Join-Path $PSScriptRoot '..')` (`backend/scripts/test.ps1:1`). Gives the absolute path of `backend`.

Line 2: `Set-Location $backendRoot` (`:2`). Same as `cd`. Pytest needs this so `testpaths = ["tests"]` is found.

Line 3: `& .\.venv\Scripts\python.exe -m pytest` (`:3`)
- `&` runs the program. `.\` means "in the current folder" (now `backend`).
- `-m pytest` runs pytest, which finds `tests/test_*.py` and runs each `test_*` function.
- Example output: `10 passed in 1.2s`.

## 4. How data flows
```
test.ps1 -> cd backend -> venv python -> pytest -> reads pyproject -> tests/*.py -> pass/fail
```

## 5. Try it
Not directly runnable on Linux. Equivalent:
```zsh
cd backend && uv run pytest -q
```
`-q` means quiet output.

## 6. Can it be better?
- Good: shortest possible wrapper.
- Weak: uses a relative path, unlike the other scripts that use `Join-Path`. Cannot pass extra pytest flags (use `@args`). No venv check.
- Cleaner way (opinion): `& $python -m pytest @args` so `.\test.ps1 -k outstation` works.
- Security: none.

## 7. Check yourself
1. Why does the script change folder first?
2. How could you pass `-k name` through to pytest?
