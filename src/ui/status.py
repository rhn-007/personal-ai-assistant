"""
NEXUS Status Manager

Stores the current operation being performed.

Example:

set_status("Searching memory")

display.py reads:

Searching memory

clear_status()

display.py removes animation.
"""


import threading



# =========================================================
# GLOBAL STATUS
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
    Update current NEXUS activity.

    Example:
        set_status("Searching memory")
        set_status("Thinking")
    """


    global _current_status


    with _status_lock:


        _current_status = status





# =========================================================
# GET STATUS
# =========================================================


def get_status():

    """
    Returns current NEXUS activity.

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
    Remove current activity.

    This tells display.py
    to erase the animation.
    """


    global _current_status


    with _status_lock:


        _current_status = None
