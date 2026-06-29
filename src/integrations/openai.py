"""
OpenAI Integration - Fixed Stable Version
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from utils.logger import setup_logger

logger = setup_logger(__name__)


class OpenAIIntegration:
    """Stable OpenAI wrapper"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        # FIX: avoid SDK proxy/transport conflicts
        self.client = OpenAI(
            api_key=api_key,
            timeout=60
        )

        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.system_prompt = (
            "You are a helpful personal AI assistant. "
            "Be concise, accurate, and helpful."
        )

        logger.info(f"OpenAI initialized with model: {self.model}")

    def generate_response(self, user_input: str, context: List[Dict[str, str]] = None) -> str:
        try:
            messages = [{"role": "system", "content": self.system_prompt}]

            if context:
                messages.extend(context)

            messages.append({"role": "user", "content": user_input})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI error: {e}")
        
            error_msg = str(e).lower()
        
            if "insufficient_quota" in error_msg:
                return "⚠️ OpenAI quota finished. Please check your billing at https://platform.openai.com/account/billing"
        
            if "invalid_api_key" in error_msg:
                return "⚠️ Invalid API key. Please check your OPENAI_API_KEY in .env"
        
            return f"AI error: {str(e)}"

    def summarize_text(self, text: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this:\n{text}"
                    }
                ],
                temperature=0.5,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Summary error: {str(e)}"

    def extract_information(self, text: str, instruction: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"{instruction}\n\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Extraction error: {str(e)}"
