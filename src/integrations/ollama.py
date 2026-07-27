"""
Ollama Integration
==================

Handles communication between the Personal AI Assistant
and the local Ollama LLM.

The assistant uses Ollama instead of OpenAI.
"""

import ollama

from src.utils.logger import setup_logger


class OllamaIntegration:

    def __init__(self, model="phi3"):

        self.logger = setup_logger(__name__)

        self.model = model

        self.available = False

        self.logger.info(
            f"Initializing Ollama with model: {self.model}"
        )

        self._check_connection()

    # =========================================================
    # CHECK OLLAMA CONNECTION
    # =========================================================

    def _check_connection(self):

        try:

            models = ollama.list()

            self.available = True

            installed_models = []

            # Ollama can return model information in different
            # formats depending on the installed Ollama version.

            if isinstance(models, dict):

                model_list = models.get(
                    "models",
                    []
                )

                for model in model_list:

                    if isinstance(model, dict):

                        name = (

                            model.get("name")

                            or model.get("model")

                        )

                        if name:

                            installed_models.append(

                                name

                            )

            self.logger.info(

                "Ollama connection successful."

            )

            self.logger.info(

                f"Installed models: {installed_models}"

            )

            # Check whether the requested model exists.

            model_exists = any(

                installed_model == self.model

                or installed_model.startswith(

                    self.model + ":"

                )

                for installed_model in installed_models

            )

            if not model_exists:

                self.logger.warning(

                    f"Model '{self.model}' was not found "

                    "in the installed Ollama models."

                )

                self.logger.warning(

                    f"Available models: {installed_models}"

                )

        except Exception as e:

            self.available = False

            self.logger.error(

                f"Could not connect to Ollama: {e}"

            )

    # =========================================================
    # GENERATE RESPONSE
    # =========================================================

    def generate_response(

        self,

        user_input,

        context=None

    ):

        if not self.available:

            return (

                "Ollama is currently unavailable. "

                "Please make sure Ollama is running."

            )

        try:

            messages = []

            # Add previous conversation/context.

            if context:

                messages.extend(

                    context

                )

            # Add the current user message.

            messages.append(

                {

                    "role": "user",

                    "content": user_input

                }

            )

            self.logger.info(

                f"Sending request to Ollama "

                f"using model '{self.model}'."

            )

            response = ollama.chat(

                model=self.model,

                messages=messages

            )

            assistant_message = (

                response

                .get(

                    "message",

                    {}

                )

                .get(

                    "content",

                    ""

                )

            )

            if not assistant_message:

                self.logger.warning(

                    "Ollama returned an empty response."

                )

                return (

                    "I received an empty response from Ollama."

                )

            return assistant_message

        except Exception as e:

            self.logger.error(

                f"Ollama generation error: {e}"

            )

            return (

                f"Ollama error: {str(e)}"

            )

    # =========================================================
    # CHANGE MODEL
    # =========================================================

    def set_model(

        self,

        model

    ):

        if not model:

            return False

        self.model = model

        self.logger.info(

            f"Ollama model changed to: {self.model}"

        )

        self._check_connection()

        return self.available

    # =========================================================
    # GET STATUS
    # =========================================================

    def get_status(self):

        return {

            "available": self.available,

            "model": self.model

        }
