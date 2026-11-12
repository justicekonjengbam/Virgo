$backendRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $backendRoot
& .\.venv\Scripts\python.exe -m pytest
