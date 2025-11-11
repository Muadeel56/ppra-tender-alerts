# Automated Tender Monitoring Flow

## Overview

This document explains the complete automated flow from scraping to notifications.

## The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOMATED TENDER MONITOR                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 1: Scrape Tenders            │
        │  - Visit PPRA website              │
        │  - Filter by city (optional)        │
        │  - Extract tender data              │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2: Detect New Tenders          │
        │  - Load existing tenders from JSON   │
        │  - Compare with scraped tenders      │
        │  - Identify new tenders (duplicates) │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 3: Send Notifications          │
        │  - For each new tender:              │
        │    • Send WhatsApp alert             │
        │    • Send Email alert                │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 4: Save New Tenders           │
        │  - Save to data/tenders.json        │
        │  - Update storage for next run       │
        └─────────────────────────────────────┘
```

## Data Flow

1. **Scraping** (`PPRAScraper`)
   - Uses Selenium to scrape PPRA website
   - Extracts: Title, Category, Department, Closing Date, Tender Number, PDF Links
   - Returns list of tender dictionaries

2. **Storage** (`tender_storage.py`)
   - Existing tenders stored in `data/tenders.json`
   - New tenders compared using `tender_number` field
   - Duplicates detected and skipped

3. **Notifications** (`notifications.py`)
   - WhatsApp: Uses Twilio API
   - Email: Uses Gmail SMTP
   - Both use the new formatted message format:
     - Tender Title
     - Category
     - Department
     - Closing Date
     - Link
     - Deliverables

4. **Automation** (`automated_tender_monitor.py`)
   - Orchestrates all steps
   - Can be run manually or scheduled (cron, etc.)

## Usage

### Run the Automated Monitor

```bash
# Activate virtual environment
source backend/venv/bin/activate  # or venv/bin/activate

# Run with default settings (uses .env for credentials)
python backend/scraper/automated_tender_monitor.py

# Filter by city
python backend/scraper/automated_tender_monitor.py --city "Islamabad"

# Specify recipients
python backend/scraper/automated_tender_monitor.py \
  --whatsapp "whatsapp:+1234567890" \
  --email "user@example.com"

# Run with visible browser (for debugging)
python backend/scraper/automated_tender_monitor.py --no-headless
```

### Schedule Automated Runs

You can schedule this to run periodically using cron:

```bash
# Edit crontab
crontab -e

# Run every 6 hours
0 */6 * * * cd /path/to/ppra-tender-alerts && source backend/venv/bin/activate && python backend/scraper/automated_tender_monitor.py

# Run daily at 9 AM
0 9 * * * cd /path/to/ppra-tender-alerts && source backend/venv/bin/activate && python backend/scraper/automated_tender_monitor.py --city "Islamabad"
```

## Configuration

### Environment Variables (.env file)

```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+1234567890

# Gmail SMTP
GMAIL_SMTP_USER=your_email@gmail.com
GMAIL_SMTP_PASSWORD=your_app_password
GMAIL_SMTP_TO=recipient@example.com
```

## What Happens When You Run It

1. **Scrapes** current active tenders from PPRA website
2. **Compares** with existing tenders in `data/tenders.json`
3. **Identifies** new tenders (ones not seen before)
4. **Sends** formatted notifications for each new tender via:
   - WhatsApp (if configured)
   - Email (if configured)
5. **Saves** new tenders to storage for next comparison

## Example Output

```
======================================================================
🤖 Automated Tender Monitor - Starting
======================================================================

======================================================================
Step 1: Scraping Tenders from PPRA Website
======================================================================

Initializing scraper (headless=True)...
✅ Scraper initialized

Applying city filter: Islamabad...
✅ City filter applied: Islamabad

Extracting tender data from website...
✅ Extracted 15 tenders

Sample tender:
  Title: Federal Directorate of Education,Islamabad, Pakistan...
  Number: TS681599E
  Closing Date: Nov 7, 2025

======================================================================
Step 2: Detecting New Tenders
======================================================================

Loading existing tenders from: /path/to/data/tenders.json
✅ Found 367 existing tenders in storage

Comparing scraped tenders with existing ones...
✅ Comparison complete:
   - Total scraped: 15
   - New tenders found: 3
   - Duplicates skipped: 12

📋 New tenders to notify:
   1. New Tender Title 1... (Closes: Nov 10, 2025)
   2. New Tender Title 2... (Closes: Nov 15, 2025)
   3. New Tender Title 3... (Closes: Nov 20, 2025)

======================================================================
Step 3: Sending Notifications for New Tenders
======================================================================

[1/3] Sending notifications for:
   Title: New Tender Title 1...
   ✅ WhatsApp: Sent (SID: SM1234567890...)
   ✅ Email: Sent to user@example.com

[2/3] Sending notifications for:
   Title: New Tender Title 2...
   ✅ WhatsApp: Sent (SID: SM0987654321...)
   ✅ Email: Sent to user@example.com

[3/3] Sending notifications for:
   Title: New Tender Title 3...
   ✅ WhatsApp: Sent (SID: SM1122334455...)
   ✅ Email: Sent to user@example.com

======================================================================
Step 4: Saving New Tenders to Storage
======================================================================

✅ Successfully saved 3 new tenders to /path/to/data/tenders.json
   Total tenders in storage: 370

======================================================================
📊 Summary
======================================================================
Tenders scraped: 15
New tenders found: 3
WhatsApp notifications: 3 sent, 0 failed
Email notifications: 3 sent, 0 failed
Storage: ✅ Saved
```

## Answer to Your Question

**Yes, the data you received came from scraping!**

The flow works like this:

1. **Previous scraping** → Data stored in `data/tenders.json` (that's where your email data came from)
2. **New scraping** → Gets latest tenders from PPRA website
3. **Comparison** → Finds which ones are new
4. **Notifications** → Sends alerts only for new tenders
5. **Storage** → Saves new tenders for next comparison

The `automated_tender_monitor.py` script connects all these pieces together into one automated flow!

