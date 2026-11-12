@echo off
title VIRGO - Live Cloud Backend
echo =======================================================
echo          VIRGO HAPPY CABBING - LIVE BACKEND
echo =======================================================
echo.
echo Starting Backend API Server...
start "VIRGO Backend Server" cmd /k "backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo.
echo Connecting to Cloudflare Public Tunnel...
echo Look for your live link (https://...trycloudflare.com) below:
echo =======================================================
dev-tools\cloudflared.exe tunnel --url http://127.0.0.1:8000
