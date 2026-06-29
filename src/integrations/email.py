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
from src.utils.logger import setup_logger

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
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')

            if credentials_file and os.path.exists(credentials_file):
                creds = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=self.SCOPES
                )
            else:
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

            self.service = googleapiclient.discovery.build(
                'gmail', 'v1', credentials=creds
            )
            logger.info("Gmail authentication successful")

        except Exception as e:
            logger.warning(f"Gmail authentication failed: {e}")
            logger.info("Email features will not be available")

    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        if not self.service:
            return False

        try:
            message = MIMEText(body, 'html' if html else 'plain')
            message['to'] = to
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}

            self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def get_emails(self, query: str = "is:unread", max_results: int = 5) -> List[Dict]:
        if not self.service:
            return []

        try:
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

            return email_data

        except Exception as e:
            logger.error(f"Error getting email content: {e}")
            return None

    def get_unread_emails(self, max_results: int = 5) -> List[Dict]:
        return self.get_emails("is:unread", max_results)

    def get_emails_from(self, sender: str, max_results: int = 5) -> List[Dict]:
        return self.get_emails(f"from:{sender}", max_results)
