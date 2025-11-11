#!/usr/bin/env python3
"""
Send All Active Tenders

This script scrapes ALL active tenders for a city and sends them
to WhatsApp and Gmail. Unlike the automated monitor, this sends
ALL tenders (not just new ones).

Useful for:
- Getting all current active tenders in a city
- Initial setup to receive all available tenders
- Periodic full updates
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.ppra_scraper import PPRAScraper
from scraper.notifications import WhatsAppNotifier, EmailNotifier


class AllTendersSender:
    """
    Scrapes and sends ALL active tenders for a city.
    """
    
    def __init__(
        self,
        city_name: str,
        whatsapp_to: str = None,
        email_to: str = None,
        headless: bool = True
    ):
        """
        Initialize the sender.
        
        Args:
            city_name (str): City to filter tenders (required)
            whatsapp_to (str, optional): WhatsApp number. If None, reads from env.
            email_to (str, optional): Email address. If None, reads from env.
            headless (bool): Run browser in headless mode. Defaults to True.
        """
        if not city_name:
            raise ValueError("city_name is required")
        
        self.city_name = city_name
        self.headless = headless
        self.scraper = None
        
        # Load environment variables
        load_dotenv()
        
        # Initialize notifiers
        try:
            self.whatsapp_notifier = WhatsAppNotifier() if whatsapp_to or os.getenv('TWILIO_WHATSAPP_TO') else None
            self.whatsapp_to = whatsapp_to or os.getenv('TWILIO_WHATSAPP_TO')
        except ValueError:
            print("⚠️  WhatsApp notifier not available (credentials missing)")
            self.whatsapp_notifier = None
            self.whatsapp_to = None
        
        try:
            self.email_notifier = EmailNotifier() if email_to or os.getenv('GMAIL_SMTP_TO') or os.getenv('GMAIL_SMTP_USER') else None
            self.email_to = email_to or os.getenv('GMAIL_SMTP_TO') or os.getenv('GMAIL_SMTP_USER')
        except ValueError:
            print("⚠️  Email notifier not available (credentials missing)")
            self.email_notifier = None
            self.email_to = None
        
        if not self.whatsapp_notifier and not self.email_notifier:
            raise ValueError("At least one notification method (WhatsApp or Email) must be configured")
    
    def scrape_tenders(self) -> List[Dict]:
        """
        Scrape all active tenders for the specified city.
        
        Returns:
            List[Dict]: List of all scraped tender dictionaries
        """
        print("=" * 70)
        print(f"Scraping ALL Active Tenders for {self.city_name}")
        print("=" * 70)
        print()
        
        try:
            # Initialize scraper
            print(f"Initializing scraper (headless={self.headless})...")
            self.scraper = PPRAScraper(headless=self.headless, timeout=30)
            self.scraper.start()
            print("✅ Scraper initialized")
            print()
            
            # Apply city filter
            print(f"Applying city filter: {self.city_name}...")
            if not self.scraper.apply_city_filter(self.city_name):
                print(f"❌ Failed to apply city filter for {self.city_name}")
                return []
            print(f"✅ City filter applied: {self.city_name}")
            print()
            
            # Extract tender data
            print("Extracting tender data from website...")
            tenders = self.scraper.extract_tender_data()
            print(f"✅ Extracted {len(tenders)} active tenders for {self.city_name}")
            print()
            
            if len(tenders) == 0:
                print(f"⚠️  No active tenders found for {self.city_name}.")
                return []
            
            # Display summary
            print("Summary of tenders found:")
            for i, tender in enumerate(tenders[:5], 1):  # Show first 5
                print(f"  {i}. {tender.get('tender_title', 'N/A')[:60]}...")
                print(f"     Closing: {tender.get('closing_date', 'N/A')}")
            if len(tenders) > 5:
                print(f"  ... and {len(tenders) - 5} more")
            print()
            
            return tenders
            
        except Exception as e:
            print(f"❌ Error during scraping: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def send_all_notifications(self, tenders: List[Dict]) -> Dict[str, int]:
        """
        Send notifications for ALL tenders via WhatsApp and/or Email.
        
        Args:
            tenders (List[Dict]): List of all tender dictionaries to notify about
            
        Returns:
            Dict[str, int]: Statistics about notifications sent
        """
        if not tenders:
            return {
                'whatsapp_sent': 0,
                'whatsapp_failed': 0,
                'email_sent': 0,
                'email_failed': 0
            }
        
        print("=" * 70)
        print(f"Sending Notifications for ALL {len(tenders)} Tenders")
        print("=" * 70)
        print()
        
        # Ask for confirmation if many tenders
        if len(tenders) > 10:
            print(f"⚠️  WARNING: You are about to send {len(tenders)} notifications!")
            print("   This may take a while and use your Twilio/Gmail quota.")
            print()
            try:
                response = input("Continue? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    print("❌ Cancelled by user.")
                    return {
                        'whatsapp_sent': 0,
                        'whatsapp_failed': 0,
                        'email_sent': 0,
                        'email_failed': 0
                    }
            except EOFError:
                # Non-interactive mode, proceed anyway
                pass
            print()
        
        stats = {
            'whatsapp_sent': 0,
            'whatsapp_failed': 0,
            'email_sent': 0,
            'email_failed': 0
        }
        
        for i, tender in enumerate(tenders, 1):
            print(f"[{i}/{len(tenders)}] Sending notifications:")
            print(f"   Title: {tender.get('tender_title', 'N/A')[:60]}...")
            print(f"   Closing: {tender.get('closing_date', 'N/A')}")
            
            # Send WhatsApp notification
            if self.whatsapp_notifier and self.whatsapp_to:
                try:
                    result = self.whatsapp_notifier.send_tender_alert(self.whatsapp_to, tender)
                    if result['success']:
                        print(f"   ✅ WhatsApp: Sent")
                        stats['whatsapp_sent'] += 1
                    else:
                        print(f"   ❌ WhatsApp: Failed - {result.get('error', 'Unknown error')[:50]}")
                        stats['whatsapp_failed'] += 1
                except Exception as e:
                    print(f"   ❌ WhatsApp: Error - {str(e)[:50]}")
                    stats['whatsapp_failed'] += 1
            else:
                print(f"   ⏭️  WhatsApp: Skipped (not configured)")
            
            # Send Email notification
            if self.email_notifier and self.email_to:
                try:
                    result = self.email_notifier.send_tender_alert(self.email_to, tender)
                    if result['success']:
                        print(f"   ✅ Email: Sent")
                        stats['email_sent'] += 1
                    else:
                        print(f"   ❌ Email: Failed - {result.get('error', 'Unknown error')[:50]}")
                        stats['email_failed'] += 1
                except Exception as e:
                    print(f"   ❌ Email: Error - {str(e)[:50]}")
                    stats['email_failed'] += 1
            else:
                print(f"   ⏭️  Email: Skipped (not configured)")
            
            print()
            
            # Small delay to avoid rate limiting
            if i < len(tenders):
                import time
                time.sleep(1)  # 1 second delay between notifications
        
        return stats
    
    def run(self) -> Dict:
        """
        Run the complete flow: scrape all tenders and send notifications.
        
        Returns:
            Dict: Summary of the run with statistics
        """
        print("\n" + "=" * 70)
        print(f"📨 Send All Active Tenders - {self.city_name}")
        print("=" * 70)
        print()
        
        try:
            # Step 1: Scrape all tenders
            tenders = self.scrape_tenders()
            
            if not tenders:
                return {
                    'success': True,
                    'tenders_count': 0,
                    'notifications_sent': 0,
                    'message': f'No active tenders found for {self.city_name}'
                }
            
            # Step 2: Send notifications for all
            notification_stats = self.send_all_notifications(tenders)
            
            # Summary
            print("=" * 70)
            print("📊 Summary")
            print("=" * 70)
            print(f"City: {self.city_name}")
            print(f"Total tenders scraped: {len(tenders)}")
            print(f"WhatsApp notifications: {notification_stats['whatsapp_sent']} sent, {notification_stats['whatsapp_failed']} failed")
            print(f"Email notifications: {notification_stats['email_sent']} sent, {notification_stats['email_failed']} failed")
            print()
            
            return {
                'success': True,
                'city': self.city_name,
                'tenders_count': len(tenders),
                'notifications_sent': notification_stats['whatsapp_sent'] + notification_stats['email_sent'],
                'notification_stats': notification_stats
            }
            
        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            # Cleanup
            if self.scraper:
                print("\n[Cleanup] Closing browser session...")
                try:
                    self.scraper.close()
                    print("✅ Browser session closed")
                except Exception as e:
                    print(f"⚠️  Error closing browser: {str(e)}")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scrape and send ALL active tenders for a city to WhatsApp and Email"
    )
    parser.add_argument(
        'city',
        type=str,
        help='City name to scrape (e.g., "Islamabad", "Lahore", "Karachi")'
    )
    parser.add_argument(
        '--whatsapp',
        type=str,
        default=None,
        help='WhatsApp number to send alerts (optional, uses TWILIO_WHATSAPP_TO from .env if not specified)'
    )
    parser.add_argument(
        '--email',
        type=str,
        default=None,
        help='Email address to send alerts (optional, uses GMAIL_SMTP_TO or GMAIL_SMTP_USER from .env if not specified)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (default: headless)'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt (useful for automation)'
    )
    
    args = parser.parse_args()
    
    try:
        sender = AllTendersSender(
            city_name=args.city,
            whatsapp_to=args.whatsapp,
            email_to=args.email,
            headless=not args.no_headless
        )
        
        result = sender.run()
        
        sys.exit(0 if result.get('success', False) else 1)
        
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

