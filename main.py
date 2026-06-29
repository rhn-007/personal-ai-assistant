#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point (Updated with Email)
"""

import os
import sys
from dotenv import load_dotenv
import typer
from typing import Optional

# Load environment variables
load_dotenv()


from src.core.assistant import PersonalAssistant
from utils.logger import setup_logger

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
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            if user_input.lower() == 'history':
                assistant.show_history()
                continue
            
            if user_input.lower() == 'clear':
                assistant.clear_history()
                print("✓ Conversation history cleared")
                continue
            
            # Get response from assistant
            response = assistant.process_input(user_input)
            print(f"\nAssistant: {response}\n")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error in chat mode: {e}")
        print(f"❌ Error: {e}")


@app.command()
def ask(question: str = typer.Argument(..., help="Question to ask the assistant")):
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
def execute_task(task_name: str = typer.Argument(..., help="Name of task to execute")):
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
            print("❌ Email integration not available. Please configure Gmail credentials.")
    except Exception as e:
        logger.error(f"Error checking emails: {e}")
        print(f"❌ Error: {e}")


@app.command()
def email_send(
    to: str = typer.Argument(..., help="Recipient email address"),
    subject: str = typer.Option(..., prompt=True, help="Email subject"),
    body: str = typer.Option(..., prompt=True, help="Email body")
):
    """Send an email"""
    init_assistant()
    try:
        if assistant.send_email(to, subject, body):
            print(f"✓ Email sent to {to}")
        else:
            print("❌ Failed to send email")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        print(f"❌ Error: {e}")


@app.command()
def version():
    """Show version information"""
    print("Personal AI Assistant v1.0.0")


def print_help():
    """Print help information"""
    help_text = """
📚 Available Commands:
  help          - Show this help message
  history       - View conversation history
  clear         - Clear conversation history
  tasks         - Show configured automation tasks
  config        - Show current configuration
  quit          - Exit the assistant

💼 Email Commands:
  check unread  - Check unread emails
  send email    - Send an email
  emails from X - Get emails from specific person

💡 Usage Examples:
  What's the weather today?
  Remind me to call Mom at 5 PM
  Summarize the file report.pdf
  Post a tweet about AI
  Check my unread emails
  Send me an email summary

🔧 CLI Commands:
  python main.py chat                    - Start interactive mode
  python main.py ask "question"          - Ask a single question
  python main.py tasks                   - Show tasks
  python main.py execute-task "task"     - Execute a task
  python main.py email-check            - Check unread emails
  python main.py email-send [to]         - Send an email
  python main.py config                  - Show configuration
  python main.py version                 - Show version
"""
    print(help_text)


if __name__ == "__main__":
    # Check if no arguments provided, start chat mode
    if len(sys.argv) == 1:
        init_assistant()
        chat()
    else:
        app()
