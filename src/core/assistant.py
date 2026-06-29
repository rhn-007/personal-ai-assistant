"""
Main Assistant Class - Memory 4.0 Upgrade (Semantic + Event + Profile Memory)
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
    """AI Assistant with Memory 4.0 (Profile + Events + Semantic Retrieval)"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing PersonalAssistant (Memory 4.0)...")

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

        # Personality cache (unchanged)
        self.personality_cache = {
            "tone": None,
            "communication_style": None,
            "interests": [],
        }

        self.logger.info("Assistant ready with Memory 4.0")

    # =========================================================
    # 🧠 PERSONALITY LEARNING
    # =========================================================

    def _update_personality(self, text: str):
        t = text.lower()

        if any(w in t for w in ["bro", "dude", "lol", "haha"]):
            self.personality_cache["tone"] = "casual"

        if any(w in t for w in ["please", "kindly", "thank you"]):
            self.personality_cache["tone"] = "formal"

        interests = [
            "ai", "coding", "python", "games", "anime",
            "robot", "music", "football", "science"
        ]

        for i in interests:
            if i in t and i not in self.personality_cache["interests"]:
                self.personality_cache["interests"].append(i)

        if "short answer" in t or "brief" in t:
            self.personality_cache["communication_style"] = "concise"

        if "explain" in t or "detail" in t:
            self.personality_cache["communication_style"] = "detailed"

    # =========================================================
    # 🧠 EVENT MEMORY (3.0 CORE STILL ACTIVE)
    # =========================================================

    def _auto_event_capture(self, text: str):
        t = text.lower()

        if "i want to" in t:
            self.memory.add_event("goal", text, importance=3)

        if "problem" in t or "issue" in t:
            self.memory.add_event("problem", text, importance=4)

        if "how to" in t or "learn" in t:
            self.memory.add_event("intent", text, importance=2)

        if "my project" in t:
            self.memory.add_event("project", text, importance=5)

    # =========================================================
    # 🧠 MEMORY 4.0 RETRIEVAL ENGINE (NEW CORE)
    # =========================================================

    def _get_memory_context(self, query: str) -> str:
        """
        Memory 4.0 smart retrieval layer
        (Profile + Events + future semantic memory hook)
        """

        memory = self.memory.retrieve_relevant_memory(query)

        lines = ["🧠 USER LONG-TERM MEMORY"]

        # PROFILE MEMORY
        if memory.get("profile"):
            lines.append("\nProfile:")
            for k, v in memory["profile"].items():
                lines.append(f"- {k}: {v}")

        # EVENT MEMORY
        if memory.get("events"):
            lines.append("\nImportant Events:")
            for e in memory["events"]:
                lines.append(f"- [{e['type']}] {e['content']}")

        return "\n".join(lines)

    # =========================================================
    # 🧠 AUTO MEMORY PIPELINE
    # =========================================================

    def _auto_memory_capture(self, text: str):
        t = text.lower()

        if "my name is" in t:
            name = text.split("my name is")[-1].strip()
            self.memory.set_profile("name", name)

        if "i like" in t:
            value = text.split("i like")[-1].strip()
            self.memory.set_profile("likes", value)

        if "i hate" in t:
            value = text.split("i hate")[-1].strip()
            self.memory.set_profile("dislikes", value)

        # personality learning
        self._update_personality(text)

        # event capture
        self._auto_event_capture(text)

    # =========================================================
    # 🚀 MAIN PIPELINE
    # =========================================================

    def process_input(self, user_input: str) -> str:

        try:
            # 1. learn memory + events
            self._auto_memory_capture(user_input)

            # 2. email routing
            if self.email and self._is_email_query(user_input):
                return self._handle_email_query(user_input)

            # 3. base conversation context
            context = self.conversation.get_context()

            # 4. MEMORY 4.0 injection (NEW)
            memory_context = self._get_memory_context(user_input)

            context.insert(0, {
                "role": "system",
                "content": memory_context
            })

            # 5. personality injection (optional enhancement)
            personality_context = f"""
USER PERSONALITY:
- tone: {self.personality_cache['tone']}
- style: {self.personality_cache['communication_style']}
- interests: {', '.join(self.personality_cache['interests'])}
""".strip()

            context.insert(1, {
                "role": "system",
                "content": personality_context
            })

            # 6. generate response
            response = self.llm.generate_response(user_input, context)

            # 7. save conversation
            self.conversation.add_exchange(user_input, response)

            return response

        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return f"Error: {str(e)}"

    # =========================================================
    # 📧 EMAIL SYSTEM
    # =========================================================

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

    def send_email(self, to: str, subject: str, body: str) -> bool:
        return self.email.send_email(to, subject, body) if self.email else False

    # =========================================================
    # 🧠 MEMORY CONTROL
    # =========================================================

    def remember(self, key: str, value: str):
        self.memory.set_profile(key, value)

    def recall(self, key: str):
        return self.memory.get_profile(key)

    def show_memory(self):
        return {
            "profile": self.memory.get_all_profile(),
            "events": self.memory.get_events(),
            "personality": self.personality_cache
        }

    # =========================================================
    # 🧾 HISTORY
    # =========================================================

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

    # =========================================================
    # ⚙️ CONFIG
    # =========================================================

    def show_config(self):
        print("\n⚙️ System Status")
        print("=" * 30)

        print("OpenAI:", bool(os.getenv("OPENAI_API_KEY")))
        print("Ollama:", True)
        print("Email:", bool(self.email))

        print("\n🧠 MEMORY:")
        print(self.memory.get_all_profile())

        print("\n📌 EVENTS:")
        print(self.memory.get_events())

        print("\n🧬 PERSONALITY:")
        print(self.personality_cache)
