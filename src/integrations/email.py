import os
import base64
import pickle
from typing import List, Dict, Optional

from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailIntegration:

    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

    def __init__(self):
        self.service = None
        self._authenticate()

    # =====================================================
    # AUTH FIX (THIS WAS MISSING / BROKEN)
    # =====================================================

    def _authenticate(self):
        creds = None
        token_file = "token.json"
        creds_file = "credentials.json"

        try:
            # Load saved token
            if os.path.exists(token_file):
                with open(token_file, "rb") as token:
                    creds = pickle.load(token)

            # If no valid creds → login flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(creds_file):
                        raise FileNotFoundError(
                            "Missing credentials.json (Google OAuth file required)"
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        creds_file,
                        self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # save token
                with open(token_file, "wb") as token:
                    pickle.dump(creds, token)

            self.service = build("gmail", "v1", credentials=creds)

            logger.info("Gmail authentication successful")

        except Exception as e:
            logger.warning(f"Gmail authentication failed: {e}")
            self.service = None

    # =====================================================
    # EMAIL FETCH
    # =====================================================

    def get_emails(self, query="is:unread", max_results=5):
        if not self.service:
            return []

        results = self.service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])

        return [
            self._get_email(msg["id"])
            for msg in messages
            if self._get_email(msg["id"])
        ]

    def get_unread_emails(self, max_results: int = 5):
        return self.get_emails("is:unread", max_results)

    def get_latest_email(self):
        emails = self.get_emails("in:inbox", 1)
        return emails[0] if emails else None

    def search_emails(self, query: str):
        return self.get_emails(query)

    # =====================================================
    # SINGLE EMAIL PARSER
    # =====================================================

    def _get_email(self, message_id: str) -> Optional[Dict]:
        msg = self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])

        def get(name):
            return next((h["value"] for h in headers if h["name"] == name), "")

        return {
            "id": message_id,
            "subject": get("Subject"),
            "from": get("From"),
            "to": get("To"),
            "date": get("Date")
        }

    # =====================================================
    # SEND EMAIL
    # =====================================================

    def send_email(self, to, subject, body):
        if not self.service:
            return False

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        self.service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        return True
    def get_email_summary(self, max_results: int = 5) -> str:
        emails = self.get_unread_emails(max_results)
    
        if not emails:
            return "No unread emails found."
    
        return "\n".join(
            f"- {e.get('subject', 'No Subject')} | {e.get('from', 'Unknown')}"
            for e in emails
        )
