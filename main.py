#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point

NEXUS
"""

import sys
import threading
import time

from dotenv import load_dotenv
import typer


load_dotenv()


from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


app = typer.Typer()

assistant = None


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
# NEXUS PROCESSING ANIMATION
# =========================================================

def nexus_animation(stop_event):

    frames = [

        "○──○──◉",

        "○──◉──○",

        "◉──○──○",

        "○──◉──○"

    ]

    index = 0


    while not stop_event.is_set():

        frame = frames[index]


        print(

            f"\r[NEXUS]  {frame}  Processing...",

            end="",

            flush=True

        )


        index = (

            index + 1

        ) % len(frames)


        time.sleep(

            0.25

        )


    # -----------------------------------------------------
    # CLEAR THE ANIMATION LINE
    # -----------------------------------------------------

    print(

        "\r" + " " * 100 + "\r",

        end="",

        flush=True

    )


# =========================================================
# PROCESS INPUT WITH ANIMATION
# =========================================================

def process_with_animation(

    bot,

    user_input

):

    result = {

        "response": None,

        "error": None

    }


    stop_event = threading.Event()


    # -----------------------------------------------------
    # RUN ASSISTANT IN BACKGROUND
    # -----------------------------------------------------

    def run_assistant():

        try:

            result["response"] = (

                bot.process_input(

                    user_input

                )

            )

        except Exception as e:

            result["error"] = e

        finally:

            stop_event.set()


    worker = threading.Thread(

        target=run_assistant,

        daemon=True

    )


    worker.start()


    # -----------------------------------------------------
    # RUN ANIMATION
    # -----------------------------------------------------

    nexus_animation(

        stop_event

    )


    worker.join()


    if result["error"]:

        raise result["error"]


    return result["response"]


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


            command = (

                user_input.lower()

            )


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
            # PROCESS REQUEST
            # -------------------------------------------------

            response = (

                process_with_animation(

                    bot,

                    user_input

                )

            )


            print(

                f"\nAssistant: "

                f"{response}\n"

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

        response = (

            process_with_animation(

                bot,

                question

            )

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
    → Show the current version

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
