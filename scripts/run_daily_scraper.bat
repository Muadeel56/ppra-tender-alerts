@echo off
REM Daily Scraper Runner Script (Batch)
REM 
REM This script runs the automated tender monitor with proper logging.
REM It's designed to be called from Windows Task Scheduler or manually.
REM
REM Usage:
REM   run_daily_scraper.bat [--city CITY] [--whatsapp NUMBER] [--email ADDRESS]
REM
REM Exit codes:
REM   0 - Success
REM   1 - Failure

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"

REM Set up log file with timestamp
set "LOG_DIR=%PROJECT_ROOT%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%"
set "LOG_FILE=%LOG_DIR%\daily_scraper_%TIMESTAMP%.log"

REM Function to log messages
call :log "=========================================="
call :log "Daily Scraper - Starting"
call :log "=========================================="
call :log "Project root: %PROJECT_ROOT%"
call :log "Log file: %LOG_FILE%"
call :log ""

REM Activate virtual environment
set "VENV_PATH=%PROJECT_ROOT%\backend\venv"
set "ACTIVATE_SCRIPT=%VENV_PATH%\Scripts\activate.bat"

if exist "%ACTIVATE_SCRIPT%" (
    call :log "Activating virtual environment: %VENV_PATH%"
    call "%ACTIVATE_SCRIPT%"
    call :log "Virtual environment activated"
) else (
    call :log "ERROR: Virtual environment not found at %ACTIVATE_SCRIPT%"
    exit /b 1
)

REM Check if Python script exists
set "PYTHON_SCRIPT=%PROJECT_ROOT%\backend\scraper\automated_tender_monitor.py"
if not exist "%PYTHON_SCRIPT%" (
    call :log "ERROR: Python script not found at %PYTHON_SCRIPT%"
    exit /b 1
)

REM Run the scraper with all arguments passed to this script
call :log "Running automated tender monitor..."
set "CMD_LINE=python %PYTHON_SCRIPT% %*"
call :log "Command: %CMD_LINE%"
call :log ""

REM Run Python script and capture output
python "%PYTHON_SCRIPT%" %* >> "%LOG_FILE%" 2>&1
set EXIT_CODE=%ERRORLEVEL%

REM Display output from log file
type "%LOG_FILE%"

call :log ""
call :log "=========================================="
if %EXIT_CODE% equ 0 (
    call :log "Daily Scraper - Completed Successfully"
    call :log "Exit code: %EXIT_CODE%"
) else (
    call :log "Daily Scraper - Failed"
    call :log "Exit code: %EXIT_CODE%"
)
call :log "=========================================="

exit /b %EXIT_CODE%

REM Logging function
:log
set "MESSAGE=%~1"
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%"
echo [%TIMESTAMP%] %MESSAGE%
echo [%TIMESTAMP%] %MESSAGE% >> "%LOG_FILE%"
exit /b

