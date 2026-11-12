# VIRGO Happy Cabbing - Real-Device APK Installer
# Target: CMF Phone 2 Pro / Any authorized Android device connected via ADB

$adb = "C:\platform-tools\adb.exe"

Write-Host "==================================================" -ForegroundColor Magenta
Write-Host " VIRGO - REAL DEVICE APP INSTALLER" -ForegroundColor Magenta
Write-Host "==================================================" -ForegroundColor Magenta

# Check ADB devices
$devices = & $adb devices
Write-Host "`nChecking connected devices..." -ForegroundColor Cyan
Write-Host $devices

if ($devices -notmatch "(?m)^\S+\s+device$") {
    Write-Host "`n[!] No authorized Android device detected." -ForegroundColor Yellow
    Write-Host "Please ensure:" -ForegroundColor Yellow
    Write-Host "  1. Phone is connected via USB." -ForegroundColor Yellow
    Write-Host "  2. USB debugging is enabled in Developer Options." -ForegroundColor Yellow
    Write-Host "  3. Screen is unlocked and 'Allow USB debugging' prompt is accepted.`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[1/4] Setting up ADB reverse port forwarding (Backend & Metro)..." -ForegroundColor Green
& $adb reverse tcp:8000 tcp:8000
& $adb reverse tcp:8081 tcp:8081
& $adb reverse tcp:8082 tcp:8082
Write-Host "  -> Port 8000 (Backend), 8081 (Passenger Metro), 8082 (Driver Metro) forwarded."

Write-Host "`n[2/4] Installing VIRGO Passenger App..." -ForegroundColor Green
$passengerApk = "passenger-app/android/app/build/outputs/apk/debug/app-debug.apk"
if (Test-Path $passengerApk) {
    & $adb install -r $passengerApk
    Write-Host "  -> Passenger App installed successfully." -ForegroundColor Green
} else {
    Write-Host "  [!] Passenger APK not found at $passengerApk" -ForegroundColor Red
}

Write-Host "`n[3/4] Installing VIRGO Driver App..." -ForegroundColor Green
$driverApk = "driver-app/android/app/build/outputs/apk/debug/app-debug.apk"
if (Test-Path $driverApk) {
    & $adb install -r $driverApk
    Write-Host "  -> Driver App installed successfully." -ForegroundColor Green
} else {
    Write-Host "  [!] Driver APK not found at $driverApk" -ForegroundColor Red
}

Write-Host "`n[4/4] Installation Complete!" -ForegroundColor Magenta
Write-Host "You can now test the apps on your phone with:" -ForegroundColor Cyan
Write-Host "  Passenger: +919876543210 (Password: TestPassenger@123)" -ForegroundColor White
Write-Host "  Driver:    +919876543220 (Vehicle: MN01AB1234)`n" -ForegroundColor White

