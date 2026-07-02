# Personal AI Assistant

A cross-platform CLI AI assistant that automates tasks, maintains conversation history, handles files, and integrates with various services including email.

## Features

- 🤖 **OpenAI Integration** - Powered by GPT-4
- 💬 **Conversation History** - Persistent memory of past conversations
- 📁 **File Handling** - Process and analyze files
- 📧 **Email Integration** - Gmail support with read/send capabilities
- 🔗 **Service Integrations** - Connect to Slack, calendar, weather, etc.
- ⚡ **Task Automation** - Automate repetitive tasks
- 📱 **Cross-Platform** - Works on desktop and mobile
- 🎯 **Context Awareness** - Remembers your preferences and past interactions

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/Rohan-201/personal-ai-assistant.git
cd personal-ai-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your API keys
cp .env.example .env
# Edit .env and add your OpenAI API key and other credentials
```

## Quick Start

### 1. Get API Keys

**OpenAI:**
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create API key
3. Add to `.env`: `OPENAI_API_KEY=your_key_here`

**Gmail (Optional but recommended):**
1. Enable Gmail API in [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Download as `credentials.json`
4. Place in project root

### 2. Run the Assistant

```bash
# Interactive mode
python main.py

# Ask a single question
python main.py ask "What is AI?"

# Check emails
python main.py email-check

# Send email
python main.py email-send recipient@example.com
```

## Usage

### Interactive Chat Mode

```bash
python main.py
```

Type any question or command:
```
You: What's the weather today?
Assistant: Based on current data...

You: Check my unread emails
Assistant: You have 3 unread emails...

You: help
# Shows all available commands
```

### Command Line Commands

```bash
# Basic queries
python main.py ask "Summarize this topic"
python main.py ask "Create a poem about coding"

# Task management
python main.py tasks              # Show available tasks
python main.py execute-task "daily_briefing"

# Email operations
python main.py email-check        # Show unread emails
python main.py email-send recipient@example.com

# Conversation management
python main.py config             # Show configuration
python main.py history            # Show conversation history
```

## Email Integration

### Supported Email Features

- ✅ **Read Emails** - Access inbox and search
- ✅ **Send Emails** - Send messages programmatically
- ✅ **Unread Check** - Get summary of unread emails
- ✅ **Email Search** - Find emails from specific senders
- ✅ **Email Digest** - Auto-summarize important emails
- ✅ **Mark as Read** - Manage email status
- ✅ **Delete Emails** - Remove unwanted messages

### Email Examples

```bash
# Check unread emails
> Check my unread emails

# Get emails from specific person
> Show emails from mom@example.com

# Send an email
python main.py email-send mom@example.com

# Email digest
python main.py execute-task "email_digest"
```

### Setting up Gmail

1. **Enable Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project
   - Search for "Gmail API" and enable it

2. **Create OAuth Credentials:**
   - Go to Credentials
   - Create OAuth 2.0 Client ID (Desktop application)
   - Download JSON file
   - Rename to `credentials.json` and place in project root

3. **First Run:**
   - When you first use email features, you'll be prompted to authenticate
   - Accept permissions
   - Token will be saved automatically

## Project Structure

```
personal-ai-assistant/
├── main.py                      ← RUN THIS
├── requirements.txt             ← Dependencies
├── .env                        ← Your credentials (create)
├── .env.example                ← Template
├── credentials.json            ← Gmail OAuth (optional)
├── token.pickle                ← Gmail token (auto-created)
├── README.md                   ← This file
├── .gitignore
├── src/
│   ├── core/
│   │   ├── assistant.py       ← Main logic
│   │   ├── conversation.py    ← Chat management
│   │   └── memory.py          ← Database storage
│   ├── integrations/
│   │   ├── openai.py          ← OpenAI API
│   │   └── email.py           ← Gmail integration
│   ├── utils/
│   │   ├── logger.py          ← Logging
│   │   └── file_handler.py    ← File operations
│   └── __init__.py
├── config/
│   └── config.yaml            ← Settings
├── data/
│   └── history.db            ← Chat history (auto-created)
└── logs/
    └── assistant.log         ← Log file (auto-created)
```

## Configuration

### Environment Variables (.env)

```env
# Required
OPENAI_API_KEY=sk-your-key

# Optional
GMAIL_EMAIL=your@gmail.com
GOOGLE_CREDENTIALS_FILE=credentials.json
SLACK_BOT_TOKEN=...
TWITTER_API_KEY=...
```

### Config File (config/config.yaml)

Customize behavior:
```yaml
assistant:
  name: "PersonalAI"
  
conversation:
  history_limit: 100
  context_window: 10

integrations:
  email:
    enabled: true
    service: "gmail"
```

## Task Automation

### Built-in Tasks

1. **Daily Briefing** - Weather, calendar, emails
2. **Weekly Report** - Summary of activities
3. **Social Media Post** - Generate tweet
4. **Email Digest** - Categorized email summary
5. **Check Emails** - Unread email check

### Execute Tasks

```bash
python main.py execute-task "daily_briefing"
python main.py execute-task "email_digest"
```

### Create Custom Tasks

Edit `config/tasks.yaml`:
```yaml
tasks:
  - name: "My Custom Task"
    trigger: "on_command"
    actions:
      - get_weather
      - send_email
```

## Conversation History

### View History

```bash
# In interactive mode
> history

# Or via CLI
python main.py history
```

### Clear History

```bash
> clear
```

### Search History

Conversation history is automatically saved to `data/history.db`. You can search through past conversations using the assistant:

```
> What did we talk about last week?
> Show me previous discussions about Python
```

## Troubleshooting

### OpenAI API Issues

**Error: "API key not found"**
- Verify `.env` has `OPENAI_API_KEY`
- Check key is valid at OpenAI dashboard

**Error: "Rate limit exceeded"**
- Wait a few moments before retrying
- Check your API plan limits

### Email Issues

**Error: "Gmail service not authenticated"**
- Download `credentials.json` from Google Cloud Console
- Place it in project root
- Run assistant again to authenticate

**Error: "Permission denied"**
- Ensure Gmail API is enabled in Google Cloud Console
- Check OAuth scopes include Gmail access

### General Issues

**Error: "Module not found"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Error in logs:**
Check `logs/assistant.log` for detailed error messages

## Development

### Running Tests

```bash
pytest tests/
pytest --cov  # With coverage
```

### Code Quality

```bash
# Format code
black src/

# Check for issues
flake8 src/
```

### Adding New Features

1. Create module in appropriate folder
2. Implement functionality
3. Update `assistant.py` to integrate
4. Add tests
5. Update documentation

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## Limitations & Future Work

### Current Limitations
- Email: Gmail only (more services coming)
- No voice interface yet
- Mobile app not built yet

### Planned Features
- 🎤 Voice input/output
- 📱 Mobile app (iOS/Android)
- 🔄 More email services (Outlook, etc.)
- 🤖 Advanced automation workflows
- 📊 Analytics dashboard
- 🔐 End-to-end encryption
- ☁️ Cloud sync

## License

MIT License - see LICENSE file for details

## Support

- 📖 Check README for common questions
- 🐛 Report bugs on GitHub Issues
- 💡 Suggest features via Discussions
- 📧 Email: your-email@example.com

## Author

Created by Rohan Sibi

---

**Happy automating!** 🚀
