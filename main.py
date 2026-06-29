#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point
"""

import sys
from dotenv import load_dotenv
import typer

# Load environment variables
load_dotenv()

# Correct package imports
from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

app = typer.Typer()

# Global assistant instance
assistant = None


def init_assistant():
    """Initialize the assistant"""
    global assistant
    if assistant is None:
        logger.info("Initializing Personal AI Assistant...")
        assistant = PersonalAssistant()
    return assistant


@app.command()
def chat():
    """Start interactive chat mode"""
    init_assistant()
    logger.info("Starting chat mode. Type 'quit' to exit, 'help' for commands.")

    print("\n🤖 Personal AI Assistant")
    print("=" * 50)
    print("Type 'help' for available commands or 'quit' to exit\n")

    try:
        while True:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("👋 Goodbye!")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            if user_input.lower() == "history":
                assistant.show_history()
                continue

            if user_input.lower() == "clear":
                assistant.clear_history()
                print("✓ Conversation history cleared")
                continue

            response = assistant.process_input(user_input)
            print(f"\nAssistant: {response}\n")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error in chat mode: {e}")
        print(f"❌ Error: {e}")


@app.command()
def ask(question: str):
    """Ask a single question"""
    init_assistant()

    try:
        response = assistant.process_input(question)
        print(f"\nAssistant: {response}\n")

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        print(f"❌ Error: {e}")


@app.command()
def tasks():
    """Show configured tasks"""
    init_assistant()

    try:
        assistant.show_tasks()
    except Exception as e:
        logger.error(f"Error showing tasks: {e}")
        print(f"❌ Error: {e}")


@app.command()
def config():
    """Show current configuration"""
    init_assistant()

    try:
        assistant.show_config()
    except Exception as e:
        logger.error(f"Error showing config: {e}")
        print(f"❌ Error: {e}")


@app.command()
def execute_task(task_name: str):
    """Execute a specific task"""
    init_assistant()

    try:
        assistant.execute_task(task_name)
        print(f"✓ Task '{task_name}' executed successfully")

    except Exception as e:
        logger.error(f"Error executing task: {e}")
        print(f"❌ Error: {e}")


@app.command()
def email_check():
    """Check and display unread emails"""
    init_assistant()

    try:
        if assistant.email:
            assistant.execute_task("check_emails")
        else:
            print("❌ Email integration not available.")

    except Exception as e:
        logger.error(f"Error checking emails: {e}")
        print(f"❌ Error: {e}")


@app.command()
def email_send(
    to: str,
    subject: str,
    body: str
):
    """Send an email"""
    init_assistant()

    try:
        success = assistant.send_email(to, subject, body)

        if success:
            print(f"✓ Email sent to {to}")
        else:
            print("❌ Failed to send email")

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        print(f"❌ Error: {e}")


@app.command()
def version():
    """Show version"""
    print("Personal AI Assistant v1.0.0")


def print_help():
    """Help menu"""
    print("""
📚 Commands:
  chat              Start interactive mode
  ask "question"    Ask a question
  tasks             Show tasks
  config            Show configuration
  email-check       Check emails
  email-send        Send email
  version           Show version
  help              Show help
  quit              Exit chat
""")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        init_assistant()
        chat()
    else:
        app()
