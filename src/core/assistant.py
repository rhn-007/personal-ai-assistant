"""
Main Assistant Class - Memory 2.0 Upgrade (Persistent User Memory + Context Injection)
"""

import os
from dotenv import load_dotenv

from src.core.conversation import ConversationManager
from src.core.memory import MemoryManager
from src.integrations.ollama import OllamaIntegration
from src.integrations.email import EmailIntegration
from src.utils.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__)


class PersonalAssistant:
    """AI Assistant with persistent memory + context awareness"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing PersonalAssistant (Memory 2.0)...")

        # Core systems
        self.memory = MemoryManager()
        self.conversation = ConversationManager(self.memory)

        # LLM (Ollama)
        self.llm = OllamaIntegration()

        # Email (optional)
        try:
            self.email = EmailIntegration()
        except Exception as e:
            self.logger.warning(f"Email disabled: {e}")
            self.email = None

        # Load persistent memory into context
        self._load_user_memory()

        self.logger.info("Assistant ready with Memory 2.0")

    # ---------------- MEMORY LOADING ----------------

    def _load_user_memory(self):
        """Load persistent memory into system context"""
        profile = self.memory.get_all_profile()

        if profile:
            memory_text = "User Profile Memory:\n"
            for k, v in profile.items():
                memory_text += f"- {k}: {v}\n"

            self.conversation.add_system_context(memory_text)

    # ---------------- MAIN PIPELINE ----------------

    def process_input(self, user_input: str) -> str:
        """Main entry point"""

        try:
            # 1. Check if user is storing memory explicitly
            self._auto_memory_capture(user_input)

            # 2. Email routing
            if self.email and self._is_email_query(user_input):
                return self._handle_email_query(user_input)

            # 3. Build context
            context = self.conversation.get_context()

            # 4. Add memory snapshot dynamically (VERY IMPORTANT)
            profile = self.memory.get_all_profile()
            if profile:
                context.insert(0, {
                    "role": "system",
                    "content": f"User memory: {profile}"
                })

            # 5. Generate response
            response = self.llm.generate_response(user_input, context)

            # 6. Save conversation
            self.conversation.add_exchange(user_input, response)

            return response

        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return f"Error: {str(e)}"

    # ---------------- MEMORY AUTO LEARNING ----------------

    def _auto_memory_capture(self, text: str):
        """
        Extract simple memory patterns automatically
        (v2.0 lightweight memory learning)
        """

        text_lower = text.lower()

        # NAME MEMORY
        if "my name is" in text_lower:
            name = text.split("is")[-1].strip()
            self.memory.set_profile("name", name)

        # PREFERENCE MEMORY
        if "i like" in text_lower:
            pref = text.split("like")[-1].strip()
            self.memory.set_profile("likes", pref)

        if "i hate" in text_lower:
            dislike = text.split("hate")[-1].strip()
            self.memory.set_profile("dislikes", dislike)

    # ---------------- EMAIL ----------------

    def _is_email_query(self, text: str) -> bool:
        keywords = ["email", "mail", "gmail", "inbox", "unread", "send", "from:"]
        return any(k in text.lower() for k in keywords)

    def _handle_email_query(self, user_input: str) -> str:
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
                    f"- {e.get('subject','No Subject')} ({e.get('date','')})"
                    for e in emails
                )

            return self.email.get_email_summary()

        except Exception as e:
            return f"Email error: {e}"

    # ---------------- EMAIL API ----------------

    def send_email(self, to: str, subject: str, body: str) -> bool:
        return self.email.send_email(to, subject, body) if self.email else False

    # ---------------- HISTORY ----------------

    def show_history(self, limit: int = 10):
        history = self.conversation.get_history(limit)

        if not history:
            print("No history found.")
            return

        print("\n🧠 Conversation History")
        print("=" * 40)

        for i, h in enumerate(history, 1):
            print(f"\n[{i}] {h['timestamp']}")
            print(f"You: {h['user'][:80]}")
            print(f"AI: {h['assistant'][:80]}")

    def clear_history(self):
        self.conversation.clear_history()
        self.logger.info("History cleared")

    # ---------------- MEMORY CONTROL ----------------

    def remember(self, key: str, value: str):
        """Manual memory storage"""
        self.memory.set_profile(key, value)

    def recall(self, key: str):
        """Manual memory retrieval"""
        return self.memory.get_profile(key)

    def show_memory(self):
        """Show everything assistant remembers"""
        return self.memory.get_all_profile()

    # ---------------- TASKS ----------------

    def execute_task(self, task_name: str):

        tasks = {
            "daily_briefing": lambda: self.process_input("Give me a daily briefing"),
            "weekly_report": lambda: self.process_input("Generate weekly report"),
            "social_media": lambda: self.process_input("Write a tweet about AI"),
        }

        if task_name in tasks:
            return tasks[task_name]()
        else:
            raise ValueError("Unknown task")

    # ---------------- CONFIG ----------------

    def show_config(self):
        print("\n⚙️ System Status")
        print("=" * 30)

        print("OpenAI:", bool(os.getenv("OPENAI_API_KEY")))
        print("Ollama:", True)
        print("Email:", bool(self.email))

        print("\n🧠 Memory:")
        print(self.memory.get_all_profile())
