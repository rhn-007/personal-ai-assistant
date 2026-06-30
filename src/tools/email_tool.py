"""
Email Tool - Handles all email-related user requests
"""

from src.integrations.email import EmailIntegration
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailTool:
    """
    Tool for:
    - Checking unread emails
    - Fetching emails from a sender
    - Sending emails (basic stage)
    """

    def __init__(self):
        self.name = "email"
        self.email = None

        try:
            self.email = EmailIntegration()
            logger.info("EmailTool initialized successfully")
        except Exception as e:
            logger.warning(f"EmailTool disabled: {e}")

    # ----------------------------------------------------
    # Tool Capability Check
    # ----------------------------------------------------

    def can_handle(self, query: str) -> bool:
        """
        Decide if this query is email-related.
        """
        keywords = [
            "email", "mail", "gmail", "inbox",
            "unread", "send email", "check mail",
            "from:", "send to", "compose"
        ]

        q = query.lower()
        return any(k in q for k in keywords)

    # ----------------------------------------------------
    # Main Execution
    # ----------------------------------------------------

    def execute(self, query: str):
        """
        Executes email-related actions based on intent.
        """

        if not self.email:
            return "Email system is not available."

        q = query.lower()

        try:
            # -----------------------------
            # 1. Check unread / inbox
            # -----------------------------
            if "unread" in q or "check" in q or "inbox" in q:
                return self.email.get_email_summary()

            # -----------------------------
            # 2. Emails from specific sender
            # -----------------------------
            if "from:" in q:
                sender = q.split("from:")[1].split()[0]
                emails = self.email.get_emails_from(sender)

                if not emails:
                    return f"No emails found from {sender}"

                return "\n".join(
                    f"- {e.get('subject', 'No Subject')} ({e.get('date', '')})"
                    for e in emails
                )

            # -----------------------------
            # 3. Send email (basic parsing)
            # Format: "send email to X subject Y body Z"
            # -----------------------------
            if "send" in q:

                # VERY SIMPLE PARSER (we will improve later)
                return "Send email feature detected. (Stage 2 will add smart parsing + structured extraction.)"

            # fallback
            return self.email.get_email_summary()

        except Exception as e:
            logger.error(f"EmailTool error: {e}")
            return f"Email error: {e}"
