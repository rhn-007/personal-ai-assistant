"""
Main Assistant Class - Memory 2.0 Upgrade (Stable + Fixed)
"""

import os
from dotenv import load_dotenv

from src.core.conversation import ConversationManager
from src.core.memory import MemoryManager
from src.integrations.ollama import OllamaIntegration
from src.integrations.email import EmailIntegration
from src.utils.logger import setup_logger

load_dotenv()


class PersonalAssistant:
    """AI Assistant with persistent memory + context awareness"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing PersonalAssistant (Memory 2.0)...")

        # Core systems
        self.memory = MemoryManager()
        self.conversation = ConversationManager(self.memory)

        # LLM
        self.llm = OllamaIntegration()

        # Email (optional)
        try:
            self.email = EmailIntegration()
        except Exception as e:
            self.logger.warning(f"Email disabled: {e}")
            self.email = None

        self.logger.info("Assistant ready with Memory 2.0")

    # ---------------- MEMORY BUILD ----------------

    def _build_memory_context(self) -> str:
        """Convert stored memory into readable system prompt"""
        profile = self.memory.get_all_profile()

        if not profile:
            return ""

        lines = ["User Persistent Memory:"]

        for k, v in profile.items():
            if v:
                lines.append(f"- {k}: {v}")

        return "\n".join(lines)

    # ---------------- AUTO MEMORY LEARNING ----------------

    def _auto_memory_capture(self, text: str):
        """Lightweight memory extraction"""

        t = text.lower().strip()

        # name
        if "my name is" in t:
            name = text.lower().split("my name is")[-1].strip()
            self.memory.set_profile("name", name)

        # preferences
        if "i like" in t:
            value = text.lower().split("i like")[-1].strip()
            self.memory.set_profile("likes", value)

        if "i hate" in t:
            value = text.lower().split("i hate")[-1].strip()
            self.memory.set_profile("dislikes", value)

    # ---------------- MAIN PIPELINE ----------------

    def process_input(self, user_input: str) -> str:
        """Main entry point"""

        try:
            # 1. store memory automatically
            self._auto_memory_capture(user_input)

            # 2. email routing
            if self.email and self._is_email_query(user_input):
                return self._handle_email_query(user_input)

            # 3. build conversation context
            context = self.conversation.get_context()

            # 4. inject memory safely (ONLY ONCE per request)
            memory_context = self._build_memory_context()
            if memory_context:
                context.insert(0, {
                    "role": "system",
                    "content": memory_context
                })

            # 5. generate response
            response = self.llm.generate_response(user_input, context)

            # 6. save exchange
            self.conversation.add_exchange(user_input, response)

            return response

        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return f"Error: {str(e)}"

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
        if not self.email:
            return False
        return self.email.send_email(to, subject, body)

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
