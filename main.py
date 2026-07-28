#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point

NEXUS
"""

import sys

from dotenv import load_dotenv
import typer


load_dotenv()


from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger
from src.ui.display import NexusDisplay


logger = setup_logger(__name__)


app = typer.Typer()

assistant = None

display = NexusDisplay()



# =========================================================
# INITIALIZE ASSISTANT
# =========================================================

def init_assistant():

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
# CHAT MODE
# =========================================================

@app.command()

def chat():

    bot = init_assistant()


    print(
        "\n🤖 NEXUS Ready "
        "(type 'help' for commands)\n"
    )


    while True:

        try:

            user_input = input(
                "You: "
            ).strip()


            if not user_input:

                continue


            command = user_input.lower()



            # -------------------------------------------------
            # EXIT
            # -------------------------------------------------

            if command in [

                "quit",

                "exit"

            ]:

                print(
                    "Goodbye 👋"
                )

                break



            # -------------------------------------------------
            # HELP
            # -------------------------------------------------

            if command == "help":

                print_help()

                continue



            # -------------------------------------------------
            # NEXUS PROCESSING
            # -------------------------------------------------

            display.start_processing(
                "Processing..."
            )


            try:

                response = bot.process_input(
                    user_input
                )


            finally:

                display.stop_processing()



            print(
                f"\nAssistant: {response}\n"
            )



        except KeyboardInterrupt:

            print(
                "\nGoodbye 👋"
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

    bot = init_assistant()


    try:

        display.start_processing(
            "Processing..."
        )


        try:

            response = bot.process_input(
                question
            )


        finally:

            display.stop_processing()



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
        "NEXUS AI Assistant v1.0.0"
    )



# =========================================================
# HELP
# =========================================================

def print_help():

    print(
        """
📌 Commands:

- chat
    → Start interactive chat mode

- ask "text"
    → Ask NEXUS a single question

- version
    → Show current version

- exit
    → Exit chat mode

- quit
    → Exit chat mode

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
