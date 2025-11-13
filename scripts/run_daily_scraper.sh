#!/bin/bash
# Daily Scraper Runner Script
# 
# This script runs the automated tender monitor with proper logging.
# It's designed to be called from cron or manually.
#
# Usage:
#   ./run_daily_scraper.sh [--city CITY] [--whatsapp NUMBER] [--email ADDRESS]
#
# Exit codes:
#   0 - Success
#   1 - Failure

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Set up log file with timestamp
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/daily_scraper_${TIMESTAMP}.log"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to handle errors
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Start logging
log "=========================================="
log "Daily Scraper - Starting"
log "=========================================="
log "Project root: $PROJECT_ROOT"
log "Log file: $LOG_FILE"
log ""

# Activate virtual environment
VENV_PATH="$PROJECT_ROOT/backend/venv"
if [ -f "$VENV_PATH/bin/activate" ]; then
    log "Activating virtual environment: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
    log "Virtual environment activated"
else
    error_exit "Virtual environment not found at $VENV_PATH/bin/activate"
fi

# Check if Python script exists
PYTHON_SCRIPT="$PROJECT_ROOT/backend/scraper/automated_tender_monitor.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    error_exit "Python script not found at $PYTHON_SCRIPT"
fi

# Run the scraper with all arguments passed to this script
log "Running automated tender monitor..."
log "Command: python3 $PYTHON_SCRIPT $@"
log ""

# Capture both stdout and stderr, and also log to file
if python3 "$PYTHON_SCRIPT" "$@" 2>&1 | tee -a "$LOG_FILE"; then
    EXIT_CODE=${PIPESTATUS[0]}
else
    EXIT_CODE=$?
fi

log ""
log "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    log "Daily Scraper - Completed Successfully"
    log "Exit code: $EXIT_CODE"
else
    log "Daily Scraper - Failed"
    log "Exit code: $EXIT_CODE"
fi
log "=========================================="

exit $EXIT_CODE

