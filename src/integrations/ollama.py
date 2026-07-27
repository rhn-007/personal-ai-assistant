"""
Ollama Integration

Provides:

- Normal AI responses
- Memory analysis
- Relevant memory selection
- Local LLM communication
"""

import json

import ollama

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class OllamaIntegration:

    def __init__(
        self,
        model="qwen2.5:3b"
    ):

        self.model = model

        self.system_prompt = """

You are JARVIS, a highly intelligent personal AI assistant.

You run locally through Ollama.

Your responsibilities:

1. Understand what the user means.
2. Answer accurately and naturally.
3. Use conversation context when relevant.
4. Use memory when relevant.
5. Do not invent facts.
6. Never claim to perform an action unless a tool actually performed it.
7. Be concise for simple questions.
8. Be detailed when the user requests detail.
9. If you do not know something, say so honestly.

PERSONALITY:

You are calm, intelligent, helpful, professional, and natural.

You should feel like an advanced personal computer assistant.

Do not call the user "sir" constantly.

Do not be unnecessarily dramatic.

Do not mention internal programming unless asked.

"""

    # =========================================================
    # NORMAL RESPONSE
    # =========================================================

    def generate_response(
        self,
        user_input: str,
        context=None
    ) -> str:

        try:

            messages = [

                {
                    "role": "system",

                    "content": self.system_prompt

                }

            ]

            if context:

                for message in context:

                    if not isinstance(
                        message,
                        dict
                    ):

                        continue

                    role = message.get(
                        "role"
                    )

                    content = message.get(
                        "content"
                    )

                    if not role or not content:

                        continue

                    if (

                        role == "system"

                        and content == self.system_prompt

                    ):

                        continue

                    messages.append({

                        "role": role,

                        "content": content

                    })

            messages.append({

                "role": "user",

                "content": user_input

            })

            response = ollama.chat(

                model=self.model,

                messages=messages,

                options={

                    "temperature": 0.3,

                    "num_ctx": 4096

                }

            )

            if not response:

                return (
                    "I was unable to generate "
                    "a response."
                )

            message = response.get(
                "message"
            )

            if not message:

                return (
                    "I was unable to generate "
                    "a response."
                )

            content = message.get(
                "content"
            )

            if not content:

                return (
                    "I received an empty response "
                    "from the local AI model."
                )

            return content.strip()

        except Exception as e:

            logger.error(
                f"Ollama response error: {e}"
            )

            return (
                f"Ollama error: {str(e)}"
            )

    # =========================================================
    # MEMORY ANALYSIS
    # =========================================================

    def analyze_memory(
        self,
        user_query: str,
        memory_snapshot: dict
    ) -> dict:

        """
        Uses Ollama to select only memory relevant
        to the user's current question.
        """

        memory_json = json.dumps(
            memory_snapshot,
            ensure_ascii=False
        )

        prompt = f"""

You are the memory retrieval system for a personal AI assistant.

The user asked:

{user_query}

Below is the assistant's stored memory:

{memory_json}

Your task:

Select only the memories relevant to answering the user's
current question.

Rules:

1. Do not invent information.
2. Do not change facts.
3. Do not create new memories.
4. If the user asks what they remember, include relevant past conversations.
5. If the user asks about a specific topic, prioritize conversations about that topic.
6. If the user asks about the last conversation, prioritize the most recent relevant conversation.
7. If the user asks about the user personally, prioritize profile and semantic memory.
8. Keep the result concise.
9. Return ONLY valid JSON.

Use exactly this structure:

{{
    "profile": {{}},
    "semantic_memory": {{}},
    "events": [],
    "conversations": []
}}

"""

        try:

            response = ollama.chat(

                model=self.model,

                messages=[

                    {

                        "role": "system",

                        "content": (

                            "You are a precise memory "
                            "retrieval engine. "
                            "Return only valid JSON."
                        )

                    },

                    {

                        "role": "user",

                        "content": prompt

                    }

                ],

                format="json",

                options={

                    "temperature": 0.0,

                    "num_ctx": 4096

                }

            )

            content = (

                response

                .get(

                    "message",

                    {}

                )

                .get(

                    "content",

                    "{}"

                )

            )

            result = json.loads(
                content
            )

            if not isinstance(
                result,
                dict
            ):

                return {}

            return result

        except Exception as e:

            logger.error(
                f"Memory analysis error: {e}"
            )

            return {}

    # =========================================================
    # STATUS
    # =========================================================

    def get_status(self):

        try:

            ollama.list()

            return "ONLINE"

        except Exception:

            return "OFFLINE"
