# Daily Scraper Runner Script (PowerShell)
# 
# This script runs the automated tender monitor with proper logging.
# It's designed to be called from Windows Task Scheduler or manually.
#
# Usage:
#   .\run_daily_scraper.ps1 [-City "CITY"] [-WhatsApp "NUMBER"] [-Email "ADDRESS"]
#
# Exit codes:
#   0 - Success
#   1 - Failure

param(
    [string]$City = $null,
    [string]$WhatsApp = $null,
    [string]$Email = $null
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# Set up log file with timestamp
$LogDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $LogDir "daily_scraper_$Timestamp.log"

# Function to log messages
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

# Function to handle errors
function Exit-WithError {
    param([string]$Message)
    Write-Log "ERROR: $Message"
    exit 1
}

# Start logging
Write-Log "=========================================="
Write-Log "Daily Scraper - Starting"
Write-Log "=========================================="
Write-Log "Project root: $ProjectRoot"
Write-Log "Log file: $LogFile"
Write-Log ""

# Activate virtual environment
$VenvPath = Join-Path $ProjectRoot "backend\venv"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

if (Test-Path $ActivateScript) {
    Write-Log "Activating virtual environment: $VenvPath"
    & $ActivateScript
    Write-Log "Virtual environment activated"
} else {
    Exit-WithError "Virtual environment not found at $ActivateScript"
}

# Check if Python script exists
$PythonScript = Join-Path $ProjectRoot "backend\scraper\automated_tender_monitor.py"
if (-not (Test-Path $PythonScript)) {
    Exit-WithError "Python script not found at $PythonScript"
}

# Build command arguments
$Args = @()
if ($City) {
    $Args += "--city"
    $Args += $City
}
if ($WhatsApp) {
    $Args += "--whatsapp"
    $Args += $WhatsApp
}
if ($Email) {
    $Args += "--email"
    $Args += $Email
}

# Run the scraper
Write-Log "Running automated tender monitor..."
$Command = "python $PythonScript $($Args -join ' ')"
Write-Log "Command: $Command"
Write-Log ""

# Capture output and log to file
try {
    $Output = & python $PythonScript $Args 2>&1
    $ExitCode = $LASTEXITCODE
    
    # Log all output
    foreach ($Line in $Output) {
        Write-Log $Line
    }
    
    Write-Log ""
    Write-Log "=========================================="
    if ($ExitCode -eq 0) {
        Write-Log "Daily Scraper - Completed Successfully"
        Write-Log "Exit code: $ExitCode"
    } else {
        Write-Log "Daily Scraper - Failed"
        Write-Log "Exit code: $ExitCode"
    }
    Write-Log "=========================================="
    
    exit $ExitCode
} catch {
    Write-Log "ERROR: Exception occurred: $_"
    exit 1
}

