import ollama


class OllamaIntegration:

    def __init__(
        self,
        model="phi3"
    ):

        self.model = model

        self.system_prompt = """

You are a highly intelligent personal AI assistant.

Your name is JARVIS.

You are running locally through Ollama.

You are the central intelligence of a personal computer assistant.

Your responsibilities:

1. Understand what the user means.
2. Answer questions clearly and accurately.
3. Use conversation context naturally.
4. Remember relevant information about the user when it is provided.
5. Be concise when the user asks a simple question.
6. Give detailed explanations when the user asks for detail.
7. Never pretend that you performed an action unless a tool actually performed it.
8. Never claim to have opened an application, sent an email, created a calendar event, or performed another computer action unless the system confirms that it happened.
9. Do not invent information.
10. If you do not know something, say so honestly.

PERSONALITY:

You are intelligent, calm, helpful, and professional.

You should feel like an advanced personal computer assistant.

You may occasionally use natural phrases such as:

- "Certainly."
- "Understood."
- "Done."
- "Right away."

However, do not overuse them.

Do not call the user "sir" in every response.

Do not be unnecessarily dramatic.

Do not explain your internal programming unless the user asks.

Always prioritize being useful over sounding robotic.

"""

    def generate_response(

        self,

        user_input,

        context=None

    ):

        try:

            messages = []

            # ---------------------------------------------
            # SYSTEM INSTRUCTIONS
            # ---------------------------------------------

            messages.append({

                "role": "system",

                "content": self.system_prompt

            })

            # ---------------------------------------------
            # CONVERSATION CONTEXT
            # ---------------------------------------------

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

                    # Avoid duplicate system prompts
                    if (

                        role == "system"

                        and content == self.system_prompt

                    ):

                        continue

                    messages.append({

                        "role": role,

                        "content": content

                    })

            # ---------------------------------------------
            # CURRENT USER MESSAGE
            # ---------------------------------------------

            messages.append({

                "role": "user",

                "content": user_input

            })

            # ---------------------------------------------
            # OLLAMA
            # ---------------------------------------------

            response = ollama.chat(

                model=self.model,

                messages=messages

            )

            # ---------------------------------------------
            # EXTRACT RESPONSE
            # ---------------------------------------------

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

            return (
                f"Ollama error: {str(e)}"
            )
