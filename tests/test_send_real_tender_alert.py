#!/usr/bin/env python3
"""
Test Real Tender Alert Script

This script sends a real tender alert to both WhatsApp and Email
using the new formatted message format.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add backend directory to path to import scraper modules
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import directly from notifications module to avoid importing other dependencies
import importlib.util
notifications_path = os.path.join(backend_path, 'scraper', 'notifications.py')
spec = importlib.util.spec_from_file_location("notifications", notifications_path)
notifications = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notifications)

WhatsAppNotifier = notifications.WhatsAppNotifier
EmailNotifier = notifications.EmailNotifier


def load_real_tender_data(filepath: str = None):
    """
    Load a real tender from the tenders.json file.
    
    Args:
        filepath (str): Path to tenders.json file. If None, uses default location.
        
    Returns:
        dict: First tender from the file, or None if file not found
    """
    if filepath is None:
        # Default to data/tenders.json in project root
        project_root = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(project_root, 'data', 'tenders.json')
    
    try:
        if not os.path.exists(filepath):
            print(f"❌ ERROR: Tender data file not found: {filepath}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            tenders = json.load(f)
        
        if not isinstance(tenders, list) or len(tenders) == 0:
            print(f"❌ ERROR: No tenders found in {filepath}")
            return None
        
        # Return a real tender (skip example data)
        for tender in tenders:
            title = tender.get('tender_title', '')
            # Skip example/test data
            if 'example.com' in str(tender.get('pdf_links', [])):
                continue
            if 'Supply of Office Equipment' in title or 'Construction of Road' in title or 'Medical Supplies' in title:
                continue
            # Prefer tenders with real Pakistani government departments and dates
            if title and tender.get('closing_date') and ('Pakistan' in title or 'Ministry' in title or 'Department' in title or 'Company' in title):
                return tender
        
        # If no real tender found, return the first non-example one
        for tender in tenders:
            if 'example.com' not in str(tender.get('pdf_links', [])):
                return tender
        
        # Last resort: return the first one
        return tenders[0] if tenders else None
        
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in {filepath}: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ ERROR: Failed to load tender data: {str(e)}")
        return None


def main():
    """Main function to send real tender alerts."""
    # Check for command-line arguments
    skip_confirmation = '--yes' in sys.argv or '-y' in sys.argv
    
    # Load environment variables
    load_dotenv()
    
    print("=" * 70)
    print("Real Tender Alert Test - WhatsApp & Email")
    print("=" * 70)
    print()
    
    # Load real tender data
    print("Loading real tender data...")
    tender_data = load_real_tender_data()
    
    if not tender_data:
        print("❌ Failed to load tender data. Exiting.")
        return 1
    
    print("✅ Tender data loaded successfully")
    print(f"   Title: {tender_data.get('tender_title', 'N/A')[:60]}...")
    print()
    
    # Display the tender data that will be sent
    print("Tender Details to be sent:")
    print("-" * 70)
    print(f"Tender Title: {tender_data.get('tender_title', 'N/A')}")
    print(f"Category: {tender_data.get('category', 'N/A')}")
    print(f"Department: {tender_data.get('department_owner', 'N/A')}")
    print(f"Closing Date: {tender_data.get('closing_date', 'N/A')}")
    print(f"Link: {tender_data.get('pdf_links', ['N/A'])[0] if tender_data.get('pdf_links') else 'N/A'}")
    print(f"Deliverables: {tender_data.get('deliverables', 'N/A')}")
    print("-" * 70)
    print()
    
    # Ask user for confirmation (unless skipped)
    if not skip_confirmation:
        try:
            response = input("Do you want to send this tender alert? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Cancelled by user.")
                return 0
        except EOFError:
            print("⚠️  No input available. Use --yes or -y flag to skip confirmation.")
            print("   Example: python tests/test_send_real_tender_alert.py --yes")
            return 1
    else:
        print("⏩ Skipping confirmation (--yes flag provided)")
        print()
    
    print()
    
    # Send WhatsApp alert
    print("=" * 70)
    print("Sending WhatsApp Alert")
    print("=" * 70)
    print()
    
    whatsapp_to = os.getenv('TWILIO_WHATSAPP_TO')
    if not whatsapp_to:
        print("⚠️  WARNING: TWILIO_WHATSAPP_TO not set. Skipping WhatsApp alert.")
        print("   Set TWILIO_WHATSAPP_TO in .env file to send WhatsApp alerts.")
        whatsapp_success = False
    else:
        try:
            whatsapp_notifier = WhatsAppNotifier()
            print(f"✅ WhatsApp notifier initialized")
            print(f"   Sending to: {whatsapp_to}")
            print()
            
            result = whatsapp_notifier.send_tender_alert(whatsapp_to, tender_data)
            
            if result['success']:
                print("✅ SUCCESS: WhatsApp alert sent!")
                print(f"   Message SID: {result.get('message_sid', 'N/A')}")
                print(f"   Status: {result.get('status', 'N/A')}")
                whatsapp_success = True
            else:
                print("❌ ERROR: Failed to send WhatsApp alert")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                whatsapp_success = False
        except ValueError as e:
            print(f"❌ ERROR: {str(e)}")
            print("   Please check your Twilio credentials in .env file")
            whatsapp_success = False
        except Exception as e:
            print(f"❌ ERROR: Unexpected error: {type(e).__name__}: {str(e)}")
            whatsapp_success = False
    
    print()
    
    # Send Email alert
    print("=" * 70)
    print("Sending Email Alert")
    print("=" * 70)
    print()
    
    email_to = os.getenv('GMAIL_SMTP_TO') or os.getenv('GMAIL_SMTP_USER')
    if not email_to:
        print("⚠️  WARNING: GMAIL_SMTP_TO and GMAIL_SMTP_USER not set. Skipping email alert.")
        print("   Set GMAIL_SMTP_TO or GMAIL_SMTP_USER in .env file to send email alerts.")
        email_success = False
    else:
        try:
            email_notifier = EmailNotifier()
            print(f"✅ Email notifier initialized")
            print(f"   Sending to: {email_to}")
            print()
            
            result = email_notifier.send_tender_alert(email_to, tender_data)
            
            if result['success']:
                print("✅ SUCCESS: Email alert sent!")
                print(f"   Check your inbox (and spam folder) for the email.")
                email_success = True
            else:
                print("❌ ERROR: Failed to send email alert")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                email_success = False
        except ValueError as e:
            print(f"❌ ERROR: {str(e)}")
            print("   Please check your Gmail credentials in .env file")
            email_success = False
        except Exception as e:
            print(f"❌ ERROR: Unexpected error: {type(e).__name__}: {str(e)}")
            email_success = False
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"WhatsApp: {'✅ Sent' if whatsapp_success else '❌ Failed or Skipped'}")
    print(f"Email:    {'✅ Sent' if email_success else '❌ Failed or Skipped'}")
    print()
    
    if whatsapp_success or email_success:
        print("🎉 At least one alert was sent successfully!")
        return 0
    else:
        print("⚠️  No alerts were sent. Please check your configuration.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

