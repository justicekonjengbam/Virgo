@echo off
cd /d "%~dp0"
title VIRGO - Build Production APKs
echo =======================================================
echo          VIRGO HAPPY CABBING - BUILD APKS
echo =======================================================
echo.

if not exist "dist\apks" mkdir "dist\apks"

echo [1/2] Building VIRGO Passenger App Release APK...
cd passenger-app\android
call gradlew.bat assembleRelease
if %ERRORLEVEL% neq 0 (
    echo [!] Passenger App build failed.
    pause
    exit /b %ERRORLEVEL%
)
cd /d "%~dp0"
copy /y "passenger-app\android\app\build\outputs\apk\release\app-release.apk" "dist\apks\VIRGO-Passenger.apk"
echo -> VIRGO Passenger APK ready at dist\apks\VIRGO-Passenger.apk
echo.

echo [2/2] Building VIRGO Driver App Release APK...
cd driver-app\android
call gradlew.bat assembleRelease
if %ERRORLEVEL% neq 0 (
    echo [!] Driver App build failed.
    pause
    exit /b %ERRORLEVEL%
)
cd /d "%~dp0"
copy /y "driver-app\android\app\build\outputs\apk\release\app-release.apk" "dist\apks\VIRGO-Driver.apk"
echo -> VIRGO Driver APK ready at dist\apks\VIRGO-Driver.apk
echo.

echo =======================================================
echo [SUCCESS] Both APKs built successfully!
echo Location: %~dp0dist\apks\
echo =======================================================
explorer "%~dp0dist\apks"
pause
