"""
Conversation Management - Handles conversation flow and context (Ollama-ready)
"""

from typing import List, Dict
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.memory import MemoryManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationManager:
    """Manages conversation flow and context"""

    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize conversation manager
        """
        self.memory_manager = memory_manager

        # Context storage for LLM
        self.current_context: List[Dict[str, str]] = []

        # prevents overflow in long chats
        self.max_context_messages = 10

        # system prompt (important for Ollama behavior)
        self.system_prompt = {
            "role": "system",
            "content": "You are a helpful, intelligent personal AI assistant. Be concise, accurate, and helpful."
        }

    # ---------------- ADD EXCHANGE ----------------

    def add_exchange(self, user_message: str, assistant_response: str) -> None:
        """Save chat exchange"""

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
        """
        Return full context for Ollama/OpenAI
        Always includes system prompt at top
        """

        return [self.system_prompt] + self.current_context

    def _trim_context(self):
        """Keep context size controlled"""
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
        """
        Dynamically change assistant behavior
        """

        self.system_prompt = {
            "role": "system",
            "content": context
        }
