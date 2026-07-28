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
# CLEAN USER INPUT
# =========================================================


def clean_user_input(text):

    """
    Removes accidental prompt duplication.

    Example:

    You: hello

    becomes:

    hello
    """


    if not text:

        return text


    text = text.strip()


    if text.lower().startswith("you:"):

        text = text[4:].strip()


    return text





# =========================================================
# CHAT MODE
# =========================================================


@app.command()

def chat():


    bot = init_assistant()



    display.start()



    print(

        "\n🤖 NEXUS Ready "

        "(type 'help' for commands)\n"

    )



    while True:


        try:


            user_input = input(

                "You: "

            )



            user_input = clean_user_input(

                user_input

            )



            if not user_input:

                continue



            command = user_input.lower()



            # ---------------------------------------------
            # EXIT
            # ---------------------------------------------


            if command in [

                "quit",

                "exit"

            ]:


                display.stop()


                print(

                    "Goodbye 👋"

                )


                break




            # ---------------------------------------------
            # HELP
            # ---------------------------------------------


            if command == "help":


                print_help()


                continue





            # ---------------------------------------------
            # PROCESS REQUEST
            # ---------------------------------------------


            response = bot.process_input(

                user_input

            )



            print(

                f"\nNEXUS: {response}\n"

            )




        except KeyboardInterrupt:



            display.stop()


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



    display.start()



    try:



        question = clean_user_input(

            question

        )



        response = bot.process_input(

            question

        )



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
    → Show version

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
