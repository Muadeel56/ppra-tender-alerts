# Scheduling Daily Execution

This document explains how to set up automated daily execution of the PPRA Tender Scraper and Notification System on both Linux and Windows platforms.

## Overview

The automated tender monitor runs daily to:
1. Scrape tenders from the PPRA website
2. Detect new tenders (compare with existing ones)
3. Send notifications (WhatsApp & Email) for new tenders
4. Save new tenders to storage

All executions are logged to files in the `logs/` directory for monitoring and troubleshooting.

## Logging

### Log File Locations

- **Python logs**: `logs/automated_monitor_YYYY-MM-DD.log`
  - Contains detailed execution logs from the Python script
  - Daily rotation (one file per day)
  - Includes timestamps, success/failure status, and error details

- **Wrapper script logs**: `logs/daily_scraper_YYYY-MM-DD_HH-MM-SS.log`
  - Contains wrapper script execution logs
  - Includes activation of virtual environment, command execution, and exit codes

### Log File Format

Log files include:
- Timestamps for each operation
- Success/failure indicators
- Error messages with stack traces (when applicable)
- Summary statistics (tenders scraped, new tenders found, notifications sent)

### Log Retention

Log files are stored in the `logs/` directory. By default, all log files are kept. You can implement log rotation by:
- Setting up a cron job to archive old logs
- Using logrotate (Linux)
- Manually deleting old log files

---

## Linux: Cron Job Setup

### Prerequisites

1. Ensure the wrapper script is executable:
   ```bash
   chmod +x scripts/run_daily_scraper.sh
   ```

2. Test the script manually first:
   ```bash
   ./scripts/run_daily_scraper.sh
   ```

### Setting Up Cron Job

1. **Open crontab editor**:
   ```bash
   crontab -e
   ```

2. **Add a cron job entry**:

   **Daily at 9:00 AM**:
   ```cron
   0 9 * * * /path/to/ppra-tender-alerts/scripts/run_daily_scraper.sh >> /path/to/ppra-tender-alerts/logs/cron.log 2>&1
   ```

   **Daily at 9:00 AM with city filter**:
   ```cron
   0 9 * * * /path/to/ppra-tender-alerts/scripts/run_daily_scraper.sh --city "Islamabad" >> /path/to/ppra-tender-alerts/logs/cron.log 2>&1
   ```

   **Twice daily (9 AM and 6 PM)**:
   ```cron
   0 9,18 * * * /path/to/ppra-tender-alerts/scripts/run_daily_scraper.sh >> /path/to/ppra-tender-alerts/logs/cron.log 2>&1
   ```

   **Every 6 hours**:
   ```cron
   0 */6 * * * /path/to/ppra-tender-alerts/scripts/run_daily_scraper.sh >> /path/to/ppra-tender-alerts/logs/cron.log 2>&1
   ```

3. **Replace `/path/to/ppra-tender-alerts`** with the actual absolute path to your project directory.

4. **Save and exit** the crontab editor.

### Cron Schedule Format

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, where 0 and 7 are Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

### Verifying Cron Job

1. **List your cron jobs**:
   ```bash
   crontab -l
   ```

2. **Check cron logs** (location varies by system):
   ```bash
   # Ubuntu/Debian
   grep CRON /var/log/syslog
   
   # CentOS/RHEL
   grep CRON /var/log/cron
   ```

3. **Check application logs**:
   ```bash
   ls -lh logs/
   tail -f logs/automated_monitor_$(date +%Y-%m-%d).log
   ```

### Troubleshooting Cron Issues

1. **Cron doesn't run**:
   - Check if cron service is running: `systemctl status cron` (or `crond` on some systems)
   - Verify the path in crontab is absolute (not relative)
   - Check file permissions (script must be executable)

2. **Cron runs but script fails**:
   - Check wrapper script log: `logs/daily_scraper_*.log`
   - Check Python script log: `logs/automated_monitor_*.log`
   - Ensure virtual environment path is correct
   - Verify Python is in PATH when cron runs

