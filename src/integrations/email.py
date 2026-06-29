"""
Email Integration - Gmail support
"""

import os
import base64
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_httplib2 import AuthorizedHttp
import googleapiclient.discovery
from email.mime.text import MIMEText
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailIntegration:
    """Gmail integration for sending and reading emails"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self):
        """Initialize Gmail integration"""
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        try:
            # Try to use credentials file if available
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
            
            if credentials_file and os.path.exists(credentials_file):
                creds = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=self.SCOPES
                )
            else:
                # Use OAuth2 flow
                creds = None
                token_file = 'token.pickle'
                
                if os.path.exists(token_file):
                    import pickle
                    with open(token_file, 'rb') as token:
                        creds = pickle.load(token)
                
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json',
                            self.SCOPES
                        )
                        creds = flow.run_local_server(port=0)
                    
                    import pickle
                    with open(token_file, 'wb') as token:
                        pickle.dump(creds, token)
            
            self.service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
            logger.info("Gmail authentication successful")
        
        except Exception as e:
            logger.warning(f"Gmail authentication failed: {e}")
            logger.info("Email features will not be available")
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether body is HTML
            
        Returns:
            True if successful
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return False
        
        try:
            # Create message
            message = MIMEText(body, 'html' if html else 'plain')
            message['to'] = to
            message['subject'] = subject
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}
            
            self.service.users().messages().send(userId='me', body=send_message).execute()
            logger.info(f"Email sent to {to}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def get_emails(self, query: str = "is:unread", max_results: int = 5) -> List[Dict]:
        """
        Get emails from Gmail
        
        Args:
            query: Gmail search query (e.g., "is:unread", "from:someone@example.com")
            max_results: Maximum emails to retrieve
            
        Returns:
            List of email dictionaries
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return []
        
        try:
            # Search for emails
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            emails = []
            messages = results.get('messages', [])
            
            for message in messages:
                email_data = self._get_email_content(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        
        except Exception as e:
            logger.error(f"Error getting emails: {e}")
            return []
    
    def _get_email_content(self, message_id: str) -> Optional[Dict]:
        """
        Get full email content
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Email data dictionary
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            email_data = {
                'id': message_id,
                'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject'),
                'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown'),
                'to': next((h['value'] for h in headers if h['name'] == 'To'), ''),
                'date': next((h['value'] for h in headers if h['name'] == 'Date'), ''),
            }
            
            # Try to get body
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            email_data['body'] = base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8')
                        break
            else:
                if 'data' in message['payload']['body']:
                    email_data['body'] = base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode('utf-8')
            
            return email_data
        
        except Exception as e:
            logger.error(f"Error getting email content: {e}")
            return None
    
    def get_unread_emails(self, max_results: int = 5) -> List[Dict]:
        """Get unread emails"""
        return self.get_emails("is:unread", max_results)
    
    def get_emails_from(self, sender: str, max_results: int = 5) -> List[Dict]:
        """
        Get emails from specific sender
        
        Args:
            sender: Email address or name
            max_results: Maximum emails to retrieve
            
        Returns:
            List of emails from sender
        """
        return self.get_emails(f"from:{sender}", max_results)
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark email as read
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            True if successful
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return False
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Email {message_id} marked as read")
            return True
        
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False
    
    def delete_email(self, message_id: str) -> bool:
        """
        Delete an email
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            True if successful
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return False
        
        try:
            self.service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()
            logger.info(f"Email {message_id} deleted")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting email: {e}")
            return False
    
    def get_email_summary(self, max_emails: int = 10) -> str:
        """
        Get summary of recent emails
        
        Args:
            max_emails: Number of emails to summarize
            
        Returns:
            Summary string
        """
        emails = self.get_emails("is:unread", max_emails)
        
        if not emails:
            return "No unread emails."
        
        summary = f"You have {len(emails)} unread emails:\n\n"
        
        for i, email in enumerate(emails, 1):
            summary += f"{i}. From: {email.get('from', 'Unknown')}\n"
            summary += f"   Subject: {email.get('subject', 'No Subject')}\n"
            summary += f"   Date: {email.get('date', 'Unknown')}\n\n"
        
        return summary
