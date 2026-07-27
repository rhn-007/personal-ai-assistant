#!/usr/bin/env python3
"""
Personal AI Assistant - Main Entry Point
NEXUS Interface
"""

import sys
import threading
import time

from dotenv import load_dotenv
import typer

load_dotenv()

from src.core.assistant import PersonalAssistant
from src.utils.logger import setup_logger

logger = setup_logger(**name**)

app = typer.Typer()

assistant = None

# =========================================================

# INITIALIZE ASSISTANT

# =========================================================

def init_assistant():

```
global assistant

if assistant is None:

    try:

        logger.info(
            "Initializing Personal AI Assistant..."
        )

        assistant = PersonalAssistant()

    except Exception as e:

        logger.error(
            f"Failed to initialize assistant: {e}"
        )

        print(
            f"❌ Initialization error: {e}"
        )

        sys.exit(1)

return assistant
```

# =========================================================

# NEXUS PROCESSING ANIMATION

# =========================================================

def nexus_animation(
stop_event
):

```
frames = [

    "○──○──◉",

    "○──◉──○",

    "◉──○──○",

    "○──◉──○"

]

index = 0

while not stop_event.is_set():

    frame = frames[index]

    print(

        f"\r[NEXUS]  {frame}  Processing...",

        end="",

        flush=True

    )

    index = (

        index + 1

    ) % len(frames)

    time.sleep(
        0.25
    )

# -----------------------------------------------------
# CLEAR THE ANIMATION LINE COMPLETELY
# -----------------------------------------------------

print(

    "\r" + " " * 45 + "\r",

    end="",

    flush=True

)
```

# =========================================================

# PROCESS USER REQUEST WITH ANIMATION

# =========================================================

def process_with_animation(
bot,
user_input
):

```
result = {

    "response": None,

    "error": None

}

stop_event = threading.Event()

# -----------------------------------------------------
# RUN ASSISTANT IN BACKGROUND
# -----------------------------------------------------

def run_assistant():

    try:

        result["response"] = (

            bot.process_input(

                user_input

            )

        )

    except Exception as e:

        result["error"] = e

    finally:

        stop_event.set()

# -----------------------------------------------------
# START ASSISTANT PROCESSING
# -----------------------------------------------------

worker = threading.Thread(

    target=run_assistant,

    daemon=True

)

worker.start()

# -----------------------------------------------------
# START NEXUS ANIMATION
# -----------------------------------------------------

nexus_animation(

    stop_event

)

worker.join()

# -----------------------------------------------------
# HANDLE ERRORS
# -----------------------------------------------------

if result["error"]:

    raise result["error"]

return result["response"]
```

# =========================================================

# CHAT MODE

# =========================================================

@app.command()
def chat():

```
bot = init_assistant()

print(

    "\n🤖 NEXUS AI Assistant Ready "

    "(type 'help' for commands)\n"

)

while True:

    try:

        user_input = input(

            "You: "

        ).strip()

        if not user_input:

            continue

        cmd = user_input.lower()

        # -------------------------------------------------
        # EXIT
        # -------------------------------------------------

        if cmd in [

            "quit",

            "exit"

        ]:

            print(

                "Bye 👋"

            )

            break

        # -------------------------------------------------
        # HELP
        # -------------------------------------------------

        if cmd == "help":

            print_help()

            continue

        # -------------------------------------------------
        # PROCESS REQUEST
        # -------------------------------------------------

        print()

        response = (

            process_with_animation(

                bot,

                user_input

            )

        )

        print(

            f"\nAssistant: {response}\n"

        )

    except KeyboardInterrupt:

        print(

            "\nBye 👋"

        )

        break

    except Exception as e:

        logger.error(

            f"Chat error: {e}"

        )

        print(

            f"❌ Error: {e}"

        )
```

# =========================================================

# ASK MODE

# =========================================================

@app.command()
def ask(
question: str
):

```
bot = init_assistant()

try:

    response = (

        process_with_animation(

            bot,

            question

        )

    )

    print(

        response

    )

except Exception as e:

    logger.error(

        f"Ask error: {e}"

    )

    print(

        f"❌ Error: {e}"

    )
```

# =========================================================

# VERSION

# =========================================================

@app.command()
def version():

```
print(

    "NEXUS AI Assistant v1.0.0 "

    "(Ollama Ready)"

)
```

# =========================================================

# HELP

# =========================================================

def print_help():

```
print(

    """
```

📌 Commands:

* chat        → interactive mode
* ask "text"  → single question
* version     → show version
* exit        → quit chat

"""

```
)
```

# =========================================================

# ENTRY POINT

# =========================================================

if **name** == "**main**":

```
if len(sys.argv) == 1:

    init_assistant()

    chat()

else:

    app()
```
