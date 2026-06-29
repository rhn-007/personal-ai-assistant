#!/usr/bin/env python3

import sys
import os
from dotenv import load_dotenv
import typer

# FIX PATH ISSUE
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger

load_dotenv()

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
    print("AI Assistant Ready")

    while True:
        q = input("You: ")

        if q.lower() == "quit":
            break

        print("Assistant:", assistant.process_input(q))


@app.command()
def ask(question: str):
    init_assistant()
    print(assistant.process_input(question))


@app.command()
def version():
    print("Personal AI Assistant v1.0.0")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        init_assistant()
        chat()
    else:
        app()
