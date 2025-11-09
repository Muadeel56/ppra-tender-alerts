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
                - tender_number (str, optional)
                - pdf_links (list, optional)
        
        Returns:
            dict: Result from send_email() method
        """
        # Format tender alert email
        subject = "🔔 New Tender Alert"
        
        # Build HTML email body
        html_parts = ["<html><body>"]
        html_parts.append("<h2>🔔 New Tender Alert</h2>")
        html_parts.append("<div style='font-family: Arial, sans-serif; line-height: 1.6;'>")
        
        if tender_data.get('tender_title'):
            html_parts.append(f"<p><strong>Title:</strong> {tender_data['tender_title']}</p>")
        
        if tender_data.get('tender_number'):
            html_parts.append(f"<p><strong>Tender No:</strong> {tender_data['tender_number']}</p>")
        
        if tender_data.get('category'):
            html_parts.append(f"<p><strong>Category:</strong> {tender_data['category']}</p>")
        
        if tender_data.get('department_owner'):
            html_parts.append(f"<p><strong>Department:</strong> {tender_data['department_owner']}</p>")
        
        if tender_data.get('closing_date'):
            html_parts.append(f"<p><strong>Closing Date:</strong> {tender_data['closing_date']}</p>")
        
        if tender_data.get('pdf_links') and len(tender_data['pdf_links']) > 0:
            html_parts.append(f"<p><strong>PDF Links ({len(tender_data['pdf_links'])} available):</strong></p>")
            html_parts.append("<ul>")
            for link in tender_data['pdf_links'][:5]:  # Limit to first 5 links
                html_parts.append(f"<li><a href='{link}'>{link}</a></li>")
            html_parts.append("</ul>")
        
        html_parts.append("</div>")
        html_parts.append("</body></html>")
        
        html_body = "\n".join(html_parts)
        
        return self.send_email(to_email, subject, html_body, is_html=True)

