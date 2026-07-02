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
        if not self.email:
            return {"success": False, "message": "Email system not available"}
    
        q = query.lower()
    
        # ================= READ =================
        if "unread" in q:
            return {
                "success": True,
                "action": "read_unread",
                "data": self.email.get_unread_emails()
            }
    
        if "latest" in q:
            return {
                "success": True,
                "action": "read_latest",
                "data": self.email.get_latest_email()
            }
    
        # ================= SEARCH =================
        if "search" in q or "about" in q:
            return {
                "success": True,
                "action": "search",
                "data": self.email.search_emails(q)
            }
    
        # ================= SEND =================
        if "send" in q:
            return {
                "success": True,
                "action": "send",
                "message": "Send email detected (parser will improve next stage)"
            }
    
        # fallback
        return {
            "success": True,
            "action": "summary",
            "data": self.email.get_unread_emails()
        }
