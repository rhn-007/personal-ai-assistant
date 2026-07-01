"""
Email Integration - Gmail support (Fixed Stable + Type Safe Version)
"""

import os
import base64
from typing import List, Dict, Optional, Union

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery

from email.mime.text import MIMEText
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailIntegration:
    """Gmail integration for sending and reading emails (SAFE VERSION)"""

    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self):
        self.service = None
        self._authenticate()

    # =========================================================
    # AUTH
    # =========================================================
    def _authenticate(self):
        try:
            creds = None
            credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")

            # Service account (optional)
            if credentials_file and os.path.exists(credentials_file):
                creds = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=self.SCOPES
                )

            token_file = "token.json"

            # OAuth flow
            if not creds:
                if os.path.exists(token_file):
                    import pickle
                    with open(token_file, "rb") as token:
                        creds = pickle.load(token)

                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        if not os.path.exists("credentials.json"):
                            raise FileNotFoundError(
                                "credentials.json missing (Google OAuth file required)"
                            )

                        flow = InstalledAppFlow.from_client_secrets_file(
                            "credentials.json",
                            self.SCOPES
                        )
                        creds = flow.run_local_server(port=0)

                    import pickle
                    with open(token_file, "wb") as token:
                        pickle.dump(creds, token)

            self.service = googleapiclient.discovery.build(
                "gmail", "v1",
                credentials=creds
            )

            logger.info("Gmail authentication successful")

        except Exception as e:
            logger.warning(f"Gmail authentication failed: {e}")
            self.service = None

    # =========================================================
    # SEND EMAIL
    # =========================================================
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        if not self.service:
            return False

        try:
            message = MIMEText(body, "html" if html else "plain")
            message["to"] = to
            message["subject"] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            self.service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()

            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    # =========================================================
    # CORE FETCH (SAFE OUTPUT ONLY DICTS OR LIST[DICT])
    # =========================================================
    def get_emails(self, query: str = "is:unread", max_results: int = 5) -> List[Dict]:
        if not self.service:
            return []

        try:
            results = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get("messages", [])
            emails = []

            for msg in messages:
                email = self._get_email_content(msg.get("id"))
                if isinstance(email, dict):
                    emails.append(email)

            return emails

        except Exception as e:
            logger.error(f"Error getting emails: {e}")
            return []

    # =========================================================
    # SAFE EMAIL PARSER
    # =========================================================
    def _get_email_content(self, message_id: str) -> Optional[Dict]:
        try:
            msg = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format="full"
            ).execute()

            headers = msg.get("payload", {}).get("headers", [])

            return {
                "id": message_id,
                "subject": self._safe_header(headers, "Subject"),
                "from": self._safe_header(headers, "From"),
                "to": self._safe_header(headers, "To"),
                "date": self._safe_header(headers, "Date"),
            }

        except Exception as e:
            logger.error(f"Error getting email content: {e}")
            return None

    # =========================================================
    # HEADER SAFETY
    # =========================================================
    def _safe_header(self, headers: List[Dict], name: str) -> str:
        try:
            return next((h["value"] for h in headers if h.get("name") == name), "")
        except Exception:
            return ""

    # =========================================================
    # HELPERS (CONSISTENT OUTPUT)
    # =========================================================
    def get_unread_emails(self, max_results: int = 5) -> List[Dict]:
        return self.get_emails("is:unread", max_results)

    def get_emails_from(self, sender: str, max_results: int = 5) -> List[Dict]:
        emails = self.get_emails(f"from:{sender}", max_results)
        return emails if isinstance(emails, list) else []

    def get_email_summary(self) -> str:
        emails = self.get_unread_emails()

        if not isinstance(emails, list) or len(emails) == 0:
            return "No unread emails found."

        safe_lines = []
        for e in emails:
            if isinstance(e, dict):
                safe_lines.append(
                    f"- {e.get('subject','No Subject')} | {e.get('from','Unknown')}"
                )

        return "\n".join(safe_lines) if safe_lines else "No unread emails found."
