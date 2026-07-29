#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point

NEXUS
"""

import sys
import time

from dotenv import load_dotenv
import typer

from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger
from src.ui.display import NexusDisplay
from src.ui.status import clear_status


load_dotenv()


logger = setup_logger(__name__)


app = typer.Typer()


assistant = None

display = NexusDisplay()



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



def clean_user_input(text):

    if not text:

        return ""


    text = text.strip()


    if text.lower().startswith(
        "you:"
    ):

        text = text[4:].strip()


    return text



@app.command()
def chat():

    bot = init_assistant()

    display.start()


    print(
        "\n🤖 N.E.X.U.S [Neural EXecutive Utility System] Ready (type 'help' for commands)\n"
    )


    try:

        while True:

            clear_status()

            user_input = input(
                "You: "
            ).strip()


            user_input = clean_user_input(
                user_input
            )


            if not user_input:

                continue


            logger.info(
                f"User input: {user_input}"
            )


            command = user_input.lower()



            if command in [
                "quit",
                "exit"
            ]:

                print(
                    "Goodbye 👋"
                )

                break



            if command == "help":

                print_help()

                continue



            response = bot.process_input(
                user_input
            )


            clear_status()


            print(
                f"\nNEXUS: {response}\n"
            )

            display.start()


            time.sleep(0.05)



    except KeyboardInterrupt:

        print(
            "\nGoodbye 👋"
        )


    except Exception as e:

        logger.error(
            f"Chat error: {e}"
        )

        print(
            f"❌ Error: {e}"
        )


    finally:

        display.stop()



@app.command()
def ask(
    question: str
):

    bot = init_assistant()

    display.start()


    try:

        question = clean_user_input(
            question
        )


        if not question:

            print(
                "Please enter a question."
            )

            return


        logger.info(
            f"User input: {question}"
        )


        response = bot.process_input(
            question
        )


        clear_status()


        print(
            f"NEXUS: {response}"
        )


    except Exception as e:

        logger.error(
            f"Ask error: {e}"
        )


        print(
            f"❌ Error: {e}"
        )


    finally:

        display.stop()



@app.command()
def version():

    print(
        "NEXUS AI Assistant v1.0.0"
    )



def print_help():

    print(
"""
📌 Commands:

chat
    → Start interactive chat mode

ask "text"
    → Ask NEXUS a single question

version
    → Show version

exit
    → Exit chat mode

quit
    → Exit chat mode

"""
    )



if __name__ == "__main__":

    app()
