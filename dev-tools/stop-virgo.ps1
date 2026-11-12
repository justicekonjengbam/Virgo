# stop-virgo.ps1 - Safely stops managed VIRGO services without terminating unrelated processes.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [ValidateSet("All", "Backend", "Passenger", "Driver", "all", "backend", "passenger", "driver")]
    [string]$Service = "All"
)

# Dot-source shared helpers
$CommonScript = Join-Path $PSScriptRoot "scripts\virgo-common.ps1"
if (-not (Test-Path $CommonScript)) {
    Write-Host "[FATAL] Missing virgo-common.ps1 at $CommonScript" -ForegroundColor Red
    exit 1
}
. $CommonScript

Ensure-EnvironmentVariables

Write-Host "==========================================================================" -ForegroundColor Magenta
Write-Host " VIRGO DEVELOPMENT ENVIRONMENT - SAFE SHUTDOWN" -ForegroundColor Magenta
Write-Host "==========================================================================" -ForegroundColor Magenta

$targetKeys = @()
if ($Service.ToLowerInvariant() -eq "all") {
    $targetKeys = @("backend", "passenger", "driver")
    Write-LauncherLog "Stopping all managed VIRGO services..." "INFO"
} else {
    $targetKeys = @($Service.ToLowerInvariant())
    Write-LauncherLog "Stopping single service: $Service..." "INFO"
}

$stoppedCount = 0
$skippedCount = 0

foreach ($key in $targetKeys) {
    $svc = $script:ServicesCatalog[$key]
    $record = Get-ManagedServiceRecord -ServiceKey $key
    $listener = Get-PortListener -Port $svc.Port

    if (-not $listener.IsListening -and -not $record) {
        Write-LauncherLog "  -> [$($svc.DisplayName)] is not running." "INFO"
        continue
    }

    if (-not $record -and $listener.IsListening) {
        Write-LauncherLog "  -> [$($svc.DisplayName)] on port $($svc.Port) (PID: $($listener.Pid)) was NOT started by this launcher. SKIPPING." "WARN"
        $skippedCount++
        continue
    }

    $res = Stop-ManagedService -ServiceKey $key
    if ($res) {
        $stoppedCount++
    }
}

Write-Host "`n==========================================================================" -ForegroundColor Magenta
Write-Host " SHUTDOWN COMPLETE" -ForegroundColor Green
Write-Host " Managed services stopped: $stoppedCount" -ForegroundColor White
if ($skippedCount -gt 0) {
    Write-Host " Unmanaged external processes protected/skipped: $skippedCount" -ForegroundColor Yellow
}
Write-Host "==========================================================================" -ForegroundColor Magenta

