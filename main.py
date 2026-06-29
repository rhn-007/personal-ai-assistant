#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point (Improved Stable Version)
"""

import sys
from dotenv import load_dotenv
import typer

load_dotenv()

from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

app = typer.Typer()
assistant = None


def init_assistant():
    """Initialize assistant once"""
    global assistant

    if assistant is None:
        try:
            logger.info("Initializing Personal AI Assistant...")
            assistant = PersonalAssistant()
        except Exception as e:
            logger.error(f"Failed to initialize assistant: {e}")
            print(f"❌ Initialization error: {e}")
            sys.exit(1)

    return assistant


@app.command()
def chat():
    """Interactive chat mode"""
    init_assistant()
    print("\n🤖 AI Assistant Ready (type 'help' for commands)\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit"]:
                print("Bye 👋")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            response = assistant.process_input(user_input)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\nBye 👋")
            break

        except Exception as e:
            logger.error(f"Chat error: {e}")
            print(f"❌ Error: {e}")


@app.command()
def ask(question: str):
    """Single question mode"""
    init_assistant()

    try:
        print(assistant.process_input(question))
    except Exception as e:
        logger.error(f"Ask error: {e}")
        print(f"❌ Error: {e}")


@app.command()
def version():
    """Show version"""
    print("AI Assistant v1.0.0")


def print_help():
    print("""
📌 Commands:
- chat     → interactive mode
- ask "q"  → single question
- version  → show version
- exit     → quit chat
""")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        init_assistant()
        chat()
    else:
        app()
