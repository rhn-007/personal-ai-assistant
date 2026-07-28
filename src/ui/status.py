"""
NEXUS Status Manager

Handles the current operation state of NEXUS.

This file does NOT print anything.

It only stores the current status so that
display.py can show the temporary animation.

Example:

set_status("Searching memory")

display.py:
[NEXUS] ○──◉──○ Searching memory...


clear_status()

display.py removes animation.
"""


import threading



# =========================================================
# GLOBAL STATUS STORAGE
# =========================================================


_current_status = None


_status_lock = threading.Lock()



# =========================================================
# SET STATUS
# =========================================================


def set_status(
    status: str
):

    """
    Set the current NEXUS operation.

    Example:

        set_status("Searching memory")

        set_status("Thinking")

        set_status("Opening Spotify")
    """


    global _current_status


    with _status_lock:

        _current_status = status





# =========================================================
# GET STATUS
# =========================================================


def get_status():

    """
    Get current NEXUS operation.

    Returns:

        "Searching memory"

        "Thinking"

        None
    """


    with _status_lock:

        return _current_status





# =========================================================
# CLEAR STATUS
# =========================================================


def clear_status():

    """
    Remove current operation.

    This tells display.py
    that the animation should disappear.
    """


    global _current_status


    with _status_lock:

        _current_status = None





# =========================================================
# CHECK STATUS
# =========================================================


def is_active():

    """
    Check whether NEXUS is currently performing a task.

    Returns:

        True  -> animation should be visible

        False -> animation should disappear
    """


    with _status_lock:

        return _current_status is not None
