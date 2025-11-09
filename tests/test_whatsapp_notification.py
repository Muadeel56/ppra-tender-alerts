#!/usr/bin/env python3
"""
Test WhatsApp Notification Script

This script tests WhatsApp message sending via Twilio sandbox.
It loads environment variables, initializes the WhatsApp notifier,
and sends a test message to verify the integration works correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import scraper modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scraper.notifications import WhatsAppNotifier


def main():
    """Main function to test WhatsApp notification sending."""
    # Load environment variables from .env file
    load_dotenv()
    
    print("=" * 60)
    print("WhatsApp Notification Test via Twilio Sandbox")
    print("=" * 60)
    print()
    
    # Check if required environment variables are set
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_WHATSAPP_FROM')
    to_number = os.getenv('TWILIO_WHATSAPP_TO')
    
    print("Checking environment variables...")
    if not account_sid:
        print("❌ ERROR: TWILIO_ACCOUNT_SID is not set in .env file")
        print("   Please add your Twilio Account SID to .env file")
        return 1
    
    if not auth_token:
        print("❌ ERROR: TWILIO_AUTH_TOKEN is not set in .env file")
        print("   Please add your Twilio Auth Token to .env file")
        return 1
    
    if not from_number:
        print("❌ ERROR: TWILIO_WHATSAPP_FROM is not set in .env file")
        print("   Please add your Twilio WhatsApp FROM number to .env file")
        print("   Format: whatsapp:+14155238886 (default Twilio sandbox number)")
        return 1
    
    if not to_number:
        print("❌ ERROR: TWILIO_WHATSAPP_TO is not set in .env file")
        print("   Please add recipient WhatsApp number to .env file")
        print("   Format: whatsapp:+1234567890")
        return 1
    
    print("✅ All required environment variables are set")
    print()
    
    # Initialize WhatsApp notifier
    print("Initializing WhatsApp notifier...")
    try:
        notifier = WhatsAppNotifier()
        print("✅ WhatsApp notifier initialized successfully")
        print(f"   From: {notifier.from_number}")
        print()
    except ValueError as e:
        print(f"❌ ERROR: Failed to initialize WhatsApp notifier")
        print(f"   {str(e)}")
        return 1
    except Exception as e:
        print(f"❌ ERROR: Unexpected error during initialization")
        print(f"   {type(e).__name__}: {str(e)}")
        return 1
    
    # Send test message
    test_message = (
        "🧪 Test Message from PPRA Tender Alerts\n\n"
        "This is a test message to verify WhatsApp notifications via Twilio sandbox.\n\n"
        "If you received this message, the integration is working correctly! ✅"
    )
    
    print("Sending test WhatsApp message...")
    print(f"To: {to_number}")
    print(f"Message: {test_message[:50]}...")
    print()
    
    try:
        result = notifier.send_message(to_number, test_message)
        
        if result['success']:
            print("✅ SUCCESS: WhatsApp message sent successfully!")
            print(f"   Message SID: {result['message_sid']}")
            print(f"   Status: {result['status']}")
            print()
            print("📱 Check your WhatsApp to confirm receipt of the message.")
            print()
            print("Note: If you don't receive the message, make sure:")
            print("  1. You have joined the Twilio sandbox by sending the join code")
            print("  2. The recipient number is correct and has WhatsApp")
            print("  3. Your Twilio account has sufficient credits")
            return 0
        else:
            print("❌ ERROR: Failed to send WhatsApp message")
            print(f"   Error: {result['error']}")
            print()
            print("Troubleshooting tips:")
            print("  - Verify your Twilio credentials are correct")
            print("  - Check that the recipient has joined the Twilio sandbox")
            print("  - Ensure phone numbers are in E.164 format with whatsapp: prefix")
            print("  - Check your Twilio account status and credits")
            return 1
            
    except Exception as e:
        print(f"❌ ERROR: Unexpected error while sending message")
        print(f"   {type(e).__name__}: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

