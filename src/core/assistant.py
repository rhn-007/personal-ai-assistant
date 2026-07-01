"""
Main Assistant Class - Memory 4.0 + Tool System + Planner + Agent Loop (Stage 5)
"""

import os
from dotenv import load_dotenv

from src.core.conversation import ConversationManager
from src.core.memory import MemoryManager
from src.integrations.ollama import OllamaIntegration
from src.integrations.email import EmailIntegration
from src.utils.logger import setup_logger

# ================= TOOL SYSTEM =================
from src.tools.tool_manager import ToolManager
from src.tools.email_tool import EmailTool

# ================= PLANNER =================
from src.planner.planner import Planner

# ================= AGENT LOOP =================
from src.agent.task_manager import TaskManager
from src.agent.agent_loop import AgentLoop

load_dotenv()


class PersonalAssistant:
    """AI Agent with Memory + Tools + Planner + Agent Loop (Stage 5)"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing Assistant (Stage 5 Agent)...")

        # =====================================================
        # CORE SYSTEMS
        # =====================================================
        self.memory = MemoryManager()
        self.conversation = ConversationManager(self.memory)
        self.llm = OllamaIntegration()

        # =====================================================
        # EMAIL SYSTEM
        # =====================================================
        try:
            self.email = EmailIntegration()
        except Exception:
            self.email = None

        # =====================================================
        # PERSONALITY
        # =====================================================
        self.personality_cache = {
            "tone": None,
            "communication_style": None,
            "interests": [],
        }

        # =====================================================
        # TOOL SYSTEM
        # =====================================================
        self.tool_manager = ToolManager()
        self.tool_manager.register(EmailTool())

        # =====================================================
        # PLANNER (Stage 4)
        # =====================================================
        self.planner = Planner(self.tool_manager)

        # =====================================================
        # AGENT LOOP (Stage 5)
        # =====================================================
        self.task_manager = TaskManager()
        self.agent_loop = AgentLoop(
            tool_manager=self.tool_manager,
            planner=self.planner,
            task_manager=self.task_manager
        )

        self.logger.info("Assistant ready (Stage 5 Complete)")

    # =========================================================
    # MEMORY CONTEXT
    # =========================================================

    def _get_memory_context(self, query: str):
        profile = self.memory.get_all_profile()
        semantic = self.memory.get_all_semantic()

        lines = ["🧠 USER MEMORY"]

        if profile:
            lines.append("\nProfile:")
            for k, v in profile.items():
                lines.append(f"- {k}: {v}")

        if semantic:
            lines.append("\nSemantic:")
            for cat, items in semantic.items():
                values = ", ".join([i["value"] for i in items])
                lines.append(f"- {cat}: {values}")

        return "\n".join(lines)

    # =========================================================
    # MEMORY LEARNING
    # =========================================================

    def _auto_memory_capture(self, text: str):
        t = text.lower()

        if "my name is" in t:
            self.memory.set_profile("name", text.split("my name is")[-1].strip())

        if "i like" in t:
            self.memory.add_semantic_memory("likes", text.split("i like")[-1].strip())

        if "i hate" in t:
            self.memory.add_semantic_memory("dislikes", text.split("i hate")[-1].strip())

        for w in ["ai", "coding", "anime", "music", "python"]:
            if w in t:
                self.memory.add_semantic_memory("interests", w)

    # =========================================================
    # TOOL LAYER
    # =========================================================

    def _run_tools(self, user_input: str):
        try:
            tool = self.tool_manager.get_tool(user_input)

            if not tool:
                return None

            self.logger.info(f"Tool triggered: {tool.__class__.__name__}")
            return tool.execute(user_input)

        except Exception as e:
            self.logger.error(f"Tool error: {e}")
            return None

    # =========================================================
    # PLANNER LAYER
    # =========================================================

    def _run_planner(self, user_input: str):
        plan = self.planner.create_plan(user_input)

        if not plan:
            return None

        results = []

        for step in plan:
            tool_name = step.get("tool")
            query = step.get("input", user_input)

            tool = self.tool_manager.get_tool(tool_name or query)

            if tool:
                output = tool.execute(query)
                results.append(output)

        return "\n".join([r for r in results if r])

    # =========================================================
    # AGENT LOOP (HIGHEST LEVEL INTELLIGENCE)
    # =========================================================

    def _run_agent_loop(self, user_input: str):
        try:
            if not self.agent_loop:
                return None

            return self.agent_loop.run(user_input)

        except Exception as e:
            self.logger.error(f"Agent loop error: {e}")
            return None

    # =========================================================
    # MAIN PIPELINE (FINAL STAGE 5 ARCHITECTURE)
    # =========================================================

    def process_input(self, user_input: str) -> str:

        try:
            # 1. MEMORY LEARNING
            self._auto_memory_capture(user_input)

            # =====================================================
            # 2. AGENT LOOP (HIGHEST PRIORITY)
            # =====================================================
            agent_result = self._run_agent_loop(user_input)
            if agent_result:
                return agent_result

            # =====================================================
            # 3. DIRECT TOOL EXECUTION
            # =====================================================
            tool_result = self._run_tools(user_input)
            if tool_result:
                return tool_result

            # =====================================================
            # 4. PLANNER EXECUTION
            # =====================================================
            plan_result = self._run_planner(user_input)
            if plan_result:
                return plan_result

            # =====================================================
            # 5. EMAIL FALLBACK
            # =====================================================
            if self.email and self._is_email_query(user_input):
                return self._handle_email_query(user_input)

            # =====================================================
            # 6. LLM CONTEXT BUILD
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
            # 7. LLM RESPONSE
            # =====================================================
            response = self.llm.generate_response(user_input, context)

            self.conversation.add_exchange(user_input, response)

            return response

        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return f"Error: {str(e)}"

    # =========================================================
    # EMAIL SYSTEM
    # =========================================================

    def _is_email_query(self, text: str):
        return any(k in text.lower() for k in ["email", "mail", "gmail", "inbox", "from:"])

    def _handle_email_query(self, user_input: str):
        text = user_input.lower()

        if "from:" in text:
            sender = text.split("from:")[1].split()[0]
            emails = self.email.get_emails_from(sender)
            return "\n".join([e.get("subject", "No Subject") for e in emails])

        return self.email.get_email_summary()

    def send_email(self, to, subject, body):
        return self.email.send_email(to, subject, body) if self.email else False

    # =========================================================
    # MEMORY CONTROL
    # =========================================================

    def remember(self, key, value):
        self.memory.set_profile(key, value)

    def recall(self, key):
        return self.memory.get_profile(key)

    def show_memory(self):
        return {
            "profile": self.memory.get_all_profile(),
            "semantic": self.memory.get_all_semantic(),
            "personality": self.personality_cache
        }

    # =========================================================
    # DEBUG
    # =========================================================

    def show_config(self):
        print("\n⚙️ SYSTEM STATUS")
        print("=" * 30)

        print("Tools:", [t.__class__.__name__ for t in self.tool_manager.tools])
        print("Email:", bool(self.email))
        print("Memory:", self.memory.get_all_profile())
        print("Semantic:", self.memory.get_all_semantic())
        print("Personality:", self.personality_cache)
