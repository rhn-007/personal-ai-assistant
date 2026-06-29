"""
Main Assistant Class - Coordinates all components (Fixed)
"""

import os
from typing import List
from dotenv import load_dotenv

# FIXED IMPORTS (IMPORTANT)
from src.core.conversation import ConversationManager
from src.core.memory import MemoryManager
from src.integrations.openai import OpenAIIntegration
from src.integrations.email import EmailIntegration
from src.utils.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__)


class PersonalAssistant:
    """Main Personal AI Assistant with Email Support"""

    def __init__(self):
        """Initialize the assistant with all components"""
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing PersonalAssistant...")

        # Core components
        self.memory_manager = MemoryManager()
        self.conversation_manager = ConversationManager(self.memory_manager)
        self.openai = OpenAIIntegration()

        # Email integration (optional)
        try:
            self.email = EmailIntegration()
        except Exception as e:
            self.logger.warning(f"Email integration disabled: {e}")
            self.email = None

        self.logger.info("PersonalAssistant initialized successfully")

    def process_input(self, user_input: str) -> str:
        """Process user input and return response"""
        try:
            # Email handling first
            if self.email and self._is_email_query(user_input):
                return self._handle_email_query(user_input)

            # Normal AI response
            context = self.conversation_manager.get_context()
            response = self.openai.generate_response(user_input, context)

            self.conversation_manager.add_exchange(user_input, response)
            return response

        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return f"Error: {str(e)}"

    def _is_email_query(self, text: str) -> bool:
        keywords = ["email", "mail", "gmail", "inbox", "unread", "send", "from:"]
        return any(k in text.lower() for k in keywords)

    def _handle_email_query(self, user_input: str) -> str:
        """Handle email-related commands"""
        try:
            text = user_input.lower()

            if "unread" in text or "check" in text:
                return self.email.get_email_summary()

            if "from:" in text:
                sender = text.split("from:")[1].split()[0]
                emails = self.email.get_emails_from(sender)

                if not emails:
                    return f"No emails found from {sender}"

                return "\n".join(
                    [f"- {e.get('subject','No Subject')} ({e.get('date','')})"
                     for e in emails]
                )

            return self.email.get_email_summary()

        except Exception as e:
            return f"Email error: {e}"

    # ---------------- EMAIL ----------------

    def send_email(self, to: str, subject: str, body: str) -> bool:
        if not self.email:
            return False
        return self.email.send_email(to, subject, body)

    def get_email_summary(self) -> str:
        if not self.email:
            return "Email not available"
        return self.email.get_email_summary()

    # ---------------- HISTORY ----------------

    def show_history(self, limit: int = 10):
        history = self.conversation_manager.get_history(limit)

        if not history:
            print("No history found.")
            return

        print("\n📝 Conversation History")
        print("=" * 40)

        for i, h in enumerate(history, 1):
            print(f"\n[{i}] {h['timestamp']}")
            print(f"You: {h['user'][:80]}")
            print(f"AI: {h['assistant'][:80]}")

    def clear_history(self):
        self.conversation_manager.clear_history()
        self.logger.info("History cleared")

    # ---------------- TASKS ----------------

    def show_tasks(self):
        print("""
📋 Tasks:
- daily_briefing
- weekly_report
- social_media
- email_digest
- check_emails
""")

    def execute_task(self, task_name: str):
        tasks = {
            "daily_briefing": self._daily_briefing,
            "weekly_report": self._weekly_report,
            "social_media": self._social_media_post,
            "email_digest": self._email_digest,
            "check_emails": self._check_emails,
        }

        task = tasks.get(task_name.lower())

        if task:
            task()
        else:
            raise ValueError(f"Unknown task: {task_name}")

    # ---------------- CONFIG ----------------

    def show_config(self):
        print("\n⚙️ Config")
        print("=" * 30)

        print("OpenAI:", bool(os.getenv("OPENAI_API_KEY")))
        print("Email:", bool(self.email))
        print("Slack:", bool(os.getenv("SLACK_BOT_TOKEN")))
        print("Calendar:", bool(os.getenv("GOOGLE_CALENDAR_ID")))
        print("Weather:", bool(os.getenv("OPENWEATHER_API_KEY")))
        print("Twitter:", bool(os.getenv("TWITTER_API_KEY")))

    # ---------------- TASK IMPLEMENTATIONS ----------------

    def _daily_briefing(self):
        print("Generating daily briefing...")
        result = self.process_input(
            "Give me a daily briefing with summary of tasks and emails"
        )
        print(result)

    def _weekly_report(self):
        print("Generating weekly report...")
        result = self.process_input("Generate weekly productivity report")
        print(result)

    def _social_media_post(self):
        print("Generating social post...")
        result = self.process_input("Write a tweet about AI trends")
        print(result)

    def _email_digest(self):
        if not self.email:
            print("Email not available")
            return

        emails = self.email.get_email_summary()
        result = self.process_input(
            f"Summarize these emails:\n{emails}"
        )
        print(result)

    def _check_emails(self):
        if not self.email:
            print("Email not available")
            return

        print(self.email.get_email_summary())
