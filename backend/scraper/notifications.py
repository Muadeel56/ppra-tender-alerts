"""
Notifications Module

This module provides functionality to send notifications via WhatsApp (Twilio sandbox)
and Email (Gmail SMTP), including error handling and environment variable management.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_primary_link(tender_data: dict) -> str:
    """
    Get the primary link from tender data.
    
    Args:
        tender_data (dict): Dictionary containing tender information
        
    Returns:
        str: First PDF link if available, otherwise "N/A"
    """
    pdf_links = tender_data.get('pdf_links', [])
    if pdf_links and len(pdf_links) > 0:
        return pdf_links[0]
    return "N/A"


def format_deliverables(tender_data: dict) -> str:
    """
    Format deliverables field from tender data.
    
    Args:
        tender_data (dict): Dictionary containing tender information
        
    Returns:
        str: Deliverables if available, otherwise "N/A"
    """
    deliverables = tender_data.get('deliverables')
    if deliverables:
        if isinstance(deliverables, str):
            return deliverables.strip() if deliverables.strip() else "N/A"
        elif isinstance(deliverables, list):
            return ", ".join(str(d) for d in deliverables) if deliverables else "N/A"
        return str(deliverables)
    return "N/A"


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
                - pdf_links (list, optional)
                - deliverables (str or list, optional)
        
        Returns:
            dict: Result from send_message() method
        """
        # Format tender alert message with required fields
        message_parts = []
        
        # Tender Title
        title = tender_data.get('tender_title', '').strip()
        if title:
            message_parts.append(f"Tender Title: {title}")
        else:
            message_parts.append("Tender Title: N/A")
        
        # Category
        category = tender_data.get('category', '').strip()
        if category:
            message_parts.append(f"Category: {category}")
        else:
            message_parts.append("Category: N/A")
        
        # Department
        department = tender_data.get('department_owner', '').strip()
        if department:
            message_parts.append(f"Department: {department}")
        else:
            message_parts.append("Department: N/A")
        
        # Closing Date
        closing_date = tender_data.get('closing_date', '').strip()
        if closing_date:
            message_parts.append(f"Closing Date: {closing_date}")
        else:
            message_parts.append("Closing Date: N/A")
        
        # Link
        link = get_primary_link(tender_data)
        message_parts.append(f"Link: {link}")
        
        # Deliverables
        deliverables = format_deliverables(tender_data)
        message_parts.append(f"Deliverables: {deliverables}")
        
        message = "\n".join(message_parts)
        
        return self.send_message(to_number, message)


