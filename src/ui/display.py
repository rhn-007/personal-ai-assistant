"""
NEXUS Display Controller

Handles:
- NEXUS loading animations
- Temporary status display
- Clearing animations after task completion

This file only controls visual output.

It reads status from:
    src.ui.status
"""


import sys
import time
import threading


from src.ui.status import (
    get_status,
    is_active
)



# =========================================================
# ANIMATION FRAMES
# =========================================================


FRAMES = [

    "○──○──◉",

    "○──◉──○",

    "◉──○──○",

    "○──◉──○"

]



# =========================================================
# DISPLAY SETTINGS
# =========================================================


animation_running = False



# =========================================================
# CLEAR CURRENT LINE
# =========================================================


def clear_line():

    """
    Removes the current NEXUS animation line.
    """

    sys.stdout.write(
        "\r" + " " * 80 + "\r"
    )

    sys.stdout.flush()



# =========================================================
# DRAW ANIMATION
# =========================================================


def show_animation():

    """
    Runs the NEXUS animation.

    Automatically disappears when
    status.py clears the task.
    """


    global animation_running


    animation_running = True


    index = 0


    while animation_running:


        status = get_status()


        if not status:

            break



        frame = FRAMES[index]



        sys.stdout.write(

            f"\r[NEXUS] {frame} {status}..."

        )


        sys.stdout.flush()



        index = (

            index + 1

        ) % len(FRAMES)



        time.sleep(0.25)



    clear_line()


    animation_running = False





# =========================================================
# START DISPLAY THREAD
# =========================================================


def start_display():

    """
    Starts the NEXUS display monitor.

    This runs separately from the assistant.
    """


    thread = threading.Thread(

        target=show_animation,

        daemon=True

    )


    thread.start()



    return thread





# =========================================================
# STOP DISPLAY
# =========================================================


def stop_display():

    """
    Force stop animation.
    """


    global animation_running


    animation_running = False


    clear_line()
