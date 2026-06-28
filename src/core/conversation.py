"""
Conversation Management - Handles conversation flow and context
"""

from typing import List, Dict, Optional
from datetime import datetime
from .memory import MemoryManager
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationManager:
    """Manages conversation flow and context"""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize conversation manager
        
        Args:
            memory_manager: MemoryManager instance for storing history
        """
        self.memory_manager = memory_manager
        self.current_context = []
        self.max_context_messages = 10
    
    def add_exchange(self, user_message: str, assistant_response: str) -> None:
        """
        Add a user-assistant exchange to history
        
        Args:
            user_message: The user's message
            assistant_response: The assistant's response
        """
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'assistant': assistant_response
        }
        
        self.memory_manager.save_exchange(exchange)
        
        # Update context
        self.current_context.append({
            'role': 'user',
            'content': user_message
        })
        self.current_context.append({
            'role': 'assistant',
            'content': assistant_response
        })
        
        # Keep context size manageable
        if len(self.current_context) > self.max_context_messages * 2:
            self.current_context = self.current_context[-self.max_context_messages * 2:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        Get current conversation context for API calls
        
        Returns:
            List of message dictionaries with role and content
        """
        return self.current_context.copy()
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """
        Get conversation history from memory
        
        Args:
            limit: Maximum number of exchanges to retrieve
            
        Returns:
            List of conversation exchanges
        """
        return self.memory_manager.get_history(limit)
    
    def clear_history(self) -> None:
        """Clear all conversation history and context"""
        self.memory_manager.clear_history()
        self.current_context = []
        logger.info("Conversation history cleared")
    
    def add_system_context(self, context: str) -> None:
        """
        Add system context to conversation
        
        Args:
            context: System context message
        """
        system_message = {
            'role': 'system',
            'content': context
        }
        
        if not self.current_context or self.current_context[0]['role'] != 'system':
            self.current_context.insert(0, system_message)
