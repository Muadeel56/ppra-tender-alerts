#!/bin/bash
# Test runner script for Chakwal filter test

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -f "backend/venv/bin/activate" ]; then
    source backend/venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Error: Virtual environment not found at backend/venv/bin/activate"
    echo "Please create it first: python3 -m venv backend/venv"
    exit 1
fi

# Run the test
echo "Running Chakwal filter test..."
python3 tests/test_chakwal_filter.py "$@"

