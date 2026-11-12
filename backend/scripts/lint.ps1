$backendRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
& (Join-Path $backendRoot '.venv\Scripts\python.exe') -m ruff check $backendRoot
