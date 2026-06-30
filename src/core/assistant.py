"""
Main Assistant Class - Memory 4.0 Upgrade (Semantic + Event + Tool System Ready)
"""

import os
from dotenv import load_dotenv

from src.core.conversation import ConversationManager
from src.core.memory import MemoryManager
from src.integrations.ollama import OllamaIntegration
from src.integrations.email import EmailIntegration
from src.utils.logger import setup_logger

# 🧠 TOOL SYSTEM (NEW)
from src.tools.tool_manager import ToolManager
from src.tools.email_tool import EmailTool

load_dotenv()


class PersonalAssistant:
    """AI Assistant with Memory 4.0 + Tool Execution Layer"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing PersonalAssistant (Memory 4.0 + Tools)...")

        # =========================================================
        # CORE SYSTEMS
        # =========================================================

        self.memory = MemoryManager()
        self.conversation = ConversationManager(self.memory)
        self.llm = OllamaIntegration()

        # =========================================================
        # OPTIONAL EMAIL INTEGRATION
        # =========================================================

        try:
            self.email = EmailIntegration()
        except Exception as e:
            self.logger.warning(f"Email disabled: {e}")
            self.email = None

        # =========================================================
        # PERSONALITY CACHE
        # =========================================================

        self.personality_cache = {
            "tone": None,
            "communication_style": None,
            "interests": [],
        }

        # =========================================================
        # 🔧 TOOL SYSTEM (STAGE 1)
        # =========================================================

        self.tool_manager = ToolManager()

        # register tools
        self.tool_manager.register(EmailTool())

        # =========================================================
        # READY
        # =========================================================

        self.logger.info("Assistant ready with Memory 4.0 + Tools")

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

        if "short answer" in t:
            self.personality_cache["communication_style"] = "concise"

        if "detail" in t or "explain" in t:
            self.personality_cache["communication_style"] = "detailed"

    # =========================================================
    # 🧠 MEMORY
    # =========================================================

    def _get_memory_context(self, query: str):

        profile = self.memory.get_all_profile()
        semantic = self.memory.get_all_semantic()

        lines = ["🧠 USER MEMORY CONTEXT"]

        if profile:
            lines.append("\nProfile Memory:")
            for k, v in profile.items():
                lines.append(f"- {k}: {v}")

        if semantic:
            lines.append("\nSemantic Memory:")
            for cat, items in semantic.items():
                values = ", ".join([i["value"] for i in items])
                lines.append(f"- {cat}: {values}")

        return "\n".join(lines)

    # =========================================================
    # 🧠 AUTO MEMORY
    # =========================================================

    def _auto_memory_capture(self, text: str):

        t = text.lower()

        if "my name is" in t:
            name = text.split("my name is")[-1].strip()
            self.memory.set_profile("name", name)

        if "i like" in t:
            value = text.split("i like")[-1].strip()
            self.memory.add_semantic_memory("likes", value)

        if "i hate" in t:
            value = text.split("i hate")[-1].strip()
            self.memory.add_semantic_memory("dislikes", value)

        for w in ["ai", "coding", "anime", "music", "games", "python"]:
            if w in t:
                self.memory.add_semantic_memory("interests", w)

        self._update_personality(text)

    # =========================================================
    # 🚀 MAIN PIPELINE (UPDATED WITH TOOLS)
    # =========================================================

    def process_input(self, user_input: str) -> str:

        try:
            # 1. memory learning
            self._auto_memory_capture(user_input)

            # =====================================================
            # 🔧 TOOL EXECUTION LAYER (STAGE 1)
            # =====================================================

            tool_result = self.tool_manager.execute(user_input)

            if tool_result:
                return tool_result

            # =====================================================
            # EMAIL FALLBACK (legacy support)
            # =====================================================

            if self.email and self._is_email_query(user_input):
                return self._handle_email_query(user_input)

            # =====================================================
            # LLM CONTEXT BUILD
            # =====================================================

            context = self.conversation.get_context()

            memory_context = self._get_memory_context(user_input)

            personality_context = f"""
USER PERSONALITY:
- tone: {self.personality_cache['tone']}
- style: {self.personality_cache['communication_style']}
- interests: {', '.join(self.personality_cache['interests'])}
""".strip()

            context.insert(0, {"role": "system", "content": memory_context})
            context.insert(1, {"role": "system", "content": personality_context})

            # =====================================================
            # LLM RESPONSE
            # =====================================================

            response = self.llm.generate_response(user_input, context)

            self.conversation.add_exchange(user_input, response)

            return response

        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return f"Error: {str(e)}"

    # =========================================================
    # 📧 EMAIL (LEGACY)
    # =========================================================

    def _is_email_query(self, text: str) -> bool:
        keywords = ["email", "mail", "gmail", "inbox", "unread", "send", "from:"]
        return any(k in text.lower() for k in keywords)

    def _handle_email_query(self, user_input: str) -> str:

        try:
            text = user_input.lower()

            if "unread" in text:
                return self.email.get_email_summary()

            if "from:" in text:
                sender = text.split("from:")[1].split()[0]
                emails = self.email.get_emails_from(sender)

                return "\n".join(
                    f"- {e.get('subject','No Subject')}"
                    for e in emails
                )

            return self.email.get_email_summary()

        except Exception as e:
            return f"Email error: {e}"

    def send_email(self, to: str, subject: str, body: str):
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
            "semantic": self.memory.get_all_semantic(),
            "personality": self.personality_cache
        }

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

        print("\n🧠 SEMANTIC:")
        print(self.memory.get_all_semantic())

        print("\n🔧 TOOLS:")
        print(self.tool_manager.tools)
