"""
Email Integration - Gmail support (Stable + Import-safe version)
"""

import os
import base64
import pickle
from typing import List, Dict, Optional

from email.mime.text import MIMEText

# ---------------- SAFE LOGGER (prevents import crashes) ----------------
try:
    from src.utils.logger import setup_logger
    logger = setup_logger(__name__)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# ---------------- GOOGLE IMPORTS ----------------
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery


class EmailIntegration:
    """
    Gmail integration for:
    - Reading emails
    - Fetching unread messages
    - Sending emails
    """

    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

    def __init__(self):
        self.service = None
        self._authenticate()

    # =========================================================
    # AUTHENTICATION
    # =========================================================
    def _authenticate(self):
        """Authenticate Gmail safely (handles all edge cases)"""

        try:
            creds = None

            credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")

            # 1. SERVICE ACCOUNT (optional)
            if credentials_file and os.path.exists(credentials_file):
                creds = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=self.SCOPES
                )

            token_file = "token.json"

            # 2. OAUTH TOKEN
            if not creds:
                if os.path.exists(token_file):
                    with open(token_file, "rb") as token:
                        creds = pickle.load(token)

                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())

                elif not creds:
                    if not os.path.exists("credentials.json"):
                        raise FileNotFoundError(
                            "Missing credentials.json (Google OAuth required)"
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json",
                        self.SCOPES
                    )

                    creds = flow.run_local_server(port=0)

                # Save token
                with open(token_file, "wb") as token:
                    pickle.dump(creds, token)

            # Build Gmail service
            self.service = googleapiclient.discovery.build(
                "gmail",
                "v1",
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
        """Send email via Gmail API"""

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
            logger.error(f"Send email error: {e}")
            return False

    # =========================================================
    # FETCH EMAILS
    # =========================================================
    def get_emails(self, query: str = "is:unread", max_results: int = 5) -> List[Dict]:
        """Generic email fetch"""

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
                email_data = self._get_email_content(msg["id"])
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            logger.error(f"Get emails error: {e}")
            return []

    def _get_email_content(self, message_id: str) -> Optional[Dict]:
        """Fetch single email details"""

        try:
            msg = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format="full"
            ).execute()

            headers = msg.get("payload", {}).get("headers", [])

            def get_header(name):
                return next((h["value"] for h in headers if h["name"] == name), "")

            return {
                "id": message_id,
                "subject": get_header("Subject") or "No Subject",
                "from": get_header("From") or "Unknown",
                "to": get_header("To"),
                "date": get_header("Date")
            }

        except Exception as e:
            logger.error(f"Email parse error: {e}")
            return None

    # =========================================================
    # HELPERS
    # =========================================================
    def get_unread_emails(self, max_results: int = 5) -> List[Dict]:
        return self.get_emails("is:unread", max_results)

    def get_emails_from(self, sender: str, max_results: int = 5) -> List[Dict]:
        return self.get_emails(f"from:{sender}", max_results)

    def get_email_summary(self) -> str:
        emails = self.get_unread_emails()

        if not emails:
            return "No unread emails found."

        return "\n".join(
            f"- {e.get('subject','No Subject')} | {e.get('from','Unknown')}"
            for e in emails
        )
