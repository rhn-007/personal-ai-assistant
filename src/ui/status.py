"""
NEXUS Status Manager

Stores and manages the current state of NEXUS.

This file does NOT:
- display animations
- print messages
- control the terminal

It only keeps track of what NEXUS is currently doing.
"""


# =========================================================
# GLOBAL STATUS
# =========================================================

_current_status = "Idle"



# =========================================================
# SET STATUS
# =========================================================

def set_status(
    message: str
):
    """
    Update the current NEXUS status.

    Example:

    set_status("Searching memory")

    """

    global _current_status


    if not message:

        _current_status = "Idle"

        return


    _current_status = message



# =========================================================
# GET STATUS
# =========================================================

def get_status():
    """
    Returns the current NEXUS status.

    Example:

    "Searching memory"
    """

    return _current_status



# =========================================================
# RESET STATUS
# =========================================================

def reset_status():
    """
    Resets NEXUS status back to idle.
    """

    global _current_status


    _current_status = "Idle"
