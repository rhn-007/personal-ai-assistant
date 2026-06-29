#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point (Stable + Ollama Ready)
"""

import sys
from dotenv import load_dotenv
import typer

load_dotenv()

# FIX: keep imports clean and safe
from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

app = typer.Typer()
assistant = None


# ---------------- INIT ----------------

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


# ---------------- CHAT MODE ----------------

@app.command()
def chat():
    """Interactive chat mode"""
    bot = init_assistant()

    print("\n🤖 AI Assistant Ready (type 'help' for commands)\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd in ["quit", "exit"]:
                print("Bye 👋")
                break

            if cmd == "help":
                print_help()
                continue

            response = bot.process_input(user_input)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\nBye 👋")
            break

        except Exception as e:
            logger.error(f"Chat error: {e}")
            print(f"❌ Error: {e}")


# ---------------- ASK MODE ----------------

@app.command()
def ask(question: str):
    """Single question mode"""
    bot = init_assistant()

    try:
        response = bot.process_input(question)
        print(response)
    except Exception as e:
        logger.error(f"Ask error: {e}")
        print(f"❌ Error: {e}")


# ---------------- VERSION ----------------

@app.command()
def version():
    print("AI Assistant v1.0.0 (Ollama Ready)")


# ---------------- HELP ----------------

def print_help():
    print("""
📌 Commands:
- chat        → interactive mode
- ask "text"  → single question
- version     → show version
- exit        → quit chat
""")


# ---------------- ENTRY POINT ----------------

if __name__ == "__main__":
    if len(sys.argv) == 1:
        init_assistant()
        chat()
    else:
        app()
