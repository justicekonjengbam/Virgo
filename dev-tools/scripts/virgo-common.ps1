# virgo-common.ps1 - Shared helper functions and configurations for VIRGO dev-tools
# Ensures consistent behavior across Windows PowerShell 5.1 and PowerShell Core.

# Determine project roots
$script:DevToolsDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$script:ProjectRoot = (Resolve-Path (Join-Path $script:DevToolsDir "..")).Path
$script:BackendDir  = Join-Path $script:ProjectRoot "backend"
$script:PassengerDir = Join-Path $script:ProjectRoot "passenger-app"
$script:DriverDir    = Join-Path $script:ProjectRoot "driver-app"
$script:LogsDir      = Join-Path $script:DevToolsDir "logs"
$script:PidsDir      = Join-Path $script:DevToolsDir "pids"

# Ensure runtime directories exist
if (-not (Test-Path $script:LogsDir)) { New-Item -ItemType Directory -Path $script:LogsDir -Force | Out-Null }
if (-not (Test-Path $script:PidsDir)) { New-Item -ItemType Directory -Path $script:PidsDir -Force | Out-Null }

# Known tool paths & settings
$script:PythonExe        = Join-Path $script:BackendDir ".venv\Scripts\python.exe"
$script:UvicornExe       = Join-Path $script:BackendDir ".venv\Scripts\uvicorn.exe"
$script:AdbExe           = "C:\platform-tools\adb.exe"
$script:AdbDeviceSerial  = "R52X90A40LV"
$script:AdoptiumJavaHome = "C:\Program Files\Eclipse Adoptium\jdk-17.0.21.9-hotspot"

# Service metadata catalog
$script:ServicesCatalog = @{
    backend = @{
        Key            = "backend"
        DisplayName    = "FastAPI Backend"
        Port           = 8000
        HealthUrl      = "http://127.0.0.1:8000/health"
        ExpectedStatus = "OK"
        Directory      = $script:BackendDir
        LogFile        = (Join-Path $script:LogsDir "backend.log")
        PidFile        = (Join-Path $script:PidsDir "backend.json")
        WindowTitle    = "VIRGO - Backend (Port 8000)"
        ProcessPattern = "python"
    }
    passenger = @{
        Key            = "passenger"
        DisplayName    = "Passenger Metro"
        Port           = 8081
        HealthUrl      = "http://127.0.0.1:8081/status"
        ExpectedStatus = "packager-status:running"
        Directory      = $script:PassengerDir
        LogFile        = (Join-Path $script:LogsDir "passenger-metro.log")
        PidFile        = (Join-Path $script:PidsDir "passenger-metro.json")
        WindowTitle    = "VIRGO - Passenger Metro (Port 8081)"
        ProcessPattern = "node"
    }
    driver = @{
        Key            = "driver"
        DisplayName    = "Driver Metro"
        Port           = 8082
        HealthUrl      = "http://127.0.0.1:8082/status"
        ExpectedStatus = "packager-status:running"
        Directory      = $script:DriverDir
        LogFile        = (Join-Path $script:LogsDir "driver-metro.log")
        PidFile        = (Join-Path $script:PidsDir "driver-metro.json")
        WindowTitle    = "VIRGO - Driver Metro (Port 8082)"
        ProcessPattern = "node"
    }
}

function Write-LauncherLog {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [ValidateSet("INFO", "SUCCESS", "WARN", "ERROR")][string]$Level = "INFO"
    )
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $logLine = "[$timestamp] [$Level] $Message"
    $launcherLog = Join-Path $script:LogsDir "launcher.log"
    Add-Content -Path $launcherLog -Value $logLine -ErrorAction SilentlyContinue

    switch ($Level) {
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        "WARN"    { Write-Host $Message -ForegroundColor Yellow }
        "ERROR"   { Write-Host $Message -ForegroundColor Red }
        Default   { Write-Host $Message -ForegroundColor Cyan }
    }
}

