Write-Host "=======================================================" -ForegroundColor Magenta
Write-Host "       VIRGO HAPPY CABBING - LIVE BACKEND" -ForegroundColor Magenta
Write-Host "=======================================================" -ForegroundColor Magenta
Write-Host ""
if (-not (Test-Path "dev-tools\cloudflared.exe")) {
    Write-Host "[Setup] dev-tools\cloudflared.exe not found. Downloading Cloudflare Tunnel..." -ForegroundColor Yellow
    if (-not (Test-Path "dev-tools")) { New-Item -ItemType Directory -Path "dev-tools" | Out-Null }
    Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "dev-tools\cloudflared.exe"
}

Write-Host "Starting Backend API Server..." -ForegroundColor Cyan

$backendProcess = Start-Process -FilePath "backend\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host "Connecting to Cloudflare Public Tunnel..." -ForegroundColor Green
Write-Host "Look for your live link (https://...trycloudflare.com) below:" -ForegroundColor Yellow
Write-Host "  - Web Admin Panel: [your live link]/admin (or http://127.0.0.1:8000/admin)" -ForegroundColor Cyan
Write-Host "  - Login: admin@virgo.com / admin12345" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Magenta

try {
    & "dev-tools\cloudflared.exe" tunnel --url http://127.0.0.1:8000
} finally {
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

