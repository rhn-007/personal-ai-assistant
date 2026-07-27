"""
Main Assistant Class
Memory + Tool System + Planner + Agent Loop

Architecture:

User Input
    ↓
Memory Capture
    ↓
Direct Tool Execution
    ↓
Agent Loop
    ↓
Email Fallback
    ↓
Ollama LLM Fallback
"""

from dotenv import load_dotenv

from src.core.conversation import ConversationManager
from src.core.memory import MemoryManager

from src.integrations.ollama import OllamaIntegration
from src.integrations.email import EmailIntegration

from src.utils.logger import setup_logger

from src.tools.system_tool import SystemTool
from src.tools.tool_manager import ToolManager
from src.tools.email_tool import EmailTool
from src.tools.spotify_tool import SpotifyTool
from src.tools.calendar_tool import CalendarTool
from src.tools.browser_tool import BrowserTool

from src.planner.planner import Planner

from src.agent.task_manager import TaskManager
from src.agent.agent_loop import AgentLoop


load_dotenv()


class PersonalAssistant:

    """
    AI Assistant with:

    - Conversation memory
    - Semantic memory
    - User profile memory
    - Ollama LLM
    - Email integration
    - Calendar tools
    - Spotify tools
    - System tools
    - Browser tools
    - Planner
    - Agent loop
    """

    def __init__(self):

        # =====================================================
        # ASSISTANT STATUS
        # =====================================================

        self.status = "INITIALIZING"

        # =====================================================
        # LOGGER
        # =====================================================

        self.logger = setup_logger(
            __name__
        )

        self.logger.info(
            "Initializing Assistant..."
        )

        # =====================================================
        # CORE SYSTEMS
        # =====================================================

        self.memory = MemoryManager()

        self.conversation = ConversationManager(
            self.memory
        )

        self.llm = OllamaIntegration()

        # =====================================================
        # EMAIL SYSTEM
        # =====================================================

        try:

            self.email = EmailIntegration()

            self.logger.info(
                "Email integration initialized."
            )

        except Exception as e:

            self.email = None

            self.logger.warning(
                f"Email integration unavailable: {e}"
            )

        # =====================================================
        # PERSONALITY
        # =====================================================

        self.personality_cache = {

            "tone": None,

            "communication_style": None,

            "interests": []

        }

        # =====================================================
        # TOOL SYSTEM
        # =====================================================

        self.tool_manager = ToolManager()

        # =====================================================
        # REGISTER TOOLS
        # =====================================================

        self.tool_manager.register(
            EmailTool()
        )

        self.tool_manager.register(
            SpotifyTool()
        )

        self.tool_manager.register(
            CalendarTool()
        )

        self.tool_manager.register(
            SystemTool()
        )

        self.tool_manager.register(

            BrowserTool(

                llm=self.llm

            )

        )

        # =====================================================
        # PLANNER
        # =====================================================

        self.planner = Planner(
            self.tool_manager
        )

        self.tool_manager.set_planner(
            self.planner
        )

        # =====================================================
        # AGENT SYSTEM
        # =====================================================

        self.task_manager = TaskManager()

        self.agent_loop = AgentLoop(

            tool_manager=self.tool_manager,

            planner=self.planner,

            task_manager=self.task_manager

        )

        # =====================================================
        # ASSISTANT READY
        # =====================================================

        self.status = "READY"

        self.logger.info(
            "Assistant ready."
        )

    # =========================================================
    # STATUS
    # =========================================================

    def get_status(self):

        return self.status

    # =========================================================
    # MEMORY CONTEXT
    # =========================================================

    def _get_memory_context(
        self,
        query: str
    ):

        profile = (

            self.memory.get_all_profile()

        )

        semantic = (

            self.memory.get_all_semantic()

        )

        lines = [

            "🧠 USER MEMORY"

        ]

        # -----------------------------------------------------
        # PROFILE MEMORY
        # -----------------------------------------------------

        if profile:

            lines.append(

                "\nProfile:"

            )

            for key, value in profile.items():

                lines.append(

                    f"- {key}: {value}"

                )

        # -----------------------------------------------------
        # SEMANTIC MEMORY
        # -----------------------------------------------------

        if semantic:

            lines.append(

                "\nSemantic:"

            )

            for category, items in semantic.items():

                values = ", ".join(

                    [

                        str(item)

                        for item in items

                    ]

                )

                lines.append(

                    f"- {category}: {values}"

                )

        return "\n".join(

            lines

        )

    # =========================================================
    # AUTOMATIC MEMORY CAPTURE
    # =========================================================

    def _auto_memory_capture(
        self,
        text: str
    ):

        if not text:

            return

        t = text.lower()

        # -----------------------------------------------------
        # NAME
        # -----------------------------------------------------

        if "my name is" in t:

            name = (

                text.split(

                    "my name is",

                    1

                )[1].strip()

            )

            if name:

                self.memory.set_profile(

                    "name",

                    name

                )

        # -----------------------------------------------------
        # LIKES
        # -----------------------------------------------------

        if "i like" in t:

            like = (

                text.split(

                    "i like",

                    1

                )[1].strip()

            )

            if like:

                self.memory.add_semantic_memory(

                    "likes",

                    like

                )

        # -----------------------------------------------------
        # DISLIKES
        # -----------------------------------------------------

        if "i hate" in t:

            dislike = (

                text.split(

                    "i hate",

                    1

                )[1].strip()

            )

            if dislike:

                self.memory.add_semantic_memory(

                    "dislikes",

                    dislike

                )

        # -----------------------------------------------------
        # INTERESTS
        # -----------------------------------------------------

        for word in [

            "ai",

            "coding",

            "anime",

            "music",

            "python",

            "robot",

            "robotics"

        ]:

            if word in t:

                self.memory.add_semantic_memory(

                    "interests",

                    word

                )

    # =========================================================
    # DIRECT TOOL EXECUTION
    # =========================================================

    def _run_tools(
        self,
        user_input: str
    ):

        try:

            tool_result = (

                self.tool_manager.execute(

                    user_input

                )

            )

            if not tool_result:

                return None

            if not tool_result.get(

                "handled"

            ):

                return None

            return tool_result.get(

                "result"

            )

        except Exception as e:

            self.logger.error(

                f"Tool execution error: {e}"

            )

            return None

    # =========================================================
    # AGENT LOOP
    # =========================================================

    def _run_agent_loop(
        self,
        user_input: str
    ):

        try:

            if not self.agent_loop:

                return None

            return self.agent_loop.run(

                user_input

            )

        except Exception as e:

            self.logger.error(

                f"Agent loop error: {e}"

            )

            return None

    # =========================================================
    # MAIN PROCESSING PIPELINE
    # =========================================================

    def process_input(
        self,
        user_input: str
    ) -> str:

        try:

            # =================================================
            # VALIDATE INPUT
            # =================================================

            if not user_input:

                return (

                    "Please enter something."

                )

            user_input = (

                user_input.strip()

            )

            if not user_input:

                return (

                    "Please enter something."

                )

            # =================================================
            # SET PROCESSING STATUS
            # =================================================

            self.status = "PROCESSING"

            # =================================================
            # 1. MEMORY CAPTURE
            # =================================================

            self._auto_memory_capture(

                user_input

            )

            # =================================================
            # 2. DIRECT TOOL EXECUTION
            # =================================================

            tool_result = self._run_tools(

                user_input

            )

            if tool_result:

                self.logger.info(

                    "Request handled by direct tool."

                )

                self.status = "READY"

                return tool_result

            # =================================================
            # 3. AGENT LOOP
            # =================================================

            agent_result = self._run_agent_loop(

                user_input

            )

            if agent_result:

                self.status = "READY"

                return agent_result

            # =================================================
            # 4. EMAIL FALLBACK
            # =================================================

            if (

                self.email

                and self._is_email_query(

                    user_input

                )

            ):

                response = self._handle_email_query(

                    user_input

                )

                self.status = "READY"

                return response

            # =================================================
            # 5. LLM FALLBACK
            # =================================================

            context = (

                self.conversation.get_context()

            )

            memory_context = (

                self._get_memory_context(

                    user_input

                )

            )

            personality_context = f"""

USER PERSONALITY:

- tone: {self.personality_cache['tone']}

- style: {self.personality_cache['communication_style']}

- interests: {
    ', '.join(
        self.personality_cache['interests']
    )
}

""".strip()

            context.insert(

                0,

                {

                    "role": "system",

                    "content": memory_context

                }

            )

            context.insert(

                1,

                {

                    "role": "system",

                    "content": personality_context

                }

            )

            response = (

                self.llm.generate_response(

                    user_input,

                    context

                )

            )

            self.conversation.add_exchange(

                user_input,

                response

            )

            self.status = "READY"

            return response

        except Exception as e:

            self.status = "ERROR"

            self.logger.error(

                f"Processing error: {e}"

            )

            return (

                f"Error: {str(e)}"

            )

    # =========================================================
    # EMAIL QUERY DETECTION
    # =========================================================

    def _is_email_query(
        self,
        text: str
    ):

        if not text:

            return False

        text = text.lower()

        return any(

            keyword in text

            for keyword in [

                "email",

                "mail",

                "gmail",

                "inbox",

                "from:"

            ]

        )

    # =========================================================
    # EMAIL QUERY HANDLER
    # =========================================================

    def _handle_email_query(
        self,
        user_input: str
    ):

        if not self.email:

            return (

                "Email integration is not available."

            )

        text = user_input.lower()

        if "from:" in text:

            sender = (

                text

                .split(

                    "from:",

                    1

                )[1]

                .split()[0]

            )

            emails = (

                self.email.get_emails_from(

                    sender

                )

            )

            if not emails:

                return (

                    "No emails found."

                )

            return "\n".join(

                [

                    email.get(

                        "subject",

                        "No Subject"

                    )

                    for email in emails

                ]

            )

        return (

            self.email.get_email_summary()

        )

    # =========================================================
    # SEND EMAIL
    # =========================================================

    def send_email(
        self,
        to,
        subject,
        body
    ):

        if not self.email:

            return False

        return self.email.send_email(

            to,

            subject,

            body

        )

    # =========================================================
    # MEMORY CONTROL
    # =========================================================

    def remember(
        self,
        key,
        value
    ):

        self.memory.set_profile(

            key,

            value

        )

    # =========================================================
    # RECALL MEMORY
    # =========================================================

    def recall(
        self,
        key
    ):

        return self.memory.get_profile(

            key

        )

    # =========================================================
    # SHOW MEMORY
    # =========================================================

    def show_memory(self):

        return {

            "profile":

                self.memory.get_all_profile(),

            "semantic":

                self.memory.get_all_semantic(),

            "personality":

                self.personality_cache

        }

    # =========================================================
    # DEBUG CONFIGURATION
    # =========================================================

    def show_config(self):

        print(

            "\n⚙️ SYSTEM STATUS"

        )

        print(

            "=" * 30

        )

        print(

            "Status:",

            self.status

        )

        print(

            "Tools:",

            list(

                self.tool_manager.tools.keys()

            )

        )

        print(

            "Email:",

            bool(

                self.email

            )

        )

        print(

            "Ollama:",

            self.llm.get_status()

        )

        print(

            "Memory:",

            self.memory.get_all_profile()

        )

        print(

            "Semantic:",

            self.memory.get_all_semantic()

        )

        print(

            "Personality:",

            self.personality_cache

        )
