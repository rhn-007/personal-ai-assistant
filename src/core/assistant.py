"""
Main Assistant Class - Coordinates all components (Updated with Email)
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

from .conversation import ConversationManager
from .memory import MemoryManager
from ..integrations.openai import OpenAIIntegration
from ..integrations.email import EmailIntegration
from ..utils.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__)


class PersonalAssistant:
    """Main Personal AI Assistant with Email Support"""
    
    def __init__(self):
        """Initialize the assistant with all components"""
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing PersonalAssistant...")
        
        # Initialize components
        self.memory_manager = MemoryManager()
        self.conversation_manager = ConversationManager(self.memory_manager)
        self.openai = OpenAIIntegration()
        
        # Initialize email integration
        try:
            self.email = EmailIntegration()
        except Exception as e:
            self.logger.warning(f"Email integration not available: {e}")
            self.email = None
        
        self.logger.info("PersonalAssistant initialized successfully")
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and return response
        
        Args:
            user_input: The user's message
            
        Returns:
            The assistant's response
        """
        try:
            # Check if user is asking for email-related tasks
            if self.email and self._is_email_query(user_input):
                return self._handle_email_query(user_input)
            
            # Get conversation context
            context = self.conversation_manager.get_context()
            
            # Get response from OpenAI
            response = self.openai.generate_response(user_input, context)
            
            # Store in conversation history
            self.conversation_manager.add_exchange(user_input, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _is_email_query(self, user_input: str) -> bool:
        """Check if user input is email-related"""
        email_keywords = [
            'email', 'mail', 'gmail', 'send', 'unread',
            'inbox', 'message', 'from:', 'subject:'
        ]
        return any(keyword in user_input.lower() for keyword in email_keywords)
    
    def _handle_email_query(self, user_input: str) -> str:
        """Handle email-related queries"""
        try:
            user_lower = user_input.lower()
            
            # Get unread emails
            if 'unread' in user_lower or 'check' in user_lower:
                summary = self.email.get_email_summary()
                return summary
            
            # Send email
            if 'send' in user_lower and 'email' in user_lower:
                return "To send an email, please use: send_email(to='email@example.com', subject='...', body='...')"
            
            # Get emails from specific person
            if 'from:' in user_lower:
                sender = user_lower.split('from:')[1].strip().split()[0]
                emails = self.email.get_emails_from(sender)
                if emails:
                    return f"Found {len(emails)} emails from {sender}:\n" + \
                           "\n".join([f"- {e['subject']} ({e['date']})" for e in emails])
                return f"No emails found from {sender}"
            
            # Default: show email summary
            return self.email.get_email_summary()
        
        except Exception as e:
            self.logger.error(f"Error handling email query: {e}")
            return f"Error accessing email: {str(e)}"
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            True if successful
        """
        if not self.email:
            print("Email integration not available")
            return False
        
        return self.email.send_email(to, subject, body)
    
    def get_email_summary(self) -> str:
        """Get email summary"""
        if not self.email:
            return "Email integration not available"
        return self.email.get_email_summary()
    
    def show_history(self, limit: int = 10):
        """Show recent conversation history"""
        history = self.conversation_manager.get_history(limit)
        
        if not history:
            print("No conversation history found.")
            return
        
        print("\n📝 Recent Conversation History:")
        print("=" * 60)
        
        for i, exchange in enumerate(history, 1):
            print(f"\n[{i}] {exchange['timestamp']}")
            print(f"You: {exchange['user'][:100]}...")
            print(f"Assistant: {exchange['assistant'][:100]}...")
        
        print("\n" + "=" * 60)
    
    def clear_history(self):
        """Clear all conversation history"""
        self.conversation_manager.clear_history()
        self.logger.info("Conversation history cleared")
    
    def show_tasks(self):
        """Show available tasks"""
        print("\n📋 Available Tasks:")
        print("=" * 60)
        print("Daily Briefing - Get weather, calendar, and email summary")
        print("Weekly Report - Compile week's activities and achievements")
        print("Social Media Post - Generate and post content to Twitter")
        print("Email Digest - Summarize and categorize emails")
        print("Check Unread Emails - Show all unread messages")
        print("=" * 60)
    
    def execute_task(self, task_name: str):
        """Execute a specific task"""
        self.logger.info(f"Executing task: {task_name}")
        
        tasks = {
            "daily_briefing": self._daily_briefing,
            "weekly_report": self._weekly_report,
            "social_media": self._social_media_post,
            "email_digest": self._email_digest,
            "check_emails": self._check_emails,
        }
        
        task_func = tasks.get(task_name.lower().replace(" ", "_"))
        if task_func:
            task_func()
        else:
            raise ValueError(f"Unknown task: {task_name}")
    
    def show_config(self):
        """Show current configuration"""
        print("\n⚙️  Current Configuration:")
        print("=" * 60)
        print(f"OpenAI API: {'✓ Configured' if os.getenv('OPENAI_API_KEY') else '✗ Not configured'}")
        print(f"Gmail/Email: {'✓ Configured' if self.email else '✗ Not configured'}")
        print(f"Slack: {'✓ Configured' if os.getenv('SLACK_BOT_TOKEN') else '✗ Not configured'}")
        print(f"Google Calendar: {'✓ Configured' if os.getenv('GOOGLE_CALENDAR_ID') else '✗ Not configured'}")
        print(f"Weather: {'✓ Configured' if os.getenv('OPENWEATHER_API_KEY') else '✗ Not configured'}")
        print(f"Twitter: {'✓ Configured' if os.getenv('TWITTER_API_KEY') else '✗ Not configured'}")
        print("=" * 60)
    
    def _daily_briefing(self):
        """Execute daily briefing task"""
        print("📰 Generating daily briefing...")
        
        # Get email summary if available
        email_summary = ""
        if self.email:
            email_summary = f"\n\nEmails:\n{self.email.get_email_summary()}"
        
        response = self.process_input(f"Give me a daily briefing with weather, my calendar for today, and important emails{email_summary}")
        print(f"\nBriefing:\n{response}")
    
    def _weekly_report(self):
        """Execute weekly report task"""
        print("📊 Generating weekly report...")
        response = self.process_input("Create a weekly report of my activities, achievements, and upcoming tasks")
        print(f"\nReport:\n{response}")
    
    def _social_media_post(self):
        """Execute social media post task"""
        print("📱 Generating social media post...")
        response = self.process_input("Generate an engaging tweet about AI and technology trends")
        print(f"\nPost:\n{response}")
    
    def _email_digest(self):
        """Execute email digest task"""
        print("📧 Generating email digest...")
        
        if not self.email:
            print("Email integration not available")
            return
        
        email_summary = self.email.get_email_summary(max_emails=10)
        response = self.process_input(f"Summarize and categorize these emails by importance:\n{email_summary}")
        print(f"\nDigest:\n{response}")
    
    def _check_emails(self):
        """Check unread emails"""
        print("📧 Checking unread emails...")
        
        if not self.email:
            print("Email integration not available")
            return
        
        summary = self.email.get_email_summary()
        print(f"\n{summary}")