3. **Environment variables not available**:
   - Cron runs with minimal environment
   - Use absolute paths in the script
   - Source `.env` file explicitly if needed (already handled in the script)

### Log Rotation (Optional)

To automatically archive old logs, add this to crontab:

```cron
# Archive logs older than 30 days (runs daily at 2 AM)
0 2 * * * find /path/to/ppra-tender-alerts/logs -name "*.log" -mtime +30 -exec gzip {} \;
```

---

## Windows: Task Scheduler Setup

### Prerequisites

1. Ensure PowerShell execution policy allows scripts:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. Test the script manually first:
   ```powershell
   .\scripts\run_daily_scraper.ps1
   ```

### Setting Up Task Scheduler

#### Method 1: Using PowerShell Script (Recommended)

1. **Open Task Scheduler**:
   - Press `Win + R`, type `taskschd.msc`, press Enter
   - Or search "Task Scheduler" in Start menu

2. **Create Basic Task**:
   - Click "Create Basic Task..." in the right panel
   - Name: `PPRA Tender Scraper Daily`
   - Description: `Runs daily scraper and notification system`

3. **Set Trigger**:
   - Trigger: Daily
   - Start date: Today's date
   - Start time: 9:00 AM (or your preferred time)
   - Recur every: 1 day

4. **Set Action**:
   - Action: Start a program
   - Program/script: `powershell.exe`
   - Add arguments:
     ```
     -ExecutionPolicy Bypass -File "C:\path\to\ppra-tender-alerts\scripts\run_daily_scraper.ps1"
     ```
   - Start in (optional): `C:\path\to\ppra-tender-alerts`

5. **Configure Settings**:
   - Check "Run whether user is logged on or not"
   - Check "Run with highest privileges" (if needed)
   - Configure for: Windows 10/Windows Server 2016

6. **Save the task**

#### Method 2: Using Batch Script

1. **Follow steps 1-3 above** (same trigger setup)

2. **Set Action**:
   - Action: Start a program
   - Program/script: `C:\path\to\ppra-tender-alerts\scripts\run_daily_scraper.bat`
   - Start in (optional): `C:\path\to\ppra-tender-alerts`

3. **Configure Settings** (same as Method 1)

4. **Save the task**

### Advanced Configuration

#### Running with City Filter

Edit the task action arguments:

**PowerShell**:
```
-ExecutionPolicy Bypass -File "C:\path\to\ppra-tender-alerts\scripts\run_daily_scraper.ps1" -City "Islamabad"
```

**Batch**:
The batch script passes all arguments, so you can modify the task action to:
```
C:\path\to\ppra-tender-alerts\scripts\run_daily_scraper.bat --city "Islamabad"
```

#### Running Multiple Times Per Day

1. Edit the task
2. Go to "Triggers" tab
3. Add additional triggers with different times

### Verifying Task Execution

1. **Check Task History**:
   - Open Task Scheduler
   - Select your task
   - Click "History" tab to see execution logs

2. **Check Application Logs**:
   ```powershell
   Get-ChildItem logs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 5
   Get-Content logs\automated_monitor_$(Get-Date -Format 'yyyy-MM-dd').log -Tail 50
   ```

3. **Test Run Manually**:
   - Right-click the task in Task Scheduler
   - Select "Run"
   - Check the History tab for results

### Troubleshooting Task Scheduler Issues

1. **Task doesn't run**:
   - Check task status (should be "Ready")
   - Verify trigger is enabled
   - Check "Last Run Result" in task properties
   - Ensure user account has permission to run tasks

2. **Task runs but script fails**:
   - Check wrapper script log: `logs\daily_scraper_*.log`
   - Check Python script log: `logs\automated_monitor_*.log`
   - Verify virtual environment path is correct
   - Check if Python is in system PATH

3. **PowerShell execution policy error**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   Or use `-ExecutionPolicy Bypass` in the task action arguments

