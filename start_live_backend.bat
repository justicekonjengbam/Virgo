@echo off
cd /d "%~dp0"
title VIRGO - Live Cloud Backend
echo =======================================================
echo          VIRGO HAPPY CABBING - LIVE BACKEND
echo =======================================================
echo.
if not exist "dev-tools\cloudflared.exe" (
    echo [Setup] dev-tools\cloudflared.exe not found. Downloading Cloudflare Tunnel...
    if not exist "dev-tools" mkdir "dev-tools"
    curl -fLo "dev-tools\cloudflared.exe" https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
)

echo Starting Backend API Server on port 8000...
start "VIRGO Backend Server" cmd /k "cd /d "%~dp0" && backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul
echo.
echo Connecting to Cloudflare Public Tunnel...
echo Look for your live link (https://...trycloudflare.com) below:
echo   - Web Admin Panel:  [your live link]/admin  (or http://127.0.0.1:8000/admin)
echo   - Login: admin@virgo.com / admin12345
echo =======================================================
dev-tools\cloudflared.exe tunnel --url http://127.0.0.1:8000
