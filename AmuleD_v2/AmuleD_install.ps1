<#
.SYNOPSIS
    AmuleD_v2 installer by Soror L.'.L.'.
    Creates a portable uv `.venv` with Python 3.12, prepares runtime directories,
    generates a default JSONC config only if missing, installs dependencies from
    requirements.txt, verifies critical imports, and writes logs\install.log.
    Idempotent: safe to re-run; never overwrites an existing config.

    O:\Work\Coding\Paradise_Lost_KAD_SA\AmuleD_v2\AmuleD_install.ps1
    Version: 0.2.0
    Author: Soror L.'.L.'.
    Updated: 2026-09-22

Patch Notes v0.2.0 (Soror L.'.L.'):
  [*] Restored the original authored ASCII welcome/menu style while keeping the new uv-based AmuleD_v2 behavior.
  [*] Preserved the established installer structure and detailed step logging.

Patch Notes v0.1.0 (Soror L.'.L'.):
  [+] Clean-room uv-based installer for AmuleD_v2 (Python ED2K/Kademlia client).
  [+] Replaces the legacy borrowed installer with AmuleD_v2-specific logic.
  [+] Idempotent: skips .venv creation if present, never overwrites config.
  [+] Creates portable runtime dirs: config, db, logs, tmp, incoming, temp, shared.
  [+] Writes install log to logs\install.log.
#>

# === Encoding ===
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# ==========================================
# AUTHORED WELCOME / MENU
# ==========================================
Write-Host " ===========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  ██▓        ██▓    ██▓        ██▓" -ForegroundColor Yellow
Write-Host " ▓██▒              ▓██▒" -ForegroundColor Yellow
Write-Host " ▒██░              ▒██░" -ForegroundColor Yellow
Write-Host " ▒██░              ▒██░" -ForegroundColor Yellow
Write-Host " ░██████▒ ██▓  ██▓ ░██████▒ ██▓  ██▓" -ForegroundColor Yellow
Write-Host " ░ ▒░▓  ░ ▒▓▒  ▒▓▒ ░ ▒░▓  ░ ▒▓▒  ▒▓▒" -ForegroundColor Yellow
Write-Host " ░ ░ ▒  ░ ░▒   ░▒  ░ ░ ▒  ░ ░▒   ░▒" -ForegroundColor Yellow
Write-Host "   ░ ░    ░    ░     ░ ░    ░    ░" -ForegroundColor Yellow
Write-Host "     ░  ░  ░    ░      ░  ░  ░    ░" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ===========================================" -ForegroundColor Green
Write-Host "    AmuleD_v2 by Soror L.'.L.'." -ForegroundColor Yellow
Write-Host "    AmuleD_v2 Installer v0.2.0" -ForegroundColor Green
Write-Host "    Python 3.12 Ready" -ForegroundColor Cyan
Write-Host ""

# === Execution Policy ===
Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"

# === Path Configuration ===
$ProjectRoot = $PSScriptRoot
$VenvPath    = Join-Path $ProjectRoot ".venv"
$VenvPython  = Join-Path $VenvPath "Scripts\python.exe"
$ConfigDir   = Join-Path $ProjectRoot "config"
$DbDir       = Join-Path $ProjectRoot "db"
$LogsDir     = Join-Path $ProjectRoot "logs"
$TmpDir      = Join-Path $ProjectRoot "tmp"
$IncomingDir = Join-Path $ProjectRoot "incoming"
$TempDir     = Join-Path $ProjectRoot "temp"
$SharedDir   = Join-Path $ProjectRoot "shared"
$ReqFile     = Join-Path $ProjectRoot "requirements.txt"
$ConfigFile  = Join-Path $ConfigDir "amuled.jsonc"
$LogFile     = Join-Path $LogsDir "install.log"
$PythonVersion = "3.12"

# === Runtime Directories ===
$RuntimeDirs = @($ConfigDir, $DbDir, $LogsDir, $TmpDir, $IncomingDir, $TempDir, $SharedDir)

