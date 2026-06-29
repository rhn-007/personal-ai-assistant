import ollama

class OllamaIntegration:
    def __init__(self, model="phi3"):
        self.model = model

    def generate_response(self, user_input, context=None):
        try:
            messages = []

            if context:
                messages.extend(context)

            messages.append({"role": "user", "content": user_input})

            response = ollama.chat(
                model=self.model,
                messages=messages
            )

            return response["message"]["content"]

        except Exception as e:
            return f"Ollama error: {str(e)}"
