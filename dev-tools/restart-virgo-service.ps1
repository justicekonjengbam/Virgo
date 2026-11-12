# restart-virgo-service.ps1 - Restarts a single VIRGO service without interrupting others.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("Backend", "Passenger", "Driver", "backend", "passenger", "driver")]
    [string]$Service,

    [int]$TimeoutSec = 35
)

# Dot-source shared helpers
$CommonScript = Join-Path $PSScriptRoot "scripts\virgo-common.ps1"
if (-not (Test-Path $CommonScript)) {
    Write-Host "[FATAL] Missing virgo-common.ps1 at $CommonScript" -ForegroundColor Red
    exit 1
}
. $CommonScript

Ensure-EnvironmentVariables

$svcKey = $Service.ToLowerInvariant()
$svc = $script:ServicesCatalog[$svcKey]

if (-not $svc) {
    Write-Host "Unknown service: $Service. Choose from Backend, Passenger, Driver." -ForegroundColor Red
    exit 1
}

Write-Host "==========================================================================" -ForegroundColor Magenta
Write-Host " VIRGO SERVICE RESTART: $($svc.DisplayName)" -ForegroundColor Magenta
Write-Host "==========================================================================" -ForegroundColor Magenta

Write-LauncherLog "Initiating targeted restart for [$($svc.DisplayName)] on Port $($svc.Port)..." "INFO"

# Step 1: Stop ONLY the requested service (allows taking over an existing listener on this port)
$stopped = Stop-ManagedService -ServiceKey $svcKey -ForceUnmanaged
if (-not $stopped) {
    # Check if port is still occupied
    $chk = Get-PortListener -Port $svc.Port
    if ($chk.IsListening) {
        Write-LauncherLog "Cannot restart [$($svc.DisplayName)]: port $($svc.Port) is occupied by PID $($chk.Pid) which could not be safely stopped." "ERROR"
        exit 1
    }
}

# Step 2: Start ONLY the requested service
Write-Host ""
$started = Start-ManagedService -ServiceKey $svcKey -StartupTimeoutSec $TimeoutSec

if ($started) {
    Write-Host "`n==========================================================================" -ForegroundColor Magenta
    Write-Host " [$($svc.DisplayName)] RESTARTED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host " Other VIRGO services were not disturbed." -ForegroundColor Cyan
    Write-Host "==========================================================================" -ForegroundColor Magenta
} else {
    Write-Host "`n==========================================================================" -ForegroundColor Magenta
    Write-Host " [$($svc.DisplayName)] RESTART FAILED OR TIMED OUT!" -ForegroundColor Red
    Write-Host " Check the log file: $($svc.LogFile)" -ForegroundColor Yellow
    Write-Host "==========================================================================" -ForegroundColor Magenta
    exit 1
}
