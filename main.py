#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point
"""

import sys
from dotenv import load_dotenv
import typer

load_dotenv()

# IMPORTANT: use src-based imports ONLY
from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

app = typer.Typer()
assistant = None


def init_assistant():
    global assistant
    if assistant is None:
        logger.info("Initializing Personal AI Assistant...")
        assistant = PersonalAssistant()
    return assistant


@app.command()
def chat():
    init_assistant()
    print("\n🤖 AI Assistant Ready\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("Bye 👋")
            break

        if user_input.lower() == "help":
            print_help()
            continue

        response = assistant.process_input(user_input)
        print(f"\nAssistant: {response}\n")


@app.command()
def ask(question: str):
    init_assistant()
    print(assistant.process_input(question))


@app.command()
def version():
    print("AI Assistant v1.0.0")


def print_help():
    print("""
Commands:
- chat
- ask "question"
- version
- quit
""")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        init_assistant()
        chat()
    else:
        app()
