"""
Main Assistant Class
"""

import os
import re
from dotenv import load_dotenv

from src.core.conversation import ConversationManager
from src.core.memory import MemoryManager
from src.integrations.ollama import OllamaIntegration
from src.integrations.email import EmailIntegration
from src.utils.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__)


class PersonalAssistant:
    """Main Personal AI Assistant"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing PersonalAssistant...")

        # Core
        self.memory_manager = MemoryManager()
        self.conversation_manager = ConversationManager(self.memory_manager)
        self.llm = OllamaIntegration()

        # Load long-term memory
        self.profile = self.memory_manager.get_all_profile()

        # Email (optional)
        try:
            self.email = EmailIntegration()
        except Exception as e:
            self.logger.warning(f"Email integration disabled: {e}")
            self.email = None

        self.logger.info("PersonalAssistant initialized successfully")

    # ----------------------------------------------------

    def process_input(self, user_input: str) -> str:
        """Main processing pipeline"""

        try:

            text = user_input.strip()

            # ---------------- EMAIL ----------------

            if self.email and self._is_email_query(text):
                return self._handle_email_query(text)

            lower = text.lower()

            # ---------------- REMEMBER NAME ----------------

            patterns = [
                r"my name is (.+)",
                r"i am (.+)",
                r"i'm (.+)"
            ]

            for pattern in patterns:
                match = re.match(pattern, lower)

                if match:
                    name = match.group(1).strip().title()

                    self.memory_manager.set_profile("name", name)
                    self.profile["name"] = name

                    return f"Nice to meet you, {name}! I'll remember your name."

            # ---------------- RECALL NAME ----------------

            if (
                "what is my name" in lower
                or "who am i" in lower
            ):
                name = self.memory_manager.get_profile("name")

                if name:
                    return f"Your name is {name}."

                return "I don't know your name yet."

            # ---------------- BUILD CONTEXT ----------------

            context = self.conversation_manager.get_context()

            if self.profile:

                memory_text = "\n".join(
                    f"{k}: {v}"
                    for k, v in self.profile.items()
                )

                context.insert(
                    0,
                    {
                        "role": "system",
                        "content":
                            "Known facts about the user:\n"
                            + memory_text
                    }
                )

            # ---------------- LLM ----------------

            response = self.llm.generate_response(
                text,
                context
            )

            self.conversation_manager.add_exchange(
                text,
                response
            )

            return response

        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return f"Error: {e}"

    # ----------------------------------------------------

    def _is_email_query(self, text: str):
        keywords = [
            "email",
            "mail",
            "gmail",
            "inbox",
            "unread",
            "send",
            "from:"
        ]

        return any(k in text.lower() for k in keywords)

    def _handle_email_query(self, user_input: str):

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
                    [
                        f"- {e.get('subject','No Subject')} ({e.get('date','')})"
                        for e in emails
                    ]
                )

            return self.email.get_email_summary()

        except Exception as e:
            return f"Email error: {e}"

    # ----------------------------------------------------
    # EMAIL
    # ----------------------------------------------------

    def send_email(self, to, subject, body):
        if not self.email:
            return False
        return self.email.send_email(to, subject, body)

    def get_email_summary(self):
        if not self.email:
            return "Email not available"
        return self.email.get_email_summary()

    # ----------------------------------------------------
    # HISTORY
    # ----------------------------------------------------

    def show_history(self, limit=10):

        history = self.conversation_manager.get_history(limit)

        if not history:
            print("No history found.")
            return

        print("\nConversation History")
        print("=" * 40)

        for i, h in enumerate(history, 1):
            print(f"\n[{i}] {h['timestamp']}")
            print(f"You: {h['user']}")
            print(f"Assistant: {h['assistant']}")

    def clear_history(self):
        self.conversation_manager.clear_history()
        self.logger.info("History cleared")

    # ----------------------------------------------------
    # TASKS
    # ----------------------------------------------------

    def show_tasks(self):
        print("""
Tasks:
- daily_briefing
- weekly_report
- social_media
- email_digest
- check_emails
""")

    def execute_task(self, task_name):

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

    # ----------------------------------------------------
    # CONFIG
    # ----------------------------------------------------

    def show_config(self):

        print("\nConfiguration")
        print("=" * 30)

        print("Using Ollama: True")
        print("Email:", bool(self.email))
        print("Saved Profile:", self.profile)

    # ----------------------------------------------------
    # TASK IMPLEMENTATIONS
    # ----------------------------------------------------

    def _daily_briefing(self):
        print(self.process_input(
            "Give me today's briefing."
        ))

    def _weekly_report(self):
        print(self.process_input(
            "Generate my weekly report."
        ))

    def _social_media_post(self):
        print(self.process_input(
            "Write an AI social media post."
        ))

    def _email_digest(self):

        if not self.email:
            print("Email unavailable.")
            return

        emails = self.email.get_email_summary()

        print(
            self.process_input(
                f"Summarize these emails:\n{emails}"
            )
        )

    def _check_emails(self):

        if not self.email:
            print("Email unavailable.")
            return

        print(self.email.get_email_summary())
