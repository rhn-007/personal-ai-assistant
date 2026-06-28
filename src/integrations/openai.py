"""
OpenAI Integration - Wrapper for OpenAI API
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from utils.logger import setup_logger

logger = setup_logger(__name__)


class OpenAIIntegration:
    """Integration with OpenAI API"""
    
    def __init__(self):
        """Initialize OpenAI integration"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.system_prompt = self._get_system_prompt()
        
        logger.info(f"OpenAI integration initialized with model: {self.model}")
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the assistant"""
        return """You are a helpful, intelligent personal AI assistant. You help users with:
- Answering questions and providing information
- Task automation and scheduling
- File analysis and summarization
- Integration with various services (email, calendar, social media)
- Conversation history and context awareness

Be concise, clear, and helpful. When appropriate, ask clarifying questions."""
    
    def generate_response(self, user_input: str, context: List[Dict[str, str]] = None) -> str:
        """
        Generate response using OpenAI API
        
        Args:
            user_input: The user's message
            context: Previous conversation context (list of messages)
            
        Returns:
            The assistant's response
        """
        try:
            # Build messages
            messages = []
            
            # Add system prompt
            messages.append({
                'role': 'system',
                'content': self.system_prompt
            })
            
            # Add context if provided
            if context:
                messages.extend(context)
            
            # Add current user input
            messages.append({
                'role': 'user',
                'content': user_input
            })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract response
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {e}")
            raise
    
    def summarize_text(self, text: str) -> str:
        """
        Summarize provided text
        
        Args:
            text: Text to summarize
            
        Returns:
            Summary of the text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': f"Please summarize the following text:\n\n{text}"
                    }
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            raise
    
    def extract_information(self, text: str, instruction: str) -> str:
        """
        Extract specific information from text
        
        Args:
            text: Text to extract from
            instruction: What information to extract
            
        Returns:
            Extracted information
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': f"{instruction}\n\nText:\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            raise