4. **Virtual environment not found**:
   - Verify the path to `backend\venv\Scripts\Activate.ps1` is correct
   - Ensure virtual environment was created properly

### Log Rotation (Optional)

Create a PowerShell script to archive old logs:

```powershell
# archive_old_logs.ps1
$LogDir = "C:\path\to\ppra-tender-alerts\logs"
$ArchiveDir = Join-Path $LogDir "archive"
if (-not (Test-Path $ArchiveDir)) {
    New-Item -ItemType Directory -Path $ArchiveDir | Out-Null
}

Get-ChildItem -Path $LogDir -Filter "*.log" | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
    Compress-Archive -DestinationPath (Join-Path $ArchiveDir "logs_$(Get-Date -Format 'yyyy-MM').zip") -Force
```

Schedule this script to run monthly in Task Scheduler.

---

## Manual Execution

You can also run the scraper manually at any time:

### Linux/Mac

```bash
# Basic run
./scripts/run_daily_scraper.sh

# With city filter
./scripts/run_daily_scraper.sh --city "Islamabad"

# With custom recipients
./scripts/run_daily_scraper.sh --city "Lahore" --whatsapp "whatsapp:+1234567890" --email "user@example.com"
```

### Windows

**PowerShell**:
```powershell
.\scripts\run_daily_scraper.ps1
.\scripts\run_daily_scraper.ps1 -City "Islamabad"
```

**Command Prompt**:
```cmd
scripts\run_daily_scraper.bat
scripts\run_daily_scraper.bat --city "Islamabad"
```

---

## Monitoring and Alerts

### Checking Log Files

**Recent logs**:
```bash
# Linux
ls -lht logs/ | head -10
tail -f logs/automated_monitor_$(date +%Y-%m-%d).log

# Windows PowerShell
Get-ChildItem logs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 10
Get-Content logs\automated_monitor_$(Get-Date -Format 'yyyy-MM-dd').log -Tail 50 -Wait
```

### Success Indicators

Look for these in the logs:
- `Run completed successfully`
- `Exit code: 0`
- Summary showing tenders scraped and notifications sent

### Failure Indicators

Watch for:
- `ERROR:` messages
- `Exit code: 1` or non-zero exit codes
- Exception stack traces
- "Failed" status messages

### Setting Up Email Alerts for Failures

You can extend the wrapper scripts to send email alerts on failure, or use system monitoring tools to watch the log files.

---

## Best Practices

1. **Test First**: Always test the script manually before scheduling
2. **Monitor Initially**: Check logs daily for the first week after setup
3. **Set Appropriate Schedule**: Consider PPRA website update frequency
4. **Log Rotation**: Implement log rotation to prevent disk space issues
5. **Backup Configuration**: Keep a backup of your cron/task scheduler configuration
6. **Document Customizations**: Note any custom arguments or filters you use

---

## Troubleshooting Common Issues

### Issue: Script runs but no tenders found

**Possible causes**:
- No active tenders on PPRA website (normal)
- City filter too restrictive
- Website structure changed (scraper needs update)

**Solution**: Check logs for scraping errors, verify city name spelling

### Issue: Notifications not sent

**Possible causes**:
- Missing or incorrect credentials in `.env` file
- Twilio/Gmail API limits reached
- Network connectivity issues

**Solution**: Check notification logs, verify credentials, check API quotas

### Issue: Virtual environment not found

**Possible causes**:
- Virtual environment not created
- Wrong path in wrapper script
- Virtual environment deleted

**Solution**: Recreate virtual environment, verify paths in wrapper script

### Issue: Permission denied errors

**Possible causes**:
- Script not executable (Linux)
- Insufficient permissions
- User account restrictions

**Solution**: 
- Linux: `chmod +x scripts/run_daily_scraper.sh`
- Windows: Run Task Scheduler as administrator or ensure user has permissions

---

## Support

For issues or questions:
1. Check the log files first
2. Review this documentation
3. Check the main README.md for general setup instructions
4. Review the AUTOMATED_FLOW.md for understanding the workflow

