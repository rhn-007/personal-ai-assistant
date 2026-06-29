#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point
"""

import sys
from dotenv import load_dotenv
import typer

# Load environment variables
load_dotenv()

# FIX: ensure consistent package imports
from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

app = typer.Typer()

assistant = None


def init_assistant():
    """Initialize assistant safely"""
    global assistant

    if assistant is None:
        logger.info("Initializing Personal AI Assistant...")
        assistant = PersonalAssistant()

    return assistant


@app.command()
def chat():
    """Interactive chat mode"""
    init_assistant()

    print("\n🤖 Personal AI Assistant")
    print("=" * 50)
    print("Type 'help' for commands or 'quit' to exit\n")

    try:
        while True:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd == "quit":
                print("👋 Goodbye!")
                break

            if cmd == "help":
                print_help()
                continue

            if cmd == "history":
                assistant.show_history()
                continue

            if cmd == "clear":
                assistant.clear_history()
                print("✓ History cleared")
                continue

            response = assistant.process_input(user_input)
            print(f"\nAssistant: {response}\n")

    except KeyboardInterrupt:
        print("\n👋 Exiting...")


@app.command()
def ask(question: str):
    """Ask a single question"""
    init_assistant()

    try:
        response = assistant.process_input(question)
        print(f"\nAssistant: {response}\n")

    except Exception as e:
        logger.error(f"Ask error: {e}")
        print(f"❌ Error: {e}")


@app.command()
def tasks():
    """Show tasks"""
    init_assistant()

    try:
        assistant.show_tasks()
    except Exception as e:
        logger.error(f"Tasks error: {e}")
        print(f"❌ Error: {e}")


@app.command()
def config():
    """Show config"""
    init_assistant()

    try:
        assistant.show_config()
    except Exception as e:
        logger.error(f"Config error: {e}")
        print(f"❌ Error: {e}")


@app.command()
def execute_task(task_name: str):
    """Run task"""
    init_assistant()

    try:
        assistant.execute_task(task_name)
        print(f"✓ Task '{task_name}' executed")
    except Exception as e:
        logger.error(f"Task error: {e}")
        print(f"❌ Error: {e}")


@app.command()
def email_check():
    """Check emails"""
    init_assistant()

    try:
        if getattr(assistant, "email", None):
            assistant.execute_task("check_emails")
        else:
            print("❌ Email not configured")
    except Exception as e:
        logger.error(f"Email check error: {e}")
        print(f"❌ Error: {e}")


@app.command()
def email_send(to: str, subject: str, body: str):
    """Send email"""
    init_assistant()

    try:
        success = assistant.send_email(to, subject, body)

        if success:
            print(f"✓ Sent to {to}")
        else:
            print("❌ Failed to send email")

    except Exception as e:
        logger.error(f"Email send error: {e}")
        print(f"❌ Error: {e}")


@app.command()
def version():
    print("Personal AI Assistant v1.0.0")


def print_help():
    print("""
Commands:
  chat
  ask "question"
  tasks
  config
  execute-task <name>
  email-check
  email-send <to> <subject> <body>
  version
""")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        init_assistant()
        chat()
    else:
        app()