# === Logging ===
function Write-Status {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] [$Level] $Message"
    $color = switch ($Level) {
        "ERROR"   { "Red" }
        "WARN"    { "Yellow" }
        "SUCCESS" { "Green" }
        "CYAN"    { "Cyan" }
        default   { "White" }
    }
    Write-Host "[$Level] $Message" -ForegroundColor $color
    if (Test-Path $LogsDir) {
        Add-Content -Path $LogFile -Value $line -Encoding UTF8
    }
}

# === Helper: Test Command ===
function Test-Command {
    param([string]$Cmd)
    return $null -ne (Get-Command $Cmd -ErrorAction SilentlyContinue)
}

# === Default Config Template ===
function Get-DefaultConfig {
    return @'
// AmuleD_v2 Configuration (JSONC)
// Version: 0.1.0
// Updated: 2026-09-22

{
  // Core daemon settings
  "daemon": {
    "pid_file": "db/amuled.pid",
    "log_level": "INFO"
  },

  // Network configuration
  "network": {
    "ed2k_tcp_port": 8089,
    "ed2k_udp_port": 8089,
    "kad_udp_port": 8089,
    "bind_address": "0.0.0.0",
    "max_connections": 200,
    "max_sources_per_file": 500,
    "connection_timeout": 30,
    "socket_buffer_size": 65536
  },

  // Kademlia bootstrap
  "kademlia": {
    "nodes_dat": "amule-daemon-config/nodes.dat",
    "bootstrap_nodes": [],
    "max_bucket_size": 20,
    "ping_timeout": 10,
    "publish_interval": 300
  },

  // ED2K server list
  "servers": {
    "server_met": "amule-daemon-config/server.met",
    "static_servers": "amule-daemon-config/staticservers.dat",
    "auto_update_server_met": false
  },

  // Sharing configuration
  "sharing": {
    "shared_dirs": [],
    "shared_files_json": "shared_files.json",
    "shareddir_dat": "amule-daemon-config/shareddir.dat",
    "incoming_dir": "incoming",
    "temp_dir": "temp",
    "max_upload_slots": 3,
    "upload_queue_size": 50,
    "upload_speed_limit": 0,
    "download_speed_limit": 0
  },

  // File paths
  "paths": {
    "config_dir": "config",
    "db_dir": "db",
    "logs_dir": "logs",
    "tmp_dir": "tmp",
    "incoming_dir": "incoming",
    "temp_dir": "temp",
    "shared_dir": "shared",
    "db_file": "db/amuled_state.db"
  },

  // IP filter
  "ipfilter": {
    "ipfilter_dat": "amule-daemon-config/ipfilter.dat",
    "ipfilter_static_dat": "amule-daemon-config/ipfilter_static.dat",
    "auto_update": false
  },

  // Security
  "security": {
    "enable_obfuscation": true,
    "enable_secure_ident": false,
    "cryptkey_file": "amule-daemon-config/cryptkey.dat"
  },

  // Search
  "search": {
    "default_search_type": "kad",
    "max_results": 500,
    "result_ttl": 300
  },

  // Download
  "download": {
    "chunk_size": 9728000,
    "block_size": 180224,
    "disk_space_reserve_mb": 100,
    "auto_retry_failed": true,
    "max_retries": 3
  },

  // NAT / UPnP
  "nat": {
    "enable_upnp": true,
    "enable_natpmp": true,
    "external_port_override": null
  },

  // GeoIP
  "geoip": {
    "geoip_dat": "amule-daemon-config/GeoIP.dat",
    "enabled": false
  }
}
'@
}

# === Main Install Process ===

# Step 0: Ensure logs directory exists for logging
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

Write-Status "========== AmuleD_v2 Installer ==========" "INFO"
Write-Status "Python target: $PythonVersion" "CYAN"
Write-Status "Project root: $ProjectRoot" "CYAN"

# Step 1: Check uv availability
Write-Status "[1/5] Checking uv availability..." "INFO"
if (-not (Test-Command "uv")) {
    Write-Status "ERROR: 'uv' not found on PATH. Install uv first:" "ERROR"
    Write-Status "  winget install uv  OR  irm https://astral.sh/uv/install.ps1 | iex" "ERROR"
    exit 1
}
$uvVersion = (uv --version 2>$null).Trim()
Write-Status "  Found uv: $uvVersion" "SUCCESS"

