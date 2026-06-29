#!/usr/bin/env python3

import sys
import os
from dotenv import load_dotenv
import typer

# ---------------- FIX PATH ISSUE ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__)

app = typer.Typer()
assistant = None


# ---------------- INIT ----------------

def init_assistant():
    global assistant

    if assistant is None:
        logger.info("Initializing Personal AI Assistant...")
        assistant = PersonalAssistant()

    return assistant


# ---------------- COMMANDS ----------------

@app.command()
def chat():
    """Interactive chat mode"""
    bot = init_assistant()
    print("AI Assistant Ready (type 'quit' to exit)\n")

    while True:
        try:
            q = input("You: ")

            if q.lower().strip() in {"quit", "exit"}:
                break

            response = bot.process_input(q)
            print(f"Assistant: {response}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break


@app.command()
def ask(question: str):
    """Single question mode"""
    bot = init_assistant()
    print(bot.process_input(question))


@app.command()
def version():
    """Show version"""
    print("Personal AI Assistant v1.0.0")


# ---------------- ENTRY POINT ----------------

if __name__ == "__main__":
    # IMPORTANT FIX:
    # Always let Typer handle CLI properly
    app()
    
