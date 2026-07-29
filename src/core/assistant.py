from dotenv import load_dotenv

from src.core.conversation import ConversationManager
from src.ui.status import set_status, clear_status
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

    def __init__(self):

        self.status = "INITIALIZING"

        self.logger = setup_logger(__name__)

        self.logger.info(
            "Initializing Assistant..."
        )

        self.memory = MemoryManager()

        self.conversation = ConversationManager(
            self.memory
        )

        self.llm = OllamaIntegration()

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

        self.personality_cache = {
            "tone": None,
            "communication_style": None,
            "interests": []
        }

        self.tool_manager = ToolManager()

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

        self.planner = Planner(
            self.tool_manager
        )

        self.tool_manager.set_planner(
            self.planner
        )

        self.task_manager = TaskManager()

        self.agent_loop = AgentLoop(
            tool_manager=self.tool_manager,
            planner=self.planner,
            task_manager=self.task_manager
        )

        self.status = "READY"

        self.logger.info(
            "Assistant ready."
        )


    def get_status(self):

        return self.status


    def _needs_memory(
        self,
        text
    ):

        memory_keywords = [

            "remember",
            "recall",
            "previous",
            "last conversation",
            "what do you know about me",
            "my interests",
            "my name",
            "what did i tell you",
            "do you know me"

        ]

        text = text.lower()

        return any(
            keyword in text
            for keyword in memory_keywords
        )


    def _get_memory_context(
        self,
        query: str
    ) -> str:

        set_status(
            "Searching memory"
        )

        try:

            self.logger.info(
                "Retrieving memory from database..."
            )

            memory_snapshot = (
                self.memory.get_memory_snapshot(
                    conversation_limit=15
                )
            )

            self.logger.info(
                "Sending memory to Ollama for relevance analysis..."
            )

            relevant_memory = (
                self.llm.analyze_memory(
                    query,
                    memory_snapshot
                )
            )

        except Exception as e:

            self.logger.error(
                f"Memory retrieval failed: {e}"
            )

            relevant_memory = {}

        finally:

            clear_status()


        if not relevant_memory:

            return "No relevant memory was found."


        lines = [
            "RELEVANT MEMORY"
        ]


        profile = relevant_memory.get(
            "profile",
            {}
        )

        if profile:

            lines.append(
                "\nUSER PROFILE:"
            )

            for key, value in profile.items():

                lines.append(
                    f"- {key}: {value}"
                )


        semantic = relevant_memory.get(
            "semantic_memory",
            {}
        )

        if semantic:

            lines.append(
                "\nSEMANTIC MEMORY:"
            )

            for category, values in semantic.items():

                if isinstance(values, list):

                    for value in values:

                        if isinstance(value, dict):

                            value = value.get(
                                "value",
                                ""
                            )

                        if value:

                            lines.append(
                                f"- {category}: {value}"
                            )


        events = relevant_memory.get(
            "events",
            []
        )

        if events:

            lines.append(
                "\nEVENTS:"
            )

            for event in events:

                if isinstance(event, dict):

                    content = event.get(
                        "content",
                        ""
                    )

                    if content:

                        lines.append(
                            f"- {content}"
                        )


        conversations = relevant_memory.get(
            "conversations",
            []
        )

        if conversations:

            lines.append(
                "\nRELEVANT PREVIOUS CONVERSATIONS:"
            )

            for conversation in conversations:

                if not isinstance(
                    conversation,
                    dict
                ):

                    continue

                user_message = conversation.get(
                    "user",
                    ""
                )

                assistant_message = conversation.get(
                    "assistant",
                    ""
                )

                if user_message:

                    lines.append(
                        f"\nUser: {user_message}"
                    )

                if assistant_message:

                    lines.append(
                        f"Assistant: {assistant_message}"
                    )


        return "\n".join(
            lines
        )


    def _auto_memory_capture(
        self,
        text: str
    ):

        if text:

            self.memory.auto_learn(
                text
            )


    def _run_tools(
        self,
        user_input: str
    ):

        try:

            set_status(
                "Running tools"
            )


            if not result:
                return None

            if not result.get(
                "handled"
            ):
                return None

            return result.get(
                "result"
            )

        except Exception as e:

            clear_status()

            self.logger.error(
                f"Tool execution error: {e}"
            )

            return None

    
    def _run_agent_loop(
        self,
        user_input: str
    ):

        try:

            set_status(
                "Planning task"
            )

            if not self.agent_loop:
                clear_status()
                return None


            return result

        except Exception as e:

            clear_status()

            self.logger.error(
                f"Agent loop error: {e}"
            )

            return None


    def process_input(
        self,
        user_input: str
    ) -> str:

        try:

            if not user_input:

                return "Please enter something."

            user_input = user_input.strip()

            if not user_input:

                return "Please enter something."


            self.status = "PROCESSING"

            set_status("Processing request")


            self._auto_memory_capture(
                user_input
            )


            tool_result = self._run_tools(
                user_input
            )

            if tool_result:


                self.status = "READY"

                return tool_result


            agent_result = self._run_agent_loop(
                user_input
            )

            if agent_result:


                self.status = "READY"

                return agent_result


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


            if self._needs_memory(
                user_input
            ):

                memory_context = (
                    self._get_memory_context(
                        user_input
                    )
                )

            else:

                memory_context = (
                    "No memory retrieval required."
                )


            context = (
                self.conversation.get_context()
            )


            personality_context = f"""
USER PERSONALITY:

Tone:
{self.personality_cache['tone']}

Communication style:
{self.personality_cache['communication_style']}

Interests:
{', '.join(self.personality_cache['interests'])}
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


            set_status(
                "Thinking"
            )


            response = self.llm.generate_response(
                user_input,
                context
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

            return f"Error: {str(e)}"
            
        finally:
            
            clear_status()

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
                text.split(
                    "from:",
                    1
                )[1]
                .split()[0]
            )


            emails = self.email.get_emails_from(
                sender
            )


            if not emails:

                return "No emails found."


            return "\n".join(
                [
                    email.get(
                        "subject",
                        "No Subject"
                    )
                    for email in emails
                ]
            )


        return self.email.get_email_summary()



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



    def remember(
        self,
        key,
        value
    ):

        self.memory.set_profile(
            key,
            value
        )



    def recall(
        self,
        key
    ):

        return self.memory.get_profile(
            key
        )



    def show_memory(
        self
    ):

        return {
            "profile":
                self.memory.get_all_profile(),

            "semantic":
                self.memory.get_all_semantic(),

            "personality":
                self.personality_cache
        }



    def show_config(
        self
    ):

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
            bool(self.email)
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
