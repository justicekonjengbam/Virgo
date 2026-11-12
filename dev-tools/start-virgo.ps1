# start-virgo.ps1 - One-command development launcher for VIRGO
# Starts Backend (8000), Passenger Metro (8081), and Driver Metro (8082) in visible console windows.

[CmdletBinding()]
param(
    [int]$TimeoutSec = 35,
    [string]$TabletSerial = "R52X90A40LV"
)

# Dot-source shared helpers
$CommonScript = Join-Path $PSScriptRoot "scripts\virgo-common.ps1"
if (-not (Test-Path $CommonScript)) {
    Write-Host "[FATAL] Missing virgo-common.ps1 at $CommonScript" -ForegroundColor Red
    exit 1
}
. $CommonScript

Ensure-EnvironmentVariables

Clear-Host
Write-Host "==========================================================================" -ForegroundColor Magenta
Write-Host " VIRGO - ONE-COMMAND DEVELOPMENT LAUNCHER" -ForegroundColor Magenta
Write-Host "==========================================================================" -ForegroundColor Magenta
Write-LauncherLog "Starting VIRGO Development Environment initialization..." "INFO"

# Step 1: Preflight Tool & Directory Verifications
Write-Host "`n[1/5] Verifying Project & Dependencies..." -ForegroundColor Cyan

$preflightFailed = $false

# 1a. Check Project Directories
if (-not (Test-Path $script:BackendDir) -or -not (Test-Path $script:PassengerDir) -or -not (Test-Path $script:DriverDir)) {
    Write-LauncherLog "Missing one or more required project directories (backend, passenger-app, driver-app)." "ERROR"
    $preflightFailed = $true
} else {
    Write-LauncherLog "  -> Core project directories located." "SUCCESS"
}

# 1b. Check Python & Uvicorn
if (-not (Test-Path $script:PythonExe)) {
    Write-LauncherLog "  -> Python virtual environment missing at $script:PythonExe" "ERROR"
    $preflightFailed = $true
} else {
    $pyVer = & $script:PythonExe --version 2>&1
    Write-LauncherLog "  -> Python virtualenv verified: $pyVer" "SUCCESS"
}

# 1c. Check Node.js and npm
$nodeCmd = Get-Command node.exe -ErrorAction SilentlyContinue
$npmCmd  = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Write-LauncherLog "  -> Node.js executable (node.exe) not found on PATH." "ERROR"
    $preflightFailed = $true
} else {
    $nodeVer = & node.exe --version
    Write-LauncherLog "  -> Node.js verified: $nodeVer" "SUCCESS"
}

if (-not $npmCmd) {
    Write-LauncherLog "  -> npm not found on PATH." "WARN"
}

# 1d. Check Java JDK
if (Test-Path $script:AdoptiumJavaHome) {
    Write-LauncherLog "  -> Eclipse Adoptium JDK 17 verified at $script:AdoptiumJavaHome" "SUCCESS"
} elseif ($env:JAVA_HOME -and (Test-Path $env:JAVA_HOME)) {
    Write-LauncherLog "  -> JAVA_HOME verified at $env:JAVA_HOME" "SUCCESS"
} else {
    Write-LauncherLog "  -> JDK 17 not detected at expected path ($script:AdoptiumJavaHome)." "WARN"
}

# 1e. Check ADB
if (Test-Path $script:AdbExe) {
    Write-LauncherLog "  -> ADB verified at $script:AdbExe" "SUCCESS"
} else {
    Write-LauncherLog "  -> ADB missing at $script:AdbExe. Android tablet connectivity will not work." "WARN"
}

if ($preflightFailed) {
    Write-LauncherLog "Preflight verification failed. Correct the errors above and re-run start-virgo.ps1." "ERROR"
    exit 1
}

# Step 2: Check Existing Service States
Write-Host "`n[2/5] Evaluating Existing Services..." -ForegroundColor Cyan

$servicesToStart = @()

foreach ($key in @("backend", "passenger", "driver")) {
    $svc = $script:ServicesCatalog[$key]
    $listener = Get-PortListener -Port $svc.Port
    $record = Get-ManagedServiceRecord -ServiceKey $key

    if ($listener.IsListening) {
        $health = Test-ServiceHealth -ServiceKey $key -TimeoutSec 3
        if ($health.IsHealthy) {
            Write-LauncherLog "  -> [$($svc.DisplayName)] is ALREADY running and healthy on port $($svc.Port) (PID: $($listener.Pid)). Keeping existing process." "SUCCESS"
        } else {
            Write-LauncherLog "  -> [$($svc.DisplayName)] is occupying port $($svc.Port) (PID: $($listener.Pid)), but failing health check. Will restart." "WARN"
            $servicesToStart += $key
        }
    } else {
        Write-LauncherLog "  -> [$($svc.DisplayName)] is not running on port $($svc.Port). Will start." "INFO"
        $servicesToStart += $key
    }
}

