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
import logging
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.ppra_scraper import PPRAScraper
from scraper.tender_storage import load_tenders, save_tenders, merge_tenders, get_tenders_filepath, normalize_tender_number, is_duplicate
from scraper.notifications import WhatsAppNotifier, EmailNotifier


def setup_logging() -> logging.Logger:
    """
    Set up file-based logging with daily log rotation.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get project root directory (parent of backend)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_dir)
    logs_dir = os.path.join(project_root, 'logs')
    
    # Create logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create log file with date suffix
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'automated_monitor_{date_str}.log'
    log_filepath = os.path.join(logs_dir, log_filename)
    
    # Configure logger
    logger = logging.getLogger('AutomatedTenderMonitor')
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


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
        
        # Set up logging
        self.logger = setup_logging()
        self.logger.info("=" * 70)
        self.logger.info("Automated Tender Monitor - Initializing")
        self.logger.info("=" * 70)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize notifiers (will raise ValueError if credentials missing)
        try:
            self.whatsapp_notifier = WhatsAppNotifier() if whatsapp_to or os.getenv('TWILIO_WHATSAPP_TO') else None
            self.whatsapp_to = whatsapp_to or os.getenv('TWILIO_WHATSAPP_TO')
            if self.whatsapp_notifier:
                self.logger.info(f"WhatsApp notifier initialized (to: {self.whatsapp_to})")
        except ValueError:
            print("⚠️  WhatsApp notifier not available (credentials missing)")
            self.logger.warning("WhatsApp notifier not available (credentials missing)")
            self.whatsapp_notifier = None
            self.whatsapp_to = None
        
        try:
            self.email_notifier = EmailNotifier() if email_to or os.getenv('GMAIL_SMTP_TO') or os.getenv('GMAIL_SMTP_USER') else None
            self.email_to = email_to or os.getenv('GMAIL_SMTP_TO') or os.getenv('GMAIL_SMTP_USER')
            if self.email_notifier:
                self.logger.info(f"Email notifier initialized (to: {self.email_to})")
        except ValueError:
            print("⚠️  Email notifier not available (credentials missing)")
            self.logger.warning("Email notifier not available (credentials missing)")
            self.email_notifier = None
            self.email_to = None
        
        if not self.whatsapp_notifier and not self.email_notifier:
            error_msg = "At least one notification method (WhatsApp or Email) must be configured"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if self.city_name:
            self.logger.info(f"City filter configured: {self.city_name}")
        else:
            self.logger.info("No city filter - will scrape all tenders")
    
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
        self.logger.info("=" * 70)
        self.logger.info("Step 1: Scraping Tenders from PPRA Website")
        self.logger.info("=" * 70)
        
        try:
            # Initialize scraper
            print(f"Initializing scraper (headless={self.headless})...")
            self.logger.info(f"Initializing scraper (headless={self.headless})")
            self.scraper = PPRAScraper(headless=self.headless, timeout=30)
            self.scraper.start()
            print("✅ Scraper initialized")
            print()
            self.logger.info("Scraper initialized successfully")
            
            # Apply city filter if specified
            if self.city_name:
                print(f"Applying city filter: {self.city_name}...")
                self.logger.info(f"Applying city filter: {self.city_name}")
                if not self.scraper.apply_city_filter(self.city_name):
                    print(f"⚠️  Warning: Failed to apply city filter for {self.city_name}")
                    print("   Continuing with all tenders...")
                    self.logger.warning(f"Failed to apply city filter for {self.city_name}, continuing with all tenders")
                else:
                    print(f"✅ City filter applied: {self.city_name}")
                    self.logger.info(f"City filter applied successfully: {self.city_name}")
                print()
            
            # Extract tender data
            print("Extracting tender data from website...")
            self.logger.info("Extracting tender data from website")
            tenders = self.scraper.extract_tender_data()
            print(f"✅ Extracted {len(tenders)} tenders")
            print()
            self.logger.info(f"Extracted {len(tenders)} tenders")
            
            if len(tenders) == 0:
                print("⚠️  No tenders found. This may be expected if there are no active tenders.")
                self.logger.warning("No tenders found - this may be expected if there are no active tenders")
                return []
            
            # Display sample
            if len(tenders) > 0:
                print("Sample tender:")
                sample = tenders[0]
                print(f"  Title: {sample.get('tender_title', 'N/A')[:60]}...")
                print(f"  Number: {sample.get('tender_number', 'N/A')}")
                print(f"  Closing Date: {sample.get('closing_date', 'N/A')}")
                print()
                self.logger.info(f"Sample tender: {sample.get('tender_title', 'N/A')[:60]}... (Number: {sample.get('tender_number', 'N/A')})")
            
            return tenders
            
        except Exception as e:
            error_msg = f"Error during scraping: {type(e).__name__}: {str(e)}"
            print(f"❌ {error_msg}")
            self.logger.error(error_msg, exc_info=True)
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
        self.logger.info("=" * 70)
        self.logger.info("Step 2: Detecting New Tenders")
        self.logger.info("=" * 70)
        
        # Load existing tenders
        filepath = get_tenders_filepath()
        print(f"Loading existing tenders from: {filepath}")
        self.logger.info(f"Loading existing tenders from: {filepath}")
        existing_tenders = load_tenders(filepath)
        print(f"✅ Found {len(existing_tenders)} existing tenders in storage")
        print()
        self.logger.info(f"Found {len(existing_tenders)} existing tenders in storage")
        
        # Merge to find new ones
        print("Comparing scraped tenders with existing ones...")
        self.logger.info("Comparing scraped tenders with existing ones")
        merged_tenders, new_count = merge_tenders(existing_tenders, scraped_tenders)
        
        print(f"✅ Comparison complete:")
        print(f"   - Total scraped: {len(scraped_tenders)}")
        print(f"   - New tenders found: {new_count}")
        print(f"   - Duplicates skipped: {len(scraped_tenders) - new_count}")
        print()
        self.logger.info(f"Comparison complete - Total scraped: {len(scraped_tenders)}, New: {new_count}, Duplicates: {len(scraped_tenders) - new_count}")
        
        if new_count == 0:
            print("ℹ️  No new tenders found. All scraped tenders already exist in storage.")
            self.logger.info("No new tenders found - all scraped tenders already exist in storage")
            return []
        
        # Extract only the new tenders using normalized comparison
        # This ensures proper handling of malformed tender numbers
        new_tenders = []
        seen_normalized_numbers = set()  # Track normalized numbers to avoid duplicates in new_tenders list
        
        for tender in scraped_tenders:
            # Use is_duplicate() which handles normalization properly
            if not is_duplicate(tender, existing_tenders):
                # Also check if we've already added this tender in this batch
                tender_number = normalize_tender_number(tender.get('tender_number', ''))
                if tender_number and tender_number not in seen_normalized_numbers:
                    new_tenders.append(tender)
                    seen_normalized_numbers.add(tender_number)
                elif not tender_number:
                    # Tender without a valid number - treat as new but log warning
                    warning_msg = f"Tender without valid tender_number detected: {tender.get('tender_title', 'N/A')[:50]}..."
                    print(f"   ⚠️  Warning: {warning_msg}")
                    self.logger.warning(warning_msg)
                    new_tenders.append(tender)
        
        if len(new_tenders) != new_count:
            warning_msg = f"Expected {new_count} new tenders but found {len(new_tenders)} after normalization"
            print(f"   ⚠️  Warning: {warning_msg}")
            self.logger.warning(warning_msg)
        
        print(f"📋 New tenders to notify:")
        self.logger.info(f"Found {len(new_tenders)} new tenders to notify")
        for i, tender in enumerate(new_tenders, 1):
            tender_num = normalize_tender_number(tender.get('tender_number', '')) or 'N/A'
            tender_info = f"{i}. {tender.get('tender_title', 'N/A')[:50]}... (Number: {tender_num}, Closes: {tender.get('closing_date', 'N/A')})"
            print(f"   {tender_info}")
            self.logger.info(f"New tender {i}: {tender.get('tender_title', 'N/A')[:50]}... (Number: {tender_num})")
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
        self.logger.info("=" * 70)
        self.logger.info("Step 3: Sending Notifications for New Tenders")
        self.logger.info("=" * 70)
        
        stats = {
            'whatsapp_sent': 0,
            'whatsapp_failed': 0,
            'email_sent': 0,
            'email_failed': 0
        }
        
        for i, tender in enumerate(new_tenders, 1):
            tender_title = tender.get('tender_title', 'N/A')[:60]
            print(f"[{i}/{len(new_tenders)}] Sending notifications for:")
            print(f"   Title: {tender_title}...")
            print()
            self.logger.info(f"[{i}/{len(new_tenders)}] Sending notifications for: {tender_title}...")
            
            # Send WhatsApp notification
            if self.whatsapp_notifier and self.whatsapp_to:
                try:
                    result = self.whatsapp_notifier.send_tender_alert(self.whatsapp_to, tender)
                    if result['success']:
                        msg_sid = result.get('message_sid', 'N/A')[:20]
                        print(f"   ✅ WhatsApp: Sent (SID: {msg_sid}...)")
                        self.logger.info(f"WhatsApp notification sent successfully (SID: {msg_sid})")
                        stats['whatsapp_sent'] += 1
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        print(f"   ❌ WhatsApp: Failed - {error_msg}")
                        self.logger.error(f"WhatsApp notification failed: {error_msg}")
                        stats['whatsapp_failed'] += 1
                except Exception as e:
                    error_msg = str(e)
                    print(f"   ❌ WhatsApp: Error - {error_msg}")
                    self.logger.error(f"WhatsApp notification error: {error_msg}", exc_info=True)
                    stats['whatsapp_failed'] += 1
            else:
                print(f"   ⏭️  WhatsApp: Skipped (not configured)")
                self.logger.info("WhatsApp notification skipped (not configured)")
            
            # Send Email notification
            if self.email_notifier and self.email_to:
                try:
                    result = self.email_notifier.send_tender_alert(self.email_to, tender)
                    if result['success']:
                        print(f"   ✅ Email: Sent to {self.email_to}")
                        self.logger.info(f"Email notification sent successfully to {self.email_to}")
                        stats['email_sent'] += 1
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        print(f"   ❌ Email: Failed - {error_msg}")
                        self.logger.error(f"Email notification failed: {error_msg}")
                        stats['email_failed'] += 1
                except Exception as e:
                    error_msg = str(e)
                    print(f"   ❌ Email: Error - {error_msg}")
                    self.logger.error(f"Email notification error: {error_msg}", exc_info=True)
                    stats['email_failed'] += 1
            else:
                print(f"   ⏭️  Email: Skipped (not configured)")
                self.logger.info("Email notification skipped (not configured)")
            
            print()
        
        self.logger.info(f"Notification summary - WhatsApp: {stats['whatsapp_sent']} sent, {stats['whatsapp_failed']} failed; Email: {stats['email_sent']} sent, {stats['email_failed']} failed")
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
        self.logger.info("=" * 70)
        self.logger.info("Step 4: Saving New Tenders to Storage")
        self.logger.info("=" * 70)
        
        filepath = get_tenders_filepath()
        self.logger.info(f"Saving to: {filepath}")
        existing_tenders = load_tenders(filepath)
        merged_tenders, _ = merge_tenders(existing_tenders, new_tenders)
        
        if save_tenders(merged_tenders, filepath):
            print(f"✅ Successfully saved {len(new_tenders)} new tenders to {filepath}")
            print(f"   Total tenders in storage: {len(merged_tenders)}")
            print()
            self.logger.info(f"Successfully saved {len(new_tenders)} new tenders to {filepath} (Total: {len(merged_tenders)})")
            return True
        else:
            print(f"❌ Failed to save tenders to {filepath}")
            print()
            self.logger.error(f"Failed to save tenders to {filepath}")
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
        self.logger.info("=" * 70)
        self.logger.info("Automated Tender Monitor - Starting")
        self.logger.info("=" * 70)
        
        try:
            # Step 1: Scrape
            scraped_tenders = self.scrape_tenders()
            
            if not scraped_tenders:
                result = {
                    'success': True,
                    'scraped_count': 0,
                    'new_count': 0,
                    'notifications_sent': 0,
                    'message': 'No tenders found to process'
                }
                self.logger.info("Run completed - No tenders found to process")
                return result
            
            # Step 2: Detect new tenders
            new_tenders = self.detect_new_tenders(scraped_tenders)
            
            # Step 3: Send notifications
            notification_stats = self.send_notifications(new_tenders)
            
            # Step 4: Save new tenders after sending notifications
            # We save regardless of notification success to mark tenders as "seen"
            # This prevents re-sending the same tenders on subsequent runs
            save_success = self.save_new_tenders(new_tenders)
            
            # Log warning if notifications failed but we're still saving
            total_notifications_attempted = notification_stats['whatsapp_sent'] + notification_stats['email_sent']
            total_notifications_failed = notification_stats['whatsapp_failed'] + notification_stats['email_failed']
            
            if len(new_tenders) > 0 and total_notifications_failed > 0:
                if total_notifications_attempted == 0:
                    warning_msg = "All notifications failed, but tenders are saved to prevent re-sending"
                    print(f"⚠️  Note: {warning_msg}")
                    self.logger.warning(warning_msg)
                else:
                    warning_msg = f"{total_notifications_failed} notification(s) failed, but tenders are saved"
                    print(f"⚠️  Note: {warning_msg}")
                    self.logger.warning(warning_msg)
            
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
            
            summary_msg = (
                f"Run completed successfully - Scraped: {len(scraped_tenders)}, "
                f"New: {len(new_tenders)}, WhatsApp: {notification_stats['whatsapp_sent']} sent/{notification_stats['whatsapp_failed']} failed, "
                f"Email: {notification_stats['email_sent']} sent/{notification_stats['email_failed']} failed, "
                f"Storage: {'Saved' if save_success else 'Failed'}"
            )
            self.logger.info(summary_msg)
            
            return {
                'success': True,
                'scraped_count': len(scraped_tenders),
                'new_count': len(new_tenders),
                'notifications_sent': notification_stats['whatsapp_sent'] + notification_stats['email_sent'],
                'notification_stats': notification_stats,
                'save_success': save_success
            }
            
        except Exception as e:
            error_msg = f"Error in automated monitor: {type(e).__name__}: {str(e)}"
            print(f"\n❌ {error_msg}")
            self.logger.error(error_msg, exc_info=True)
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
                self.logger.info("Closing browser session")
                try:
                    self.scraper.close()
                    print("✅ Browser session closed")
                    self.logger.info("Browser session closed successfully")
                except Exception as e:
                    error_msg = f"Error closing browser: {str(e)}"
                    print(f"⚠️  {error_msg}")
                    self.logger.warning(error_msg, exc_info=True)


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
        error_msg = f"Configuration error: {str(e)}"
        print(f"❌ {error_msg}")
        # Try to log if logger exists (may not if error occurs before monitor init)
        try:
            logger = logging.getLogger('AutomatedTenderMonitor')
            if logger.handlers:
                logger.error(error_msg)
        except:
            pass
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        try:
            logger = logging.getLogger('AutomatedTenderMonitor')
            if logger.handlers:
                logger.warning("Interrupted by user")
        except:
            pass
        sys.exit(1)
    except Exception as e:
        error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        try:
            logger = logging.getLogger('AutomatedTenderMonitor')
            if logger.handlers:
                logger.error(error_msg, exc_info=True)
        except:
            pass
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

