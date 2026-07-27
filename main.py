#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point
NEXUS Neural Pulse Loading Animation
"""

import sys
import threading
import time

from dotenv import load_dotenv
import typer


load_dotenv()


# =========================================================
# IMPORTS
# =========================================================

from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


app = typer.Typer()


assistant = None


# =========================================================
# NEXUS LOADING ANIMATION
# =========================================================

class NexusLoadingAnimation:

    """
    Neural Pulse animation for NEXUS.

    Animation:

        NEXUS  ◉──○──○
        NEXUS  ○──◉──○
        NEXUS  ○──○──◉
        NEXUS  ○──◉──○
    """

    def __init__(self):

        self.running = False

        self.thread = None

        self.frames = [

            "◉──○──○",

            "○──◉──○",

            "○──○──◉",

            "○──◉──○"

        ]

        self.frame_index = 0

    def _animate(self):

        while self.running:

            frame = (

                self.frames[

                    self.frame_index

                    % len(self.frames)

                ]

            )

            # \r returns to the beginning
            # of the current terminal line.

            print(

                f"\rNEXUS  {frame}  Processing...",

                end="",

                flush=True

            )

            self.frame_index += 1

            time.sleep(0.18)

    def start(self):

        if self.running:

            return

        self.running = True

        self.frame_index = 0

        self.thread = threading.Thread(

            target=self._animate,

            daemon=True

        )

        self.thread.start()

    def stop(self):

        if not self.running:

            return

        self.running = False

        if self.thread:

            self.thread.join(

                timeout=1

            )

        # Clear the animation line.

        print(

            "\r" + (" " * 60) + "\r",

            end="",

            flush=True

        )


# =========================================================
# ASSISTANT INITIALIZATION
# =========================================================

def init_assistant():

    """Initialize assistant once."""

    global assistant

    if assistant is None:

        try:

            logger.info(

                "Initializing Personal AI Assistant..."

            )

            assistant = PersonalAssistant()

        except Exception as e:

            logger.error(

                f"Failed to initialize assistant: {e}"

            )

            print(

                f"❌ Initialization error: {e}"

            )

            sys.exit(1)

    return assistant


# =========================================================
# PROCESS WITH NEXUS ANIMATION
# =========================================================

def process_with_animation(

    bot,

    user_input

):

    """

    Runs the assistant while the NEXUS
    neural pulse animation is active.
    """

    loading = NexusLoadingAnimation()

    loading.start()

    try:

        response = bot.process_input(

            user_input

        )

        return response

    finally:

        loading.stop()


# =========================================================
# CHAT MODE
# =========================================================

@app.command()

def chat():

    """Interactive chat mode."""

    bot = init_assistant()

    print(

        "\n🤖 NEXUS AI Assistant Ready "

        "(type 'help' for commands)\n"

    )

    while True:

        try:

            user_input = input(

                "You: "

            ).strip()

            if not user_input:

                continue

            cmd = user_input.lower()

            # -------------------------------------------------
            # EXIT
            # -------------------------------------------------

            if cmd in [

                "quit",

                "exit"

            ]:

                print(

                    "Bye 👋"

                )

                break

            # -------------------------------------------------
            # HELP
            # -------------------------------------------------

            if cmd == "help":

                print_help()

                continue

            # -------------------------------------------------
            # PROCESS REQUEST
            # -------------------------------------------------

            response = process_with_animation(

                bot,

                user_input

            )

            print(

                f"\nAssistant: {response}\n"

            )

        except KeyboardInterrupt:

            print(

                "\nBye 👋"

            )

            break

        except Exception as e:

            logger.error(

                f"Chat error: {e}"

            )

            print(

                f"❌ Error: {e}"

            )


# =========================================================
# ASK MODE
# =========================================================

@app.command()

def ask(

    question: str

):

    """Single question mode."""

    bot = init_assistant()

    try:

        response = process_with_animation(

            bot,

            question

        )

        print(

            response

        )

    except Exception as e:

        logger.error(

            f"Ask error: {e}"

        )

        print(

            f"❌ Error: {e}"

        )


# =========================================================
# VERSION
# =========================================================

@app.command()

def version():

    print(

        "NEXUS AI Assistant v1.0.0 "

        "(Ollama Ready)"

    )


# =========================================================
# HELP
# =========================================================

def print_help():

    print(

        """

📌 Commands:

- chat        → interactive mode
- ask "text"  → single question
- version     → show version
- exit        → quit chat

"""

    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) == 1:

        init_assistant()

        chat()

    else:

        app()
