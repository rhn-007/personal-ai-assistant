"""
Main Assistant Class - Memory 2.5 Upgrade (Personality Learning System)
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
    """AI Assistant with persistent memory + personality learning"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing PersonalAssistant (Memory 2.5 - Personality Learning)...")

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

        # Personality state (runtime)
        self.personality_cache = {
            "tone": None,
            "communication_style": None,
            "interests": [],
        }

        self.logger.info("Assistant ready with Personality Learning")

    # ---------------- PERSONALITY BUILDER ----------------

    def _update_personality(self, text: str):
        """
        Learns how the user behaves and speaks
        """

        t = text.lower()

        # tone detection
        if any(word in t for word in ["bro", "dude", "lol", "haha"]):
            self.personality_cache["tone"] = "casual"

        if any(word in t for word in ["please", "kindly", "thank you"]):
            self.personality_cache["tone"] = "formal"

        # interest detection
        interests = [
            "ai", "coding", "python", "games", "anime",
            "robot", "music", "football", "science"
        ]

        for i in interests:
            if i in t:
                if i not in self.personality_cache["interests"]:
                    self.personality_cache["interests"].append(i)

        # writing style preference
        if "short answer" in t or "brief" in t:
            self.personality_cache["communication_style"] = "concise"

        if "explain" in t or "detail" in t:
            self.personality_cache["communication_style"] = "detailed"

    # ---------------- MEMORY + PERSONALITY CONTEXT ----------------

    def _build_system_context(self) -> str:
        """
        Combines:
        - stored memory
        - learned personality
        """

        profile = self.memory.get_all_profile()

        lines = []

        # user profile memory
        if profile:
            lines.append("User Memory:")
            for k, v in profile.items():
                if v:
                    lines.append(f"- {k}: {v}")

        # personality learning
        lines.append("\nUser Personality Profile:")

        tone = self.personality_cache["tone"]
        style = self.personality_cache["communication_style"]
        interests = self.personality_cache["interests"]

        if tone:
            lines.append(f"- tone: {tone}")
        if style:
            lines.append(f"- style: {style}")
        if interests:
            lines.append(f"- interests: {', '.join(interests)}")

        return "\n".join(lines)

    # ---------------- AUTO MEMORY CAPTURE ----------------

    def _auto_memory_capture(self, text: str):
        """Extract long-term memory facts"""

        t = text.lower()

        # name memory
        if "my name is" in t:
            name = text.split("my name is")[-1].strip()
            self.memory.set_profile("name", name)

        # preference memory
        if "i like" in t:
            value = text.split("i like")[-1].strip()
            self.memory.set_profile("likes", value)

        if "i hate" in t:
            value = text.split("i hate")[-1].strip()
            self.memory.set_profile("dislikes", value)

        # update personality learning
        self._update_personality(text)

    # ---------------- MAIN PIPELINE ----------------

    def process_input(self, user_input: str) -> str:
        """Main reasoning pipeline"""

        try:
            # 1. learn from input
            self._auto_memory_capture(user_input)

            # 2. email routing
            if self.email and self._is_email_query(user_input):
                return self._handle_email_query(user_input)

            # 3. conversation context
            context = self.conversation.get_context()

            # 4. inject SYSTEM intelligence (memory + personality)
            system_context = self._build_system_context()

            if system_context:
                context.insert(0, {
                    "role": "system",
                    "content": system_context
                })

            # 5. generate response
            response = self.llm.generate_response(user_input, context)

            # 6. save conversation
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
        self.memory.set_profile(key, value)

    def recall(self, key: str):
        return self.memory.get_profile(key)

    def show_memory(self):
        return {
            "profile": self.memory.get_all_profile(),
            "personality": self.personality_cache
        }

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

        print("\n🧬 Personality:")
        print(self.personality_cache)
