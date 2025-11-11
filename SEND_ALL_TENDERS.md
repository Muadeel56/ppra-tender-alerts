# Send All Active Tenders

This script scrapes **ALL** active tenders for a city and sends them to your WhatsApp and Gmail.

## Quick Start

### Send all active tenders in Islamabad

```bash
# Activate virtual environment
source backend/venv/bin/activate  # or venv/bin/activate

# Send all Islamabad tenders
python backend/scraper/send_all_tenders.py Islamabad
```

### What it does

1. **Scrapes** all active tenders from PPRA website for the specified city
2. **Sends** each tender to:
   - Your WhatsApp (if configured)
   - Your Gmail (if configured)

## Usage Examples

### Basic usage (uses .env for credentials)

```bash
python backend/scraper/send_all_tenders.py Islamabad
```

### Specify recipients

```bash
python backend/scraper/send_all_tenders.py Islamabad \
  --whatsapp "whatsapp:+923145494430" \
  --email "muadeel69@gmail.com"
```

### Run with visible browser (for debugging)

```bash
python backend/scraper/send_all_tenders.py Islamabad --no-headless
```

### Skip confirmation prompt

```bash
python backend/scraper/send_all_tenders.py Islamabad --yes
```

## Other Cities

You can use this for any city:

```bash
python backend/scraper/send_all_tenders.py Lahore
python backend/scraper/send_all_tenders.py Karachi
python backend/scraper/send_all_tenders.py Rawalpindi
```

## Important Notes

⚠️ **Rate Limiting**: If there are many tenders (10+), the script will:
- Ask for confirmation before sending
- Add a 1-second delay between each notification
- This prevents overwhelming Twilio/Gmail APIs

⚠️ **Quota Usage**: Sending many notifications will use your:
- Twilio credits (for WhatsApp)
- Gmail sending quota

## Example Output

```
======================================================================
📨 Send All Active Tenders - Islamabad
======================================================================

======================================================================
Scraping ALL Active Tenders for Islamabad
======================================================================

Initializing scraper (headless=True)...
✅ Scraper initialized

Applying city filter: Islamabad...
✅ City filter applied: Islamabad

Extracting tender data from website...
✅ Extracted 15 active tenders for Islamabad

Summary of tenders found:
  1. Federal Directorate of Education,Islamabad, Pakistan...
     Closing: Nov 7, 2025
  2. National Information Technology Board,Islamabad, Pakistan...
     Closing: Nov 21, 2025
  ... and 13 more

======================================================================
Sending Notifications for ALL 15 Tenders
======================================================================

[1/15] Sending notifications:
   Title: Federal Directorate of Education,Islamabad, Pakistan...
   Closing: Nov 7, 2025
   ✅ WhatsApp: Sent
   ✅ Email: Sent

[2/15] Sending notifications:
   Title: National Information Technology Board,Islamabad, Pakistan...
   Closing: Nov 21, 2025
   ✅ WhatsApp: Sent
   ✅ Email: Sent

...

======================================================================
📊 Summary
======================================================================
City: Islamabad
Total tenders scraped: 15
WhatsApp notifications: 15 sent, 0 failed
Email notifications: 15 sent, 0 failed
```

## Difference from Automated Monitor

| Feature | `send_all_tenders.py` | `automated_tender_monitor.py` |
|---------|----------------------|-------------------------------|
| **What it sends** | ALL active tenders | Only NEW tenders |
| **Use case** | Get all current tenders | Get notified about new ones |
| **Frequency** | Run manually when needed | Run periodically (cron) |
| **Storage** | Doesn't save to storage | Saves new tenders |

## Configuration

Make sure your `.env` file has:

```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+923145494430

# Gmail SMTP
GMAIL_SMTP_USER=your_email@gmail.com
GMAIL_SMTP_PASSWORD=your_app_password
GMAIL_SMTP_TO=muadeel69@gmail.com
```

