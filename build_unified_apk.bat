@echo off
cd /d "%~dp0"
title VIRGO - Build Release APK
echo =======================================================
echo          VIRGO - BUILD PRODUCTION RELEASE APK
echo =======================================================
echo.

if not exist "dist\apks" mkdir "dist\apks"

echo [*] Building VIRGO Release APK...
cd passenger-app\android
call gradlew.bat assembleRelease
if %ERRORLEVEL% neq 0 (
    echo [!] Build failed!
    pause
    exit /b %ERRORLEVEL%
)
cd /d "%~dp0"
copy /y "passenger-app\android\app\build\outputs\apk\release\app-release.apk" "dist\apks\VIRGO.apk"
copy /y "passenger-app\android\app\build\outputs\apk\release\app-release.apk" "dist\apks\VIRGO-Unified.apk"
echo.
echo =======================================================
echo [SUCCESS] VIRGO Release APK generated!
echo Path: %~dp0dist\apks\VIRGO.apk
echo =======================================================
explorer "%~dp0dist\apks"
pause
