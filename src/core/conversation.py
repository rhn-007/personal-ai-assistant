"""
Conversation Management - Handles conversation flow and context
"""

from typing import List, Dict
from datetime import datetime

from src.core.memory import MemoryManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationManager:
    """Manages conversation flow and context"""

    def __init__(
        self,
        memory_manager: MemoryManager,
        max_context_messages: int = 10
    ):

        self.memory_manager = memory_manager

        self.max_context_messages = (
            max_context_messages
        )

        # -------------------------------------------------
        # SYSTEM PROMPT
        # -------------------------------------------------

        self.system_prompt = {

            "role": "system",

            "content": (
                "You are a helpful, intelligent "
                "personal AI assistant. "
                "Be concise, accurate, and helpful."
            )

        }

        # -------------------------------------------------
        # LOAD PREVIOUS CONVERSATION HISTORY
        # -------------------------------------------------

        self.current_context = []

        self._load_history()

    # =====================================================
    # LOAD HISTORY
    # =====================================================

    def _load_history(self):

        try:

            history = (

                self.memory_manager.get_history(

                    self.max_context_messages

                )

            )

            for exchange in history:

                user_message = exchange.get(
                    "user"
                )

                assistant_message = exchange.get(
                    "assistant"
                )

                if user_message:

                    self.current_context.append({

                        "role": "user",

                        "content": user_message

                    })

                if assistant_message:

                    self.current_context.append({

                        "role": "assistant",

                        "content": assistant_message

                    })

            self._trim_context()

            logger.info(

                f"Loaded {len(history)} "
                "conversation exchanges."

            )

        except Exception as e:

            logger.error(

                f"Failed to load conversation history: {e}"

            )

    # =====================================================
    # ADD EXCHANGE
    # =====================================================

    def add_exchange(

        self,

        user_message: str,

        assistant_response: str

    ) -> None:

        exchange = {

            "timestamp": datetime.now().isoformat(),

            "user": user_message,

            "assistant": assistant_response

        }

        # Save permanently

        self.memory_manager.save_exchange(

            exchange

        )

        # Add to current context

        self.current_context.append({

            "role": "user",

            "content": user_message

        })

        self.current_context.append({

            "role": "assistant",

            "content": assistant_response

        })

        self._trim_context()

    # =====================================================
    # GET CONTEXT
    # =====================================================

    def get_context(self) -> List[Dict[str, str]]:

        return [

            self.system_prompt

        ] + self.current_context

    # =====================================================
    # TRIM CONTEXT
    # =====================================================

    def _trim_context(self):

        max_items = (

            self.max_context_messages * 2

        )

        if len(

            self.current_context

        ) > max_items:

            self.current_context = (

                self.current_context[-max_items:]

            )

    # =====================================================
    # HISTORY
    # =====================================================

    def get_history(

        self,

        limit: int = 10

    ) -> List[Dict]:

        return (

            self.memory_manager.get_history(

                limit

            )

        )

    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    def clear_history(self) -> None:

        self.memory_manager.clear_history()

        self.current_context = []

        logger.info(

            "Conversation history cleared"

        )

    # =====================================================
    # SYSTEM PROMPT
    # =====================================================

    def add_system_context(

        self,

        context: str

    ) -> None:

        self.system_prompt = {

            "role": "system",

            "content": context

        }
