"""
Notifications Module

This module provides functionality to send WhatsApp messages via Twilio sandbox
and email notifications via SMTP, including error handling and environment
variable management.
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class WhatsAppNotifier:
    """
    WhatsApp notification sender using Twilio sandbox.
    
    Provides methods to send WhatsApp messages via Twilio's WhatsApp sandbox.
    Requires Twilio credentials to be set in environment variables.
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        """
        Initialize the WhatsApp notifier with Twilio credentials.
        
        Args:
            account_sid (Optional[str]): Twilio Account SID. If None, reads from TWILIO_ACCOUNT_SID env var.
            auth_token (Optional[str]): Twilio Auth Token. If None, reads from TWILIO_AUTH_TOKEN env var.
            from_number (Optional[str]): Twilio WhatsApp FROM number. If None, reads from TWILIO_WHATSAPP_FROM env var.
                                        Should be in format: whatsapp:+14155238886
        
        Raises:
            ValueError: If required credentials are missing
        """
        # Get credentials from parameters or environment variables
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = from_number or os.getenv('TWILIO_WHATSAPP_FROM')
        
        # Validate required credentials
        if not self.account_sid:
            raise ValueError("TWILIO_ACCOUNT_SID is required. Set it in .env file or pass as parameter.")
        if not self.auth_token:
            raise ValueError("TWILIO_AUTH_TOKEN is required. Set it in .env file or pass as parameter.")
        if not self.from_number:
            raise ValueError("TWILIO_WHATSAPP_FROM is required. Set it in .env file or pass as parameter.")
        
        # Ensure from_number has whatsapp: prefix
        if not self.from_number.startswith('whatsapp:'):
            self.from_number = f'whatsapp:{self.from_number}'
        
        # Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            raise ValueError(f"Failed to initialize Twilio client: {str(e)}")
    
    def send_message(
        self,
        to_number: str,
        message: str
    ) -> dict:
        """
        Send a WhatsApp message via Twilio sandbox.
        
        Args:
            to_number (str): Recipient WhatsApp number. Should be in format: whatsapp:+1234567890
                           If missing 'whatsapp:' prefix, it will be added automatically.
            message (str): Message content to send
        
        Returns:
            dict: Dictionary with success status and message details:
                - success (bool): True if message was sent successfully
                - message_sid (str): Twilio message SID if successful, None otherwise
                - error (str): Error message if failed, None otherwise
        
        Raises:
            ValueError: If to_number or message is empty
        """
        if not to_number:
            raise ValueError("to_number cannot be empty")
        if not message:
            raise ValueError("message cannot be empty")
        
        # Ensure to_number has whatsapp: prefix
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        try:
            # Send message via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                'success': True,
                'message_sid': twilio_message.sid,
                'status': twilio_message.status,
                'error': None
            }
            
        except TwilioRestException as e:
            return {
                'success': False,
                'message_sid': None,
                'status': None,
                'error': f"Twilio API error: {e.msg} (Code: {e.code})"
            }
        except TwilioException as e:
            return {
                'success': False,
                'message_sid': None,
                'status': None,
                'error': f"Twilio error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'message_sid': None,
                'status': None,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def send_tender_alert(
        self,
        to_number: str,
        tender_data: dict
    ) -> dict:
        """
        Send a formatted tender alert message via WhatsApp.
        
        Args:
            to_number (str): Recipient WhatsApp number
            tender_data (dict): Dictionary containing tender information with keys:
                - tender_title (str)
                - category (str, optional)
                - department_owner (str, optional)
                - closing_date (str, optional)
                - tender_number (str, optional)
                - pdf_links (list, optional)
        
        Returns:
            dict: Result from send_message() method
        """
        # Format tender alert message
        message_parts = ["🔔 *New Tender Alert*"]
        
        if tender_data.get('tender_title'):
            message_parts.append(f"\n*Title:* {tender_data['tender_title']}")
        
        if tender_data.get('tender_number'):
            message_parts.append(f"*Tender No:* {tender_data['tender_number']}")
        
        if tender_data.get('category'):
            message_parts.append(f"*Category:* {tender_data['category']}")
        
        if tender_data.get('department_owner'):
            message_parts.append(f"*Department:* {tender_data['department_owner']}")
        
        if tender_data.get('closing_date'):
            message_parts.append(f"*Closing Date:* {tender_data['closing_date']}")
        
        if tender_data.get('pdf_links') and len(tender_data['pdf_links']) > 0:
            message_parts.append(f"\n*PDF Links:* {len(tender_data['pdf_links'])} available")
            for i, link in enumerate(tender_data['pdf_links'][:3], 1):  # Limit to first 3 links
                message_parts.append(f"{i}. {link}")
        
        message = "\n".join(message_parts)
        
        return self.send_message(to_number, message)


def send_email_notification(recipient_email: str, subject: str, body: str) -> bool:
    """
    Sends an email notification via SMTP.

    Retrieves SMTP configuration (sender email, app password, host, port)
    from environment variables.

    Args:
        recipient_email (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The body content of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_app_password = os.getenv("SENDER_APP_PASSWORD")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))  # Default to 587 if not set

    if not all([sender_email, sender_app_password, smtp_host]):
        print("Error: SMTP environment variables (SENDER_EMAIL, SENDER_APP_PASSWORD, SMTP_HOST) are not all set.")
        return False

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Create the email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        print(f"Attempting to send email to {recipient_email} from {sender_email} via {smtp_host}:{smtp_port}...")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=context)  # Secure the connection
            server.login(sender_email, sender_app_password)
            server.send_message(msg)
        print("Email sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP authentication failed. Check SENDER_EMAIL and SENDER_APP_PASSWORD.")
        print("If using Gmail, ensure 'Less secure app access' is enabled or an App Password is used.")
        return False
    except smtplib.SMTPServerDisconnected:
        print("Error: SMTP server disconnected unexpectedly. Check SMTP_HOST and SMTP_PORT.")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"Error: Could not connect to SMTP server. Check SMTP_HOST and SMTP_PORT. Details: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while sending email: {e}")
        return False


if __name__ == '__main__':
    print("--- Running Notifications Test ---")

    # Test WhatsApp Notifier (if configured)
    try:
        wa_notifier = WhatsAppNotifier()
        test_wa_recipient = os.getenv('TEST_WHATSAPP_RECIPIENT_NUMBER')
        if test_wa_recipient:
            print(f"\nAttempting to send WhatsApp test message to {test_wa_recipient}...")
            wa_result = wa_notifier.send_message(
                to_number=test_wa_recipient,
                message="This is a test WhatsApp notification from the scraper backend!"
            )
            if wa_result['success']:
                print(f"WhatsApp message sent! SID: {wa_result['message_sid']}")
            else:
                print(f"Failed to send WhatsApp message: {wa_result['error']}")
        else:
            print("\nSkipping WhatsApp test: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, or TEST_WHATSAPP_RECIPIENT_NUMBER not fully set in .env")
    except ValueError as e:
        print(f"\nSkipping WhatsApp test due to configuration error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during WhatsApp test setup: {e}")


    # Test Email Notification
    print("\n--- Testing Email Notification ---")
    test_recipient_email = os.getenv("TEST_RECIPIENT_EMAIL")
    if test_recipient_email:
        test_subject = "Test Email Notification from Backend Scraper"
        test_body = """
Hello from the Backend Scraper!

This is a test email sent from the `notifications.py` module to verify SMTP functionality.
If you received this, the email setup is working correctly.

Best regards,
Your Backend Scraper
"""
        email_sent = send_email_notification(test_recipient_email, test_subject, test_body)
        if email_sent:
            print("Test email function executed. Check recipient's inbox.")
        else:
            print("Test email function failed to send email. See logs above for details.")
    else:
        print("Skipping email test: TEST_RECIPIENT_EMAIL environment variable not set.")

    print("\n--- To set up and test notifications: ---")
    print("1. Ensure 'python-dotenv' is installed (it should be in requirements.txt): `pip install -r backend/requirements.txt`")
    print("2. Create a `.env` file in the `backend/` directory with the following variables:")
    print("   For Email Notifications:")
    print("   SENDER_EMAIL='your_sender_email@example.com'")
    print("   SENDER_APP_PASSWORD='your_email_app_password' # For Gmail, generate an app password (not your main password).")
    print("   SMTP_HOST='smtp.gmail.com' # Or your email provider's SMTP host (e.g., 'smtp.mail.yahoo.com')")
    print("   SMTP_PORT=587 # Or your email provider's SMTP port (e.g., 465 for SSL, 587 for TLS/STARTTLS)")
    print("   TEST_RECIPIENT_EMAIL='recipient_for_test@example.com'")
    print("\n   For WhatsApp Notifications (optional, if you want to test WhatsApp):")
    print("   TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'")
    print("   TWILIO_AUTH_TOKEN='your_auth_token'")
    print("   TWILIO_WHATSAPP_FROM='whatsapp:+14155238886' # Your Twilio Sandbox number, including 'whatsapp:' prefix")
    print("   TEST_WHATSAPP_RECIPIENT_NUMBER='whatsapp:+1234567890' # Your WhatsApp number for testing, including 'whatsapp:' prefix")
    print("\n3. Run this script: `python backend/scraper/notifications.py`")