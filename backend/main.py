#!/usr/bin/env python3
"""
Main Entry Point for PPRA Tender Alerts

This script executes the end-to-end workflow:
1. Scrape tenders from PPRA website
2. Compare with existing tenders to detect new ones
3. Send notifications (WhatsApp & Email) for new tenders

Usage:
    python main.py [--city CITY] [--whatsapp NUMBER] [--email ADDRESS] [--no-headless]
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add backend directory to path to allow imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from scraper.automated_tender_monitor import AutomatedTenderMonitor


def main():
    """
    Main entry point that runs the automated tender monitoring workflow.
    
    Executes: scrape -> compare -> send notifications automatically.
    """
    # Load environment variables
    load_dotenv()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="PPRA Tender Alerts - Automated Scraping and Notification System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (uses .env configuration)
  python main.py
  
  # Filter by city
  python main.py --city "Chakwal"
  
  # Specify notification recipients
  python main.py --whatsapp "whatsapp:+1234567890" --email "user@example.com"
  
  # Run with visible browser (for debugging)
  python main.py --no-headless
        """
    )
    
    parser.add_argument(
        '--city',
        type=str,
        default=None,
        metavar='CITY',
        help='City name to filter tenders (optional, scrapes all if not specified)'
    )
    parser.add_argument(
        '--whatsapp',
        type=str,
        default=None,
        metavar='NUMBER',
        help='WhatsApp number to send alerts (optional, uses TWILIO_WHATSAPP_TO from .env if not specified)'
    )
    parser.add_argument(
        '--email',
        type=str,
        default=None,
        metavar='ADDRESS',
        help='Email address to send alerts (optional, uses GMAIL_SMTP_TO or GMAIL_SMTP_USER from .env if not specified)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (default: headless)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize the automated monitor
        monitor = AutomatedTenderMonitor(
            city_name=args.city,
            whatsapp_to=args.whatsapp,
            email_to=args.email,
            headless=not args.no_headless
        )
        
        # Run the complete workflow: scrape -> compare -> send notifications
        result = monitor.run()
        
        # Exit with appropriate code based on success
        if result.get('success', False):
            sys.exit(0)
        else:
            print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except ValueError as e:
        print(f"\n❌ Configuration error: {str(e)}")
        print("\nPlease check your .env file or provide required credentials via command-line arguments.")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