function Rotate-LogFile {
    param(
        [Parameter(Mandatory = $true)][string]$LogPath,
        [long]$MaxSizeBytes = 5242880 # 5 MB
    )
    if (Test-Path $LogPath) {
        try {
            $file = Get-Item $LogPath
            if ($file.Length -gt $MaxSizeBytes) {
                $backupPath = "$LogPath.old"
                if (Test-Path $backupPath) {
                    Remove-Item -Path $backupPath -Force -ErrorAction SilentlyContinue
                }
                Rename-Item -Path $LogPath -NewName (Split-Path $backupPath -Leaf) -Force -ErrorAction SilentlyContinue
            }
        } catch {
            # Non-critical if file is currently open
        }
    }
}

function Ensure-EnvironmentVariables {
    # Ensure Java JDK is in environment
    if (-not $env:JAVA_HOME -and (Test-Path $script:AdoptiumJavaHome)) {
        $env:JAVA_HOME = $script:AdoptiumJavaHome
        if ($env:PATH -notmatch [regex]::Escape($script:AdoptiumJavaHome)) {
            $env:PATH = "$script:AdoptiumJavaHome\bin;$env:PATH"
        }
    }
    # Ensure platform-tools (ADB) is on PATH
    $adbDir = Split-Path $script:AdbExe -Parent
    if ((Test-Path $adbDir) -and ($env:PATH -notmatch [regex]::Escape($adbDir))) {
        $env:PATH = "$adbDir;$env:PATH"
    }
}

