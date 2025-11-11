#!/usr/bin/env python3
"""
Automated Tender Monitor

This script implements the complete flow:
1. Scrapes tenders from PPRA website
2. Detects new tenders (compares with existing ones)
3. Sends notifications (WhatsApp & Email) for new tenders only

This is the main automation script that connects scraping to notifications.
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.ppra_scraper import PPRAScraper
from scraper.tender_storage import load_tenders, save_tenders, merge_tenders, get_tenders_filepath
from scraper.notifications import WhatsAppNotifier, EmailNotifier


class AutomatedTenderMonitor:
    """
    Automated monitor that scrapes, detects new tenders, and sends notifications.
    """
    
    def __init__(
        self,
        city_name: str = None,
        whatsapp_to: str = None,
        email_to: str = None,
        headless: bool = True
    ):
        """
        Initialize the automated monitor.
        
        Args:
            city_name (str, optional): City to filter tenders. If None, scrapes all tenders.
            whatsapp_to (str, optional): WhatsApp number to send alerts. If None, reads from env.
            email_to (str, optional): Email to send alerts. If None, reads from env.
            headless (bool): Run browser in headless mode. Defaults to True.
        """
        self.city_name = city_name
        self.headless = headless
        self.scraper = None
        
        # Load environment variables
        load_dotenv()
        
        # Initialize notifiers (will raise ValueError if credentials missing)
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
        Scrape tenders from PPRA website.
        
        Returns:
            List[Dict]: List of scraped tender dictionaries
        """
        print("=" * 70)
        print("Step 1: Scraping Tenders from PPRA Website")
        print("=" * 70)
        print()
        
        try:
            # Initialize scraper
            print(f"Initializing scraper (headless={self.headless})...")
            self.scraper = PPRAScraper(headless=self.headless, timeout=30)
            self.scraper.start()
            print("✅ Scraper initialized")
            print()
            
            # Apply city filter if specified
            if self.city_name:
                print(f"Applying city filter: {self.city_name}...")
                if not self.scraper.apply_city_filter(self.city_name):
                    print(f"⚠️  Warning: Failed to apply city filter for {self.city_name}")
                    print("   Continuing with all tenders...")
                else:
                    print(f"✅ City filter applied: {self.city_name}")
                print()
            
            # Extract tender data
            print("Extracting tender data from website...")
            tenders = self.scraper.extract_tender_data()
            print(f"✅ Extracted {len(tenders)} tenders")
            print()
            
            if len(tenders) == 0:
                print("⚠️  No tenders found. This may be expected if there are no active tenders.")
                return []
            
            # Display sample
            if len(tenders) > 0:
                print("Sample tender:")
                sample = tenders[0]
                print(f"  Title: {sample.get('tender_title', 'N/A')[:60]}...")
                print(f"  Number: {sample.get('tender_number', 'N/A')}")
                print(f"  Closing Date: {sample.get('closing_date', 'N/A')}")
                print()
            
            return tenders
            
        except Exception as e:
            print(f"❌ Error during scraping: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def detect_new_tenders(self, scraped_tenders: List[Dict]) -> List[Dict]:
        """
        Compare scraped tenders with existing ones to find new tenders.
        
        Args:
            scraped_tenders (List[Dict]): List of scraped tender dictionaries
            
        Returns:
            List[Dict]: List of new tender dictionaries (not in existing storage)
        """
        print("=" * 70)
        print("Step 2: Detecting New Tenders")
        print("=" * 70)
        print()
        
        # Load existing tenders
        filepath = get_tenders_filepath()
        print(f"Loading existing tenders from: {filepath}")
        existing_tenders = load_tenders(filepath)
        print(f"✅ Found {len(existing_tenders)} existing tenders in storage")
        print()
        
        # Merge to find new ones
        print("Comparing scraped tenders with existing ones...")
        merged_tenders, new_count = merge_tenders(existing_tenders, scraped_tenders)
        
        print(f"✅ Comparison complete:")
        print(f"   - Total scraped: {len(scraped_tenders)}")
        print(f"   - New tenders found: {new_count}")
        print(f"   - Duplicates skipped: {len(scraped_tenders) - new_count}")
        print()
        
        if new_count == 0:
            print("ℹ️  No new tenders found. All scraped tenders already exist in storage.")
            return []
        
        # Extract only the new tenders
        new_tenders = []
        existing_numbers = {str(t.get('tender_number', '')).strip().lower() for t in existing_tenders if t.get('tender_number')}
        
        for tender in scraped_tenders:
            tender_number = str(tender.get('tender_number', '')).strip().lower()
            if tender_number and tender_number not in existing_numbers:
                new_tenders.append(tender)
                existing_numbers.add(tender_number)  # Avoid duplicates in new_tenders
        
        print(f"📋 New tenders to notify:")
        for i, tender in enumerate(new_tenders, 1):
            print(f"   {i}. {tender.get('tender_title', 'N/A')[:50]}... (Closes: {tender.get('closing_date', 'N/A')})")
        print()
        
        return new_tenders
    
    def send_notifications(self, new_tenders: List[Dict]) -> Dict[str, int]:
        """
        Send notifications for new tenders via WhatsApp and/or Email.
        
        Args:
            new_tenders (List[Dict]): List of new tender dictionaries to notify about
            
        Returns:
            Dict[str, int]: Statistics about notifications sent
                - whatsapp_sent: Number of WhatsApp notifications sent
                - whatsapp_failed: Number of WhatsApp notifications failed
                - email_sent: Number of email notifications sent
                - email_failed: Number of email notifications failed
        """
        if not new_tenders:
            return {
                'whatsapp_sent': 0,
                'whatsapp_failed': 0,
                'email_sent': 0,
                'email_failed': 0
            }
        
        print("=" * 70)
        print("Step 3: Sending Notifications for New Tenders")
        print("=" * 70)
        print()
        
        stats = {
            'whatsapp_sent': 0,
            'whatsapp_failed': 0,
            'email_sent': 0,
            'email_failed': 0
        }
        
        for i, tender in enumerate(new_tenders, 1):
            print(f"[{i}/{len(new_tenders)}] Sending notifications for:")
            print(f"   Title: {tender.get('tender_title', 'N/A')[:60]}...")
            print()
            
            # Send WhatsApp notification
            if self.whatsapp_notifier and self.whatsapp_to:
                try:
                    result = self.whatsapp_notifier.send_tender_alert(self.whatsapp_to, tender)
                    if result['success']:
                        print(f"   ✅ WhatsApp: Sent (SID: {result.get('message_sid', 'N/A')[:20]}...)")
                        stats['whatsapp_sent'] += 1
                    else:
                        print(f"   ❌ WhatsApp: Failed - {result.get('error', 'Unknown error')}")
                        stats['whatsapp_failed'] += 1
                except Exception as e:
                    print(f"   ❌ WhatsApp: Error - {str(e)}")
                    stats['whatsapp_failed'] += 1
            else:
                print(f"   ⏭️  WhatsApp: Skipped (not configured)")
            
            # Send Email notification
            if self.email_notifier and self.email_to:
                try:
                    result = self.email_notifier.send_tender_alert(self.email_to, tender)
                    if result['success']:
                        print(f"   ✅ Email: Sent to {self.email_to}")
                        stats['email_sent'] += 1
                    else:
                        print(f"   ❌ Email: Failed - {result.get('error', 'Unknown error')}")
                        stats['email_failed'] += 1
                except Exception as e:
                    print(f"   ❌ Email: Error - {str(e)}")
                    stats['email_failed'] += 1
            else:
                print(f"   ⏭️  Email: Skipped (not configured)")
            
            print()
        
        return stats
    
    def save_new_tenders(self, new_tenders: List[Dict]) -> bool:
        """
        Save new tenders to storage file.
        
        Args:
            new_tenders (List[Dict]): List of new tender dictionaries to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not new_tenders:
            return True
        
        print("=" * 70)
        print("Step 4: Saving New Tenders to Storage")
        print("=" * 70)
        print()
        
        filepath = get_tenders_filepath()
        existing_tenders = load_tenders(filepath)
        merged_tenders, _ = merge_tenders(existing_tenders, new_tenders)
        
        if save_tenders(merged_tenders, filepath):
            print(f"✅ Successfully saved {len(new_tenders)} new tenders to {filepath}")
            print(f"   Total tenders in storage: {len(merged_tenders)}")
            print()
            return True
        else:
            print(f"❌ Failed to save tenders to {filepath}")
            print()
            return False
    
    def run(self) -> Dict:
        """
        Run the complete automated monitoring flow:
        1. Scrape tenders
        2. Detect new tenders
        3. Send notifications
        4. Save new tenders
        
        Returns:
            Dict: Summary of the run with statistics
        """
        print("\n" + "=" * 70)
        print("🤖 Automated Tender Monitor - Starting")
        print("=" * 70)
        print()
        
        try:
            # Step 1: Scrape
            scraped_tenders = self.scrape_tenders()
            
            if not scraped_tenders:
                return {
                    'success': True,
                    'scraped_count': 0,
                    'new_count': 0,
                    'notifications_sent': 0,
                    'message': 'No tenders found to process'
                }
            
            # Step 2: Detect new tenders
            new_tenders = self.detect_new_tenders(scraped_tenders)
            
            # Step 3: Send notifications
            notification_stats = self.send_notifications(new_tenders)
            
            # Step 4: Save new tenders
            save_success = self.save_new_tenders(new_tenders)
            
            # Summary
            print("=" * 70)
            print("📊 Summary")
            print("=" * 70)
            print(f"Tenders scraped: {len(scraped_tenders)}")
            print(f"New tenders found: {len(new_tenders)}")
            print(f"WhatsApp notifications: {notification_stats['whatsapp_sent']} sent, {notification_stats['whatsapp_failed']} failed")
            print(f"Email notifications: {notification_stats['email_sent']} sent, {notification_stats['email_failed']} failed")
            print(f"Storage: {'✅ Saved' if save_success else '❌ Failed'}")
            print()
            
            return {
                'success': True,
                'scraped_count': len(scraped_tenders),
                'new_count': len(new_tenders),
                'notifications_sent': notification_stats['whatsapp_sent'] + notification_stats['email_sent'],
                'notification_stats': notification_stats,
                'save_success': save_success
            }
            
        except Exception as e:
            print(f"\n❌ Error in automated monitor: {type(e).__name__}: {str(e)}")
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
        description="Automated Tender Monitor - Scrapes, detects new tenders, and sends notifications"
    )
    parser.add_argument(
        '--city',
        type=str,
        default=None,
        help='City name to filter tenders (optional, scrapes all if not specified)'
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
    
    args = parser.parse_args()
    
    try:
        monitor = AutomatedTenderMonitor(
            city_name=args.city,
            whatsapp_to=args.whatsapp,
            email_to=args.email,
            headless=not args.no_headless
        )
        
        result = monitor.run()
        
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