class EmailNotifier:
    """
    Email notification sender using Gmail SMTP.
    
    Provides methods to send email messages via Gmail SMTP with App Password authentication.
    Requires Gmail SMTP credentials to be set in environment variables.
    """
    
    def __init__(
        self,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        smtp_from: Optional[str] = None
    ):
        """
        Initialize the email notifier with Gmail SMTP credentials.
        
        Args:
            smtp_user (Optional[str]): Gmail address. If None, reads from GMAIL_SMTP_USER env var.
            smtp_password (Optional[str]): Gmail App Password. If None, reads from GMAIL_SMTP_PASSWORD env var.
            smtp_from (Optional[str]): Sender email address. If None, reads from GMAIL_SMTP_FROM env var,
                                      or defaults to smtp_user.
        
        Raises:
            ValueError: If required credentials are missing
        """
        # Get credentials from parameters or environment variables
        self.smtp_user = smtp_user or os.getenv('GMAIL_SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('GMAIL_SMTP_PASSWORD')
        
        # Validate required credentials
        if not self.smtp_user:
            raise ValueError("GMAIL_SMTP_USER is required. Set it in .env file or pass as parameter.")
        if not self.smtp_password:
            raise ValueError("GMAIL_SMTP_PASSWORD is required. Set it in .env file or pass as parameter.")
        
        # Set sender email (defaults to smtp_user if not provided)
        self.smtp_from = smtp_from or os.getenv('GMAIL_SMTP_FROM') or self.smtp_user
        
        # Gmail SMTP settings
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> dict:
        """
        Send an email via Gmail SMTP.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject line
            body (str): Email body content (plain text or HTML)
            is_html (bool): If True, body is treated as HTML; otherwise as plain text
        
        Returns:
            dict: Dictionary with success status and message details:
                - success (bool): True if email was sent successfully
                - error (str): Error message if failed, None otherwise
        
        Raises:
            ValueError: If to_email, subject, or body is empty
        """
        if not to_email:
            raise ValueError("to_email cannot be empty")
        if not subject:
            raise ValueError("subject cannot be empty")
        if not body:
            raise ValueError("body cannot be empty")
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to Gmail SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS encryption
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return {
                'success': True,
                'error': None
            }
            
        except smtplib.SMTPAuthenticationError as e:
            return {
                'success': False,
                'error': f"SMTP authentication error: {str(e)}. Check your Gmail App Password."
            }
        except smtplib.SMTPRecipientsRefused as e:
            return {
                'success': False,
                'error': f"SMTP recipient refused: {str(e)}. Check the recipient email address."
            }
        except smtplib.SMTPServerDisconnected as e:
            return {
                'success': False,
                'error': f"SMTP server disconnected: {str(e)}. Check your internet connection."
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'error': f"SMTP error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def send_tender_alert(
        self,
        to_email: str,
        tender_data: dict
    ) -> dict:
        """
        Send a formatted tender alert email.
        
        Args:
            to_email (str): Recipient email address
            tender_data (dict): Dictionary containing tender information with keys:
                - tender_title (str)
                - category (str, optional)
                - department_owner (str, optional)
                - closing_date (str, optional)
                - pdf_links (list, optional)
                - deliverables (str or list, optional)
        
        Returns:
            dict: Result from send_email() method
        """
        # Format tender alert email
        subject = "🔔 New Tender Alert"
        
        # Build HTML email body with required fields
        html_parts = ["<html><body>"]
        html_parts.append("<div style='font-family: Arial, sans-serif; line-height: 1.8; max-width: 600px;'>")
        html_parts.append("<h2 style='color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;'>🔔 New Tender Alert</h2>")
        html_parts.append("<div style='background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-top: 20px;'>")
        
        # Tender Title
        title = tender_data.get('tender_title', '').strip()
        html_parts.append(f"<p style='margin: 10px 0;'><strong style='color: #2c3e50;'>Tender Title:</strong> <span>{title if title else 'N/A'}</span></p>")
        
        # Category
        category = tender_data.get('category', '').strip()
        html_parts.append(f"<p style='margin: 10px 0;'><strong style='color: #2c3e50;'>Category:</strong> <span>{category if category else 'N/A'}</span></p>")
        
        # Department
        department = tender_data.get('department_owner', '').strip()
        html_parts.append(f"<p style='margin: 10px 0;'><strong style='color: #2c3e50;'>Department:</strong> <span>{department if department else 'N/A'}</span></p>")
        
        # Closing Date
        closing_date = tender_data.get('closing_date', '').strip()
        html_parts.append(f"<p style='margin: 10px 0;'><strong style='color: #2c3e50;'>Closing Date:</strong> <span>{closing_date if closing_date else 'N/A'}</span></p>")
        
        # Link
        link = get_primary_link(tender_data)
        if link != "N/A":
            html_parts.append(f"<p style='margin: 10px 0;'><strong style='color: #2c3e50;'>Link:</strong> <a href='{link}' style='color: #3498db; text-decoration: none;'>{link}</a></p>")
        else:
            html_parts.append(f"<p style='margin: 10px 0;'><strong style='color: #2c3e50;'>Link:</strong> <span>N/A</span></p>")
        
        # Deliverables
        deliverables = format_deliverables(tender_data)
        html_parts.append(f"<p style='margin: 10px 0;'><strong style='color: #2c3e50;'>Deliverables:</strong> <span>{deliverables}</span></p>")
        
        html_parts.append("</div>")
        html_parts.append("</div>")
        html_parts.append("</body></html>")
        
        html_body = "\n".join(html_parts)
        
        return self.send_email(to_email, subject, html_body, is_html=True)

