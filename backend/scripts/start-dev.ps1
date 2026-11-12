$backendRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$python = Join-Path $backendRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $python)) {
  throw 'Backend virtual environment is missing. Run: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e .[dev]'
}

Set-Location $backendRoot
& $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
