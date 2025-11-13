#!/bin/bash
# Verification Script for Issue #35 - Schedule Daily Execution
# This script checks if all components are in place and working

echo "=========================================="
echo "Issue #35 Verification Checklist"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Verify branch
echo "[1/10] Checking branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" == *"issue-35"* ]]; then
    echo "  ✓ On issue branch: $CURRENT_BRANCH"
else
    echo "  ⚠ Warning: Not on issue-35 branch (current: $CURRENT_BRANCH)"
    ((WARNINGS++))
fi
echo ""

# Check 2: Verify logs directory exists
echo "[2/10] Checking logs directory..."
if [ -d "logs" ]; then
    echo "  ✓ logs/ directory exists"
    if [ -f "logs/.gitkeep" ]; then
        echo "  ✓ logs/.gitkeep exists"
    else
        echo "  ✗ logs/.gitkeep missing"
        ((ERRORS++))
    fi
else
    echo "  ✗ logs/ directory missing"
    ((ERRORS++))
fi
echo ""

# Check 3: Verify .gitignore updated
echo "[3/10] Checking .gitignore..."
if grep -q "logs/\*.log" .gitignore 2>/dev/null; then
    echo "  ✓ .gitignore includes logs/*.log"
else
    echo "  ✗ .gitignore missing logs/*.log entry"
    ((ERRORS++))
fi
echo ""

# Check 4: Verify Linux wrapper script
echo "[4/10] Checking Linux wrapper script..."
if [ -f "scripts/run_daily_scraper.sh" ]; then
    echo "  ✓ scripts/run_daily_scraper.sh exists"
    if [ -x "scripts/run_daily_scraper.sh" ]; then
        echo "  ✓ Script is executable"
    else
        echo "  ⚠ Warning: Script not executable (run: chmod +x scripts/run_daily_scraper.sh)"
        ((WARNINGS++))
    fi
else
    echo "  ✗ scripts/run_daily_scraper.sh missing"
    ((ERRORS++))
fi
echo ""

# Check 5: Verify Windows PowerShell script
echo "[5/10] Checking Windows PowerShell script..."
if [ -f "scripts/run_daily_scraper.ps1" ]; then
    echo "  ✓ scripts/run_daily_scraper.ps1 exists"
else
    echo "  ✗ scripts/run_daily_scraper.ps1 missing"
    ((ERRORS++))
fi
echo ""

# Check 6: Verify Windows Batch script
echo "[6/10] Checking Windows Batch script..."
if [ -f "scripts/run_daily_scraper.bat" ]; then
    echo "  ✓ scripts/run_daily_scraper.bat exists"
else
    echo "  ✗ scripts/run_daily_scraper.bat missing"
    ((ERRORS++))
fi
echo ""

# Check 7: Verify documentation
echo "[7/10] Checking documentation..."
if [ -f "docs/SCHEDULING.md" ]; then
    echo "  ✓ docs/SCHEDULING.md exists"
    # Check if it has key sections
    if grep -q "Linux.*Cron" docs/SCHEDULING.md 2>/dev/null; then
        echo "  ✓ Documentation includes Linux/Cron instructions"
    fi
    if grep -q "Windows.*Task Scheduler" docs/SCHEDULING.md 2>/dev/null; then
        echo "  ✓ Documentation includes Windows/Task Scheduler instructions"
    fi
else
    echo "  ✗ docs/SCHEDULING.md missing"
    ((ERRORS++))
fi
echo ""

# Check 8: Verify README updated
echo "[8/10] Checking README.md..."
if grep -q "Automated Daily Execution" README.md 2>/dev/null; then
    echo "  ✓ README.md includes 'Automated Daily Execution' section"
    if grep -q "SCHEDULING.md" README.md 2>/dev/null; then
        echo "  ✓ README.md references SCHEDULING.md"
    fi
else
    echo "  ✗ README.md missing scheduling section"
    ((ERRORS++))
fi
echo ""

# Check 9: Verify logging in automated_tender_monitor.py
echo "[9/10] Checking logging implementation..."
if grep -q "import logging" backend/scraper/automated_tender_monitor.py 2>/dev/null; then
    echo "  ✓ automated_tender_monitor.py imports logging"
    if grep -q "setup_logging" backend/scraper/automated_tender_monitor.py 2>/dev/null; then
        echo "  ✓ setup_logging function exists"
    fi
    if grep -q "self.logger" backend/scraper/automated_tender_monitor.py 2>/dev/null; then
        echo "  ✓ Logger is used in class methods"
    fi
else
    echo "  ✗ Logging not implemented in automated_tender_monitor.py"
    ((ERRORS++))
fi
echo ""

# Check 10: Test script syntax (if Python available)
echo "[10/10] Testing script syntax..."
if command -v python3 &> /dev/null; then
    if python3 -m py_compile backend/scraper/automated_tender_monitor.py 2>/dev/null; then
        echo "  ✓ Python script syntax is valid"
    else
        echo "  ✗ Python script has syntax errors"
        ((ERRORS++))
    fi
else
    echo "  ⚠ Warning: python3 not found, skipping syntax check"
    ((WARNINGS++))
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "✓ All checks passed! Issue #35 appears to be complete."
        exit 0
    else
        echo "✓ All critical checks passed, but there are warnings."
        echo "  Review warnings above and fix if needed."
        exit 0
    fi
else
    echo "✗ Some checks failed. Please review errors above."
    exit 1
fi