function Get-PortListener {
    param([Parameter(Mandatory = $true)][int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($conn) {
        $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        return @{
            IsListening   = $true
            Pid           = $conn.OwningProcess
            ProcessName   = if ($proc) { $proc.ProcessName } else { "Unknown" }
            ProcessObject = $proc
        }
    }
    return @{
        IsListening   = $false
        Pid           = $null
        ProcessName   = $null
        ProcessObject = $null
    }
}

function Test-ServiceHealth {
    param(
        [Parameter(Mandatory = $true)][string]$ServiceKey,
        [int]$TimeoutSec = 3
    )
    $svc = $script:ServicesCatalog[$ServiceKey.ToLowerInvariant()]
    if (-not $svc) {
        return @{ IsHealthy = $false; StatusCode = $null; Response = $null; Error = "Unknown service $ServiceKey" }
    }

    try {
        # Always use -UseBasicParsing to prevent IE engine hangs on Windows PowerShell 5.1
        $resp = Invoke-WebRequest -Uri $svc.HealthUrl -UseBasicParsing -TimeoutSec $TimeoutSec -ErrorAction Stop
        
        $rawContent = $resp.Content
        if ($rawContent -is [byte[]]) {
            $content = [System.Text.Encoding]::UTF8.GetString($rawContent)
        } else {
            $content = [string]$rawContent
        }

        $isExpected = $false
        if ($svc.Key -eq "backend") {
            # Backend returns JSON with status "OK"
            if ($resp.StatusCode -eq 200 -and $content -match '"status"\s*:\s*"OK"') {
                $isExpected = $true
            }
        } else {
            # Metro returns text containing "packager-status:running"
            if ($resp.StatusCode -eq 200 -and $content -match "packager-status:running") {
                $isExpected = $true
            }
        }

        return @{
            IsHealthy   = $isExpected
            StatusCode  = $resp.StatusCode
            Response    = $content.Trim()
            Error       = if ($isExpected) { $null } else { "Unexpected response: $content" }
        }
    } catch {
        return @{
            IsHealthy   = $false
            StatusCode  = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { $null }
            Response    = $null
            Error       = $_.Exception.Message
        }
    }
}

function Get-ManagedServiceRecord {
    param([Parameter(Mandatory = $true)][string]$ServiceKey)
    $svc = $script:ServicesCatalog[$ServiceKey.ToLowerInvariant()]
    if ($svc -and (Test-Path $svc.PidFile)) {
        try {
            $raw = Get-Content -Path $svc.PidFile -Raw -ErrorAction Stop
            $record = ($raw | ConvertFrom-Json)
            # Prune stale records if neither window nor listening port is active
            $listener = Get-PortListener -Port $svc.Port
            $winProc = if ($record.window_pid) { Get-Process -Id $record.window_pid -ErrorAction SilentlyContinue } else { $null }
            if (-not $listener.IsListening -and -not $winProc) {
                Remove-Item -Path $svc.PidFile -Force -ErrorAction SilentlyContinue
                return $null
            }
            return $record
        } catch {
            return $null
        }
    }
    return $null
}

function Save-ManagedServiceRecord {
    param(
        [Parameter(Mandatory = $true)][string]$ServiceKey,
        [Parameter(Mandatory = $true)][hashtable]$Data
    )
    $svc = $script:ServicesCatalog[$ServiceKey.ToLowerInvariant()]
    if ($svc) {
        $json = $Data | ConvertTo-Json -Compress
        Set-Content -Path $svc.PidFile -Value $json -Force
    }
}

function Remove-ManagedServiceRecord {
    param([Parameter(Mandatory = $true)][string]$ServiceKey)
    $svc = $script:ServicesCatalog[$ServiceKey.ToLowerInvariant()]
    if ($svc -and (Test-Path $svc.PidFile)) {
        Remove-Item -Path $svc.PidFile -Force -ErrorAction SilentlyContinue
    }
}

function Stop-ManagedService {
    param(
        [Parameter(Mandatory = $true)][string]$ServiceKey,
        [switch]$ForceUnmanaged
    )
    $svc = $script:ServicesCatalog[$ServiceKey.ToLowerInvariant()]
    if (-not $svc) {
        Write-LauncherLog "Unknown service key '$ServiceKey'." "ERROR"
        return $false
    }

    $listener = Get-PortListener -Port $svc.Port
    $record = Get-ManagedServiceRecord -ServiceKey $svc.Key

    if (-not $record -and -not $listener.IsListening) {
        Write-LauncherLog "[$($svc.DisplayName)] is already stopped." "INFO"
        return $true
    }

    if (-not $record -and $listener.IsListening -and -not $ForceUnmanaged) {
        Write-LauncherLog "[$($svc.DisplayName)] Port $($svc.Port) is occupied by PID $($listener.Pid) ($($listener.ProcessName)), but it was NOT launched by this development manager. Skipping to protect external processes." "WARN"
        return $false
    }

    Write-LauncherLog "Stopping [$($svc.DisplayName)]..." "INFO"
    $stopped = $false

    # 1. Terminate spawned PowerShell window tree if recorded
    if ($record -and $record.window_pid) {
        $winProc = Get-Process -Id $record.window_pid -ErrorAction SilentlyContinue
        if ($winProc -and $winProc.ProcessName -match "powershell|pwsh") {
            # Use taskkill to cleanly eliminate the window process tree
            & taskkill.exe /PID $record.window_pid /T /F 2>&1 | Out-Null
            $stopped = $true
        }
    }

    # 2. Terminate listening process if it matches tracked listening PID or expected process name
    $currentListener = Get-PortListener -Port $svc.Port
    if ($currentListener.IsListening) {
        $shouldKill = $false
        if ($record -and $record.listening_pid -and ($currentListener.Pid -eq $record.listening_pid)) {
            $shouldKill = $true
        } elseif ($ForceUnmanaged) {
            $shouldKill = $true
        } elseif ($currentListener.ProcessName -match $svc.ProcessPattern) {
            # Double safety: matches expected process pattern (python/node)
            $shouldKill = $true
        }

        if ($shouldKill) {
            & taskkill.exe /PID $currentListener.Pid /T /F 2>&1 | Out-Null
            $stopped = $true
        }
    }

    # Wait up to 5 seconds for port to clear
    $waitCount = 0
    while ($waitCount -lt 10) {
        $chk = Get-PortListener -Port $svc.Port
        if (-not $chk.IsListening) { break }
        Start-Sleep -Milliseconds 500
        $waitCount++
    }

    Remove-ManagedServiceRecord -ServiceKey $svc.Key
    $finalCheck = Get-PortListener -Port $svc.Port
    if (-not $finalCheck.IsListening) {
        Write-LauncherLog "[$($svc.DisplayName)] successfully stopped." "SUCCESS"
        return $true
    } else {
        Write-LauncherLog "[$($svc.DisplayName)] Port $($svc.Port) is still occupied by PID $($finalCheck.Pid)." "ERROR"
        return $false
    }
}

function Start-ManagedService {
    param(
        [Parameter(Mandatory = $true)][string]$ServiceKey,
        [int]$StartupTimeoutSec = 30
    )
    $svc = $script:ServicesCatalog[$ServiceKey.ToLowerInvariant()]
    if (-not $svc) {
        Write-LauncherLog "Unknown service key '$ServiceKey'." "ERROR"
        return $false
    }

    # Check if already running and healthy
    $listener = Get-PortListener -Port $svc.Port
    if ($listener.IsListening) {
        $health = Test-ServiceHealth -ServiceKey $svc.Key
        if ($health.IsHealthy) {
            Write-LauncherLog "[$($svc.DisplayName)] is already running and healthy on port $($svc.Port) (PID: $($listener.Pid)). Not starting duplicate." "SUCCESS"
            return $true
        } else {
            Write-LauncherLog "[$($svc.DisplayName)] Port $($svc.Port) is occupied by PID $($listener.Pid), but service is UNHEALTHY." "WARN"
            # If managed, stop it first
            $record = Get-ManagedServiceRecord -ServiceKey $svc.Key
            if ($record) {
                Write-LauncherLog "Restarting managed unhealthy instance..." "INFO"
                Stop-ManagedService -ServiceKey $svc.Key | Out-Null
            } else {
                Write-LauncherLog "Port $($svc.Port) belongs to an unmanaged process. Please free port $($svc.Port) or restart that process manually." "ERROR"
                return $false
            }
        }
    }

    # Rotate log if needed
    Rotate-LogFile -LogPath $svc.LogFile

    # Build launch command for visible PowerShell window
    $logPath = $svc.LogFile
    $title   = $svc.WindowTitle
    $dir     = $svc.Directory

    $commandBody = ""
    switch ($svc.Key) {
        "backend" {
            $py = $script:PythonExe
            $commandBody = "cd '$dir'; `$Host.UI.RawUI.WindowTitle = '$title'; `$env:PYTHONUNBUFFERED = '1'; Write-Host 'Starting VIRGO FastAPI Backend...' -ForegroundColor Cyan; & '$py' -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
        }
        "passenger" {
            $commandBody = "cd '$dir'; `$Host.UI.RawUI.WindowTitle = '$title'; Write-Host 'Starting VIRGO Passenger Metro...' -ForegroundColor Cyan; npx.cmd react-native start --port 8081 *>&1 | Tee-Object -FilePath '$logPath' -Append"
        }
        "driver" {
            $commandBody = "cd '$dir'; `$Host.UI.RawUI.WindowTitle = '$title'; Write-Host 'Starting VIRGO Driver Metro...' -ForegroundColor Cyan; npx.cmd react-native start --port 8082 *>&1 | Tee-Object -FilePath '$logPath' -Append"
        }
    }

    Write-LauncherLog "Launching [$($svc.DisplayName)] in a new visible console window..." "INFO"

    $proc = Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $commandBody -PassThru

    if (-not $proc) {
        Write-LauncherLog "Failed to spawn PowerShell process for [$($svc.DisplayName)]." "ERROR"
        return $false
    }

    # Record initial window state
    $stateData = @{
        service       = $svc.Key
        display_name  = $svc.DisplayName
        port          = $svc.Port
        window_pid    = $proc.Id
        listening_pid = $null
        started_at    = (Get-Date).ToString("o")
        managed_by    = "virgo-dev-manager"
        log_file      = $svc.LogFile
    }
    Save-ManagedServiceRecord -ServiceKey $svc.Key -Data $stateData

    # Bounded polling for health
    Write-LauncherLog "Waiting for [$($svc.DisplayName)] to respond at $($svc.HealthUrl) (max ${StartupTimeoutSec}s)..." "INFO"
    $elapsed = 0
    $isReady = $false

    while ($elapsed -lt $StartupTimeoutSec) {
        Start-Sleep -Seconds 2
        $elapsed += 2

        $health = Test-ServiceHealth -ServiceKey $svc.Key -TimeoutSec 2
        if ($health.IsHealthy) {
            $isReady = $true
            break
        }
    }

    if ($isReady) {
        # Update listening PID in state
        $activeListener = Get-PortListener -Port $svc.Port
        if ($activeListener.IsListening) {
            $stateData.listening_pid = $activeListener.Pid
            Save-ManagedServiceRecord -ServiceKey $svc.Key -Data $stateData
        }
        Write-LauncherLog "[$($svc.DisplayName)] is READY and HEALTHY on port $($svc.Port)! (PID: $($activeListener.Pid))" "SUCCESS"
        return $true
    } else {
        Write-LauncherLog "[$($svc.DisplayName)] did not become healthy within ${StartupTimeoutSec}s." "ERROR"
        if (Test-Path $svc.LogFile) {
            Write-LauncherLog "--- Recent entries from $($svc.LogFile) ---" "WARN"
            Get-Content -Path $svc.LogFile -Tail 10 -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
        }
        return $false
    }
}

function Get-AdbDeviceStatus {
    param([string]$Serial = $script:AdbDeviceSerial)
    if (-not (Test-Path $script:AdbExe)) {
        return @{
            Installed = $false
            Connected = $false
            Status    = "ADB_NOT_FOUND"
            Message   = "ADB executable not found at $script:AdbExe"
        }
    }

    try {
        $raw = & $script:AdbExe devices 2>$null
        $lines = $raw -split "`r?`n" | Where-Object { $_ -match "\S" }

        $found = $false
        $status = "DISCONNECTED"

        foreach ($line in $lines) {
            if ($line -match "^($Serial)\s+(\w+)") {
                $found = $true
                $rawState = $Matches[2].ToLowerInvariant()
                if ($rawState -eq "device") {
                    $status = "CONNECTED"
                } elseif ($rawState -eq "unauthorized") {
                    $status = "UNAUTHORIZED"
                } else {
                    $status = $rawState.ToUpperInvariant()
                }
                break
            }
        }

        return @{
            Installed = $true
            Connected = ($status -eq "CONNECTED")
            Status    = $status
            Message   = switch ($status) {
                "CONNECTED"    { "Samsung Tablet ($Serial) is connected and authorized." }
                "UNAUTHORIZED" { "Samsung Tablet ($Serial) is connected but unauthorized. Unlock screen and accept 'Allow USB debugging'." }
                Default        { "Samsung Tablet ($Serial) is not detected on USB." }
            }
        }
    } catch {
        return @{
            Installed = $true
            Connected = $false
            Status    = "ERROR"
            Message   = $_.Exception.Message
        }
    }
}

function Setup-AdbReverseMappings {
    param([string]$Serial = $script:AdbDeviceSerial)
    $dev = Get-AdbDeviceStatus -Serial $Serial
    if (-not $dev.Connected) {
        Write-LauncherLog "Tablet not ready: $($dev.Message)" "WARN"
        return $false
    }

    Write-LauncherLog "Configuring ADB reverse port forwarding for $Serial..." "INFO"
    $ports = @(8000, 8081, 8082)
    foreach ($p in $ports) {
        & $script:AdbExe -s $Serial reverse tcp:$p tcp:$p 2>&1 | Out-Null
    }

    # Verify reverse
    $revList = & $script:AdbExe -s $Serial reverse --list 2>$null
    $allOk = $true
    foreach ($p in $ports) {
        if ($revList -match "tcp:$p\s+tcp:$p") {
            Write-LauncherLog "  -> tcp:$p => tcp:$p (OK)" "SUCCESS"
        } else {
            Write-LauncherLog "  -> tcp:$p => tcp:$p (FAILED)" "WARN"
            $allOk = $false
        }
    }
    return $allOk
}
