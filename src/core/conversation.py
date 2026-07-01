"""
Conversation Management - Handles conversation flow and context (Ollama-ready)
"""

from typing import List, Dict
from datetime import datetime

from src.core.memory import MemoryManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationManager:
    """Manages conversation flow and context"""

    def __init__(self, memory_manager: MemoryManager):

        self.memory_manager = memory_manager

        self.current_context: List[Dict[str, str]] = []

        self.max_context_messages = 10

        self.system_prompt = {
            "role": "system",
            "content": "You are a helpful, intelligent personal AI assistant. Be concise, accurate, and helpful."
        }

    # ---------------- ADD EXCHANGE ----------------

    def add_exchange(self, user_message: str, assistant_response: str) -> None:

        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_response
        }

        self.memory_manager.save_exchange(exchange)

        self.current_context.append({"role": "user", "content": user_message})
        self.current_context.append({"role": "assistant", "content": assistant_response})

        self._trim_context()

    # ---------------- CONTEXT ----------------

    def get_context(self) -> List[Dict[str, str]]:

        return [self.system_prompt] + self.current_context

    def _trim_context(self):

        max_items = self.max_context_messages * 2

        if len(self.current_context) > max_items:
            self.current_context = self.current_context[-max_items:]

    # ---------------- HISTORY ----------------

    def get_history(self, limit: int = 10) -> List[Dict]:
        return self.memory_manager.get_history(limit)

    def clear_history(self) -> None:
        self.memory_manager.clear_history()
        self.current_context = []
        logger.info("Conversation history cleared")

    # ---------------- SYSTEM PROMPT ----------------

    def add_system_context(self, context: str) -> None:

        self.system_prompt = {
            "role": "system",
            "content": context
        }
