<#
.SYNOPSIS
    AmuleD_v2 launcher by Soror L.'.L.'.
    Activates the portable uv virtualenv and runs `python -m amuled_v2`
    with all remaining arguments forwarded. Supports `-NoPause` to skip
    the exit prompt and defaults to `--help` when no arguments are given.

    O:\Work\Coding\Paradise_Lost_KAD_SA\AmuleD_v2\AmuleD_Run.ps1
    Version: 1.0.0
    Author: Soror L.'.L.'.
    Updated: 2026-09-22

Patch Notes v1.0.0 (Soror L.'.L.'):
  [*] Restored the original authored ASCII welcome/menu style while keeping the new AmuleD_v2 launcher behavior.
  [*] Preserved clear environment checks, environment variables, argument forwarding, and -NoPause support.

Patch Notes v0.1.0 (Soror L.'.L'.):
  [+] Clean-room runner for AmuleD_v2 (Python ED2K/Kademlia client).
  [+] Replaces the legacy borrowed launcher with AmuleD_v2-specific logic.
  [+] Forwards all arguments to `python -m amuled_v2`.
  [+] Supports -NoPause flag to skip exit prompt.
  [+] Defaults to --help when no arguments provided.
  [+] Sets AMULED_ROOT, AMULED_CONFIG, AMULED_DB, AMULED_LOGS env vars.
#>

param(
    [switch]$NoPause,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"

$Host.UI.RawUI.WindowTitle = "AmuleD_v2 Launcher by Soror L.'.L.'."

# ==========================================
# AUTHORED WELCOME / MENU
# ==========================================
Write-Host @"

   ██▓        ██▓    ██▓        ██▓
  ▓██▒              ▓██▒
  ▒██░              ▒██░
  ▒██░              ▒██░
  ░██████▒ ██▓  ██▓ ░██████▒ ██▓  ██▓
  ░ ▒░▓  ░ ▒▓▒  ▒▓▒ ░ ▒░▓  ░ ▒▓▒  ▒▓▒
  ░ ░ ▒  ░ ░▒   ░▒  ░ ░ ▒  ░ ░▒   ░▒
    ░ ░    ░    ░     ░ ░    ░    ░
      ░  ░  ░    ░      ░  ░  ░    ░
  ===========================================
    AmuleD_v2 Launcher by Soror L.'.L.'.
    Version: 1.0.0
  ===========================================

"@

# === Path Configuration ===
$ProjectRoot  = $PSScriptRoot
$VenvPython   = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$ConfigDir    = Join-Path $ProjectRoot "config"
$ConfigFile   = Join-Path $ConfigDir "amuled.jsonc"
$DbDir        = Join-Path $ProjectRoot "db"
$DbFile       = Join-Path $DbDir "amuled_state.db"
$LogsDir      = Join-Path $ProjectRoot "logs"

# === Pre-flight Validation ===
if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] AmuleD_v2: Virtual environment not found at $VenvPython" -ForegroundColor Red
    Write-Host "[ERROR] Run AmuleD_install.ps1 first to set up the environment." -ForegroundColor Red
    if (-not $NoPause) { Read-Host "Press Enter to exit" }
    exit 1
}

if (-not (Test-Path $ConfigFile)) {
    Write-Host "[ERROR] AmuleD_v2: Configuration file not found at $ConfigFile" -ForegroundColor Red
    Write-Host "[ERROR] Run AmuleD_install.ps1 first to generate the default config." -ForegroundColor Red
    if (-not $NoPause) { Read-Host "Press Enter to exit" }
    exit 1
}

# === Environment Variables ===
$env:PYTHONUNBUFFERED = "1"
$env:AMULED_ROOT      = $ProjectRoot
$env:AMULED_CONFIG    = $ConfigFile
$env:AMULED_DB        = $DbFile
$env:AMULED_LOGS      = $LogsDir

# === Argument Preparation ===
# Default to --help if no user-provided arguments
if ($Args.Count -eq 0) {
    $passArgs = @("--help")
} else {
    $passArgs = $Args
}

Set-Location $ProjectRoot

# === Execution ===
try {
    & $VenvPython -m amuled_v2 @passArgs
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "[ERROR] AmuleD_v2: Exception during execution: $($_.Exception.Message)" -ForegroundColor Red
    if (-not $NoPause) { Read-Host "Press Enter to exit" }
    exit 1
}

if ($exitCode -ne 0) {
    Write-Host "[ERROR] AmuleD_v2: Process exited with code $exitCode" -ForegroundColor Red
}

if (-not $NoPause) { Read-Host "Press Enter to exit" }
exit $exitCode
