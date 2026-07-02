"""
Email Tool - Handles all email-related user requests
"""

from src.integrations.email import EmailIntegration
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailTool:
    def __init__(self):
        self.name = "email"
        self.email = EmailIntegration()

    # =========================================================
    # TOOL CAPABILITY CHECK (still used by router fallback)
    # =========================================================

    def can_handle(self, query: str):
        if not isinstance(query, str):
            return False

        q = query.lower()
        return any(k in q for k in [
            "email", "mail", "gmail", "inbox",
            "unread", "send", "from:"
        ])

    # =========================================================
    # NEW UNIFIED EXECUTION
    # =========================================================

    def execute(self, payload):

        # -------------------------
        # LEGACY SUPPORT (string)
        # -------------------------
        if isinstance(payload, str):
            q = payload.lower()

            if "unread" in q or "inbox" in q:
                return self.email.get_email_summary()

            if "from:" in q:
                sender = q.split("from:")[-1].split()[0]
                emails = self.email.get_emails_from(sender)
                return "\n".join(e["subject"] for e in emails)

            return self.email.get_email_summary()

        # -------------------------
        # NEW STRUCTURED MODE
        # -------------------------
        if isinstance(payload, dict):

            action = payload.get("action")
            data = payload.get("input", {})

            # GET UNREAD EMAILS
            if action == "get_unread":
                emails = self.email.get_unread_emails()
                return "\n".join(
                    f"{e['subject']} | {e['from']}"
                    for e in emails
                )

            # GET FROM SENDER
            if action == "get_from_sender":
                sender = data.get("sender", "")
                emails = self.email.get_emails_from(sender)
                return "\n".join(e["subject"] for e in emails)

            # SEND EMAIL (future)
            if action == "send_email":
                return "Send email not implemented yet"

            return f"Unknown email action: {action}"

        return "Invalid payload"
