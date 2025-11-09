#!/usr/bin/env python3
"""
Test Email Notification Script

This script tests email sending via Gmail SMTP.
It loads environment variables, initializes the email notifier,
and sends a test email to verify the integration works correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import scraper modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scraper.notifications import EmailNotifier


def main():
    """Main function to test email notification sending."""
    # Load environment variables from .env file
    load_dotenv()
    
    print("=" * 60)
    print("Email Notification Test via Gmail SMTP")
    print("=" * 60)
    print()
    
    # Check if required environment variables are set
    smtp_user = os.getenv('GMAIL_SMTP_USER')
    smtp_password = os.getenv('GMAIL_SMTP_PASSWORD')
    smtp_from = os.getenv('GMAIL_SMTP_FROM')
    to_email = os.getenv('GMAIL_SMTP_TO')
    
    print("Checking environment variables...")
    if not smtp_user:
        print("❌ ERROR: GMAIL_SMTP_USER is not set in .env file")
        print("   Please add your Gmail address to .env file")
        print("   Example: GMAIL_SMTP_USER=yourname@gmail.com")
        return 1
    
    if not smtp_password:
        print("❌ ERROR: GMAIL_SMTP_PASSWORD is not set in .env file")
        print("   Please add your Gmail App Password to .env file")
        print("   See README.md for instructions on generating an App Password")
        return 1
    
    if not to_email:
        print("⚠️  WARNING: GMAIL_SMTP_TO is not set in .env file")
        print("   Using GMAIL_SMTP_USER as recipient for testing")
        to_email = smtp_user
    else:
        print(f"✅ Recipient email: {to_email}")
    
    print("✅ All required environment variables are set")
    print()
    
    # Initialize email notifier
    print("Initializing email notifier...")
    try:
        notifier = EmailNotifier()
        print("✅ Email notifier initialized successfully")
        print(f"   SMTP Server: {notifier.smtp_server}:{notifier.smtp_port}")
        print(f"   From: {notifier.smtp_from}")
        print()
    except ValueError as e:
        print(f"❌ ERROR: Failed to initialize email notifier")
        print(f"   {str(e)}")
        return 1
    except Exception as e:
        print(f"❌ ERROR: Unexpected error during initialization")
        print(f"   {type(e).__name__}: {str(e)}")
        return 1
    
    # Send test email
    test_subject = "🧪 Test Email from PPRA Tender Alerts"
    test_body = (
        "This is a test email to verify Gmail SMTP email notifications.\n\n"
        "If you received this email, the integration is working correctly! ✅\n\n"
        "You can now use the EmailNotifier class to send tender alerts via email."
    )
    
    print("Sending test email...")
    print(f"To: {to_email}")
    print(f"Subject: {test_subject}")
    print()
    
    try:
        result = notifier.send_email(to_email, test_subject, test_body)
        
        if result['success']:
            print("✅ SUCCESS: Email sent successfully!")
            print()
            print("📧 Check your email inbox (and spam folder) to confirm receipt of the message.")
            print()
            print("Note: If you don't receive the email, check:")
            print("  1. Your Gmail App Password is correct (16 characters)")
            print("  2. 2-Step Verification is enabled on your Google account")
            print("  3. The recipient email address is correct")
            print("  4. Check your spam/junk folder")
            print("  5. Your internet connection is working")
            return 0
        else:
            print("❌ ERROR: Failed to send email")
            print(f"   Error: {result['error']}")
            print()
            print("Troubleshooting tips:")
            print("  - Verify your Gmail App Password is correct (not your regular password)")
            print("  - Ensure 2-Step Verification is enabled on your Google account")
            print("  - Check that 'Less secure app access' is not required (App Passwords replace this)")
            print("  - Verify the recipient email address is valid")
            print("  - Check your internet connection")
            return 1
            
    except Exception as e:
        print(f"❌ ERROR: Unexpected error while sending email")
        print(f"   {type(e).__name__}: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

