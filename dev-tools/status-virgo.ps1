# status-virgo.ps1 - Health and diagnostics dashboard for VIRGO development environment
[CmdletBinding()]
param(
    [string]$TabletSerial = "R52X90A40LV",
    [switch]$Detailed
)

# Dot-source shared helpers
$CommonScript = Join-Path $PSScriptRoot "scripts\virgo-common.ps1"
if (-not (Test-Path $CommonScript)) {
    Write-Host "[FATAL] Missing virgo-common.ps1 at $CommonScript" -ForegroundColor Red
    exit 1
}
. $CommonScript

Ensure-EnvironmentVariables

$timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")

Clear-Host
Write-Host "==========================================================================" -ForegroundColor Magenta
Write-Host " VIRGO DEVELOPMENT ENVIRONMENT - STATUS DASHBOARD" -ForegroundColor Magenta
Write-Host " Timestamp: $timestamp" -ForegroundColor DarkGray
Write-Host "==========================================================================" -ForegroundColor Magenta

# SECTION 1: SERVICES STATUS
Write-Host "`n--- SERVICES HEALTH & PORTS ----------------------------------------------" -ForegroundColor Cyan

foreach ($key in @("backend", "passenger", "driver")) {
    $svc = $script:ServicesCatalog[$key]
    $listener = Get-PortListener -Port $svc.Port
    $record = Get-ManagedServiceRecord -ServiceKey $key
    $health = Test-ServiceHealth -ServiceKey $key -TimeoutSec 3

    $statusLabel = "STOPPED"
    $statusColor = "Red"
    $icon = "[X]"

    if ($health.IsHealthy) {
        $statusLabel = "HEALTHY"
        $statusColor = "Green"
        $icon = "[OK]"
    } elseif ($listener.IsListening) {
        $statusLabel = "UNHEALTHY (Port occupied, health check failed)"
        $statusColor = "Yellow"
        $icon = "[!]"
    }

    Write-Host "$icon " -NoNewline -ForegroundColor $statusColor
    Write-Host "$($svc.DisplayName) (Port $($svc.Port))" -ForegroundColor White
    Write-Host "     Health:       " -NoNewline -ForegroundColor DarkGray
    Write-Host "$statusLabel" -ForegroundColor $statusColor
    Write-Host "     Endpoint:     $($svc.HealthUrl)" -ForegroundColor DarkGray

    if ($health.IsHealthy) {
        Write-Host "     Response:     " -NoNewline -ForegroundColor DarkGray
        Write-Host "$($health.Response)" -ForegroundColor Green
    } elseif ($health.Error) {
        Write-Host "     Error:        " -NoNewline -ForegroundColor DarkGray
        Write-Host "$($health.Error)" -ForegroundColor Yellow
    }

    if ($listener.IsListening) {
        $procInfo = "PID: $($listener.Pid) ($($listener.ProcessName))"
        if ($record -and $record.managed_by) {
            $procInfo += " [Managed by Launcher, Window PID: $($record.window_pid)]"
        } else {
            $procInfo += " [External / Unmanaged]"
        }
        Write-Host "     Process:      $procInfo" -ForegroundColor DarkGray
    } else {
        Write-Host "     Process:      Not running on port $($svc.Port)" -ForegroundColor DarkGray
    }

    if (Test-Path $svc.LogFile) {
        $logSize = [math]::Round(((Get-Item $svc.LogFile).Length / 1KB), 1)
        Write-Host "     Log File:     $($svc.LogFile) (${logSize} KB)" -ForegroundColor DarkGray
    } else {
        Write-Host "     Log File:     $($svc.LogFile) (No log yet)" -ForegroundColor DarkGray
    }
    Write-Host ""
}

# SECTION 2: HARDWARE & ADB STATUS
Write-Host "--- SAMSUNG TABLET & ADB FORWARDING -------------------------------------" -ForegroundColor Cyan
$tablet = Get-AdbDeviceStatus -Serial $TabletSerial

if (-not $tablet.Installed) {
    Write-Host "[X] ADB Not Installed" -ForegroundColor Red
    Write-Host "    $($tablet.Message)" -ForegroundColor DarkGray
} elseif ($tablet.Connected) {
    Write-Host "[OK] Samsung Galaxy Tab ($TabletSerial) Connected & Authorized" -ForegroundColor Green

    # Inspect reverse mappings
    $revList = & $script:AdbExe -s $TabletSerial reverse --list 2>$null
    Write-Host "     ADB Reverse Port Mappings:" -ForegroundColor DarkGray

    foreach ($p in @(8000, 8081, 8082)) {
        $target = switch ($p) { 8000 { "FastAPI Backend" } 8081 { "Passenger Metro" } 8082 { "Driver Metro" } }
        if ($revList -match "tcp:$p\s+tcp:$p") {
            Write-Host "       [+] tcp:$p => tcp:$p ($target)" -ForegroundColor Green
        } else {
            Write-Host "       [-] tcp:$p => tcp:$p (MISSING - run start-virgo.ps1 to restore)" -ForegroundColor Yellow
        }
    }
} elseif ($tablet.Status -eq "UNAUTHORIZED") {
    Write-Host "[!] Samsung Galaxy Tab ($TabletSerial) Unauthorized" -ForegroundColor Yellow
    Write-Host "    $($tablet.Message)" -ForegroundColor Yellow
} else {
    Write-Host "[-] Samsung Galaxy Tab ($TabletSerial) Not Connected" -ForegroundColor DarkGray
    Write-Host "    Connect tablet via USB with USB Debugging enabled." -ForegroundColor DarkGray
}

# SECTION 3: QUICK COMMAND CHEATSHEET
Write-Host "`n--- MANAGEMENT COMMANDS -------------------------------------------------" -ForegroundColor Cyan
Write-Host "  Start all missing:       .\start-virgo.ps1" -ForegroundColor White
Write-Host "  Restart single service:  .\restart-virgo-service.ps1 -Service <Backend|Passenger|Driver>" -ForegroundColor White
Write-Host "  Stop managed services:   .\stop-virgo.ps1" -ForegroundColor White
Write-Host "==========================================================================" -ForegroundColor Magenta

