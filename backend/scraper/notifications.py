"""
WhatsApp Notifications Module

This module provides functionality to send WhatsApp messages via Twilio sandbox,
including error handling and environment variable management.
"""

import os
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