# Step 2: Create runtime directories
Write-Status "[2/5] Creating runtime directories..." "INFO"
foreach ($dir in $RuntimeDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Status "  Created: $dir" "INFO"
    }
}
Write-Status "  [+] All runtime directories ready" "SUCCESS"

# Step 3: Create config if missing
Write-Status "[3/5] Checking configuration..." "INFO"
if (-not (Test-Path $ConfigFile)) {
    if (Test-Path $ConfigDir) {
        $defaultConfig = Get-DefaultConfig
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($ConfigFile, $defaultConfig, $utf8NoBom)
        Write-Status "  [+] Created default config: $ConfigFile" "SUCCESS"
    } else {
        Write-Status "  [!] Config dir not found, skipping config creation" "WARN"
    }
} else {
    Write-Status "  Config already exists, leaving untouched: $ConfigFile" "INFO"
}

# Step 4: Create or verify .venv with Python 3.12
Write-Status "[4/5] Setting up Python $PythonVersion virtual environment..." "INFO"
if (-not (Test-Path $VenvPython)) {
    Write-Status "  Creating .venv with Python $PythonVersion via uv..." "INFO"
    Push-Location $ProjectRoot
    try {
        $env:UV_PROJECT_ENVIRONMENT = $VenvPath
        $result = uv venv $VenvPath --python $PythonVersion 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Status "ERROR: uv venv failed: $result" "ERROR"
            Pop-Location
            exit 1
        }
        Write-Status "  [+] .venv created at $VenvPath" "SUCCESS"
    } finally {
        Pop-Location
    }
} else {
    Write-Status "  .venv already exists, skipping creation" "INFO"
}

# Verify Python version
if (Test-Path $VenvPython) {
    $pyVersion = (& $VenvPython --version 2>$null).Trim()
    Write-Status "  Python in venv: $pyVersion" "CYAN"
    if ($pyVersion -notmatch "3\.12") {
        Write-Status "  [!] WARNING: Expected Python 3.12, got: $pyVersion" "WARN"
        Write-Status "  [!] Recommendation: remove $VenvPath and re-run installer." "WARN"
    }
} else {
    Write-Status "ERROR: Virtual environment python not found at $VenvPython" "ERROR"
    exit 1
}

# Step 5: Install dependencies from requirements.txt
Write-Status "[5/5] Installing dependencies..." "INFO"
if (Test-Path $ReqFile) {
    Push-Location $ProjectRoot
    try {
        $installResult = uv pip install --python $VenvPython -r $ReqFile --quiet 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Status "  [!] uv pip install completed with warnings/errors:" "WARN"
            Write-Status "  $installResult" "WARN"
        } else {
            Write-Status "  [+] Dependencies installed successfully" "SUCCESS"
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Status "  [!] requirements.txt not found at $ReqFile" "WARN"
}

# Verify critical imports
Write-Status "Verifying critical imports..." "INFO"
$CriticalModules = @("duckdb", "aiohttp", "cryptography", "prompt_toolkit", "rich", "json5")
$AllImportsOK = $true
foreach ($mod in $CriticalModules) {
    $checkResult = & $VenvPython -c "import $mod" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Status "  [+] $mod" "SUCCESS"
    } else {
        Write-Status "  [!] $mod NOT FOUND" "ERROR"
        $AllImportsOK = $false
    }
}

Write-Status "" "INFO"
if ($AllImportsOK) {
    Write-Status "========== Installation Complete ==========" "SUCCESS"
    Write-Status "  Config:  $ConfigFile" "INFO"
    Write-Status "  Venv:    $VenvPath" "INFO"
    Write-Status "  Log:     $LogFile" "INFO"
    Write-Status "Next: Run AmuleD_Run.ps1 to start the client." "INFO"
} else {
    Write-Status "========== Installation Completed with Warnings ==========" "WARN"
}

exit 0