# Step 3: Launch Services in Visible PowerShell Windows
Write-Host "`n[3/5] Starting Missing / Unhealthy Services..." -ForegroundColor Cyan

if ($servicesToStart.Count -eq 0) {
    Write-LauncherLog "All services (Backend, Passenger, Driver) are already running and healthy!" "SUCCESS"
} else {
    foreach ($key in $servicesToStart) {
        $svc = $script:ServicesCatalog[$key]
        $started = Start-ManagedService -ServiceKey $key -StartupTimeoutSec $TimeoutSec
        if (-not $started) {
            Write-LauncherLog "Warning: [$($svc.DisplayName)] could not be started or did not pass health check." "WARN"
        }
    }
}

# Step 4: Configure Samsung Tablet (ADB)
Write-Host "`n[4/5] Checking Samsung Tablet & Reverse Port Forwarding..." -ForegroundColor Cyan
$tablet = Get-AdbDeviceStatus -Serial $TabletSerial

if ($tablet.Connected) {
    Write-LauncherLog "  -> Connected to Samsung Tablet ($TabletSerial)." "SUCCESS"
    $revSuccess = Setup-AdbReverseMappings -Serial $TabletSerial
    if ($revSuccess) {
        Write-LauncherLog "  -> ADB reverse port forwarding (8000, 8081, 8082) active." "SUCCESS"
    } else {
        Write-LauncherLog "  -> One or more reverse port forwarding rules could not be set." "WARN"
    }
} elseif ($tablet.Status -eq "UNAUTHORIZED") {
    Write-LauncherLog "  -> Tablet ($TabletSerial) is connected but unauthorized. Unlock screen and accept USB prompt." "WARN"
} else {
    Write-LauncherLog "  -> Tablet ($TabletSerial) is not connected. (Continuing launcher without tablet forwarding)." "WARN"
    Write-Host "     Connect the Samsung tablet via USB anytime and run:" -ForegroundColor Yellow
    Write-Host "     & '$script:AdbExe' -s $TabletSerial reverse tcp:8000 tcp:8000; ... tcp:8081 ... tcp:8082" -ForegroundColor Yellow
}

# Step 5: Final Status Summary
Write-Host "`n[5/5] Final Readiness Verification..." -ForegroundColor Cyan

$allHealthy = $true
foreach ($key in @("backend", "passenger", "driver")) {
    $svc = $script:ServicesCatalog[$key]
    $h = Test-ServiceHealth -ServiceKey $key -TimeoutSec 2
    if ($h.IsHealthy) {
        Write-Host ("  [HEALTHY] {0,-18} Port {1,-5} ({2})" -f $svc.DisplayName, $svc.Port, $svc.HealthUrl) -ForegroundColor Green
    } else {
        Write-Host ("  [OFFLINE] {0,-18} Port {1,-5} ({2})" -f $svc.DisplayName, $svc.Port, $h.Error) -ForegroundColor Red
        $allHealthy = $false
    }
}

Write-Host "`n==========================================================================" -ForegroundColor Magenta
if ($allHealthy) {
    Write-Host " VIRGO DEVELOPMENT ENVIRONMENT IS FULLY OPERATIONAL!" -ForegroundColor Green
    Write-Host " - Backend API:        http://127.0.0.1:8000/docs" -ForegroundColor White
    Write-Host " - Passenger Metro:    http://127.0.0.1:8081" -ForegroundColor White
    Write-Host " - Driver Metro:       http://127.0.0.1:8082" -ForegroundColor White
    Write-Host " - Logs Directory:     $script:LogsDir" -ForegroundColor White
    Write-Host "`n Tip: Run .\status-virgo.ps1 anytime to inspect system health." -ForegroundColor Cyan
} else {
    Write-Host " VIRGO STARTED WITH WARNINGS - Check the offline services above." -ForegroundColor Yellow
    Write-Host " View detailed logs in: $script:LogsDir" -ForegroundColor Yellow
}
Write-Host "==========================================================================" -ForegroundColor Magenta

