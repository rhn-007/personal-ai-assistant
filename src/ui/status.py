"""
NEXUS Status Manager

Central communication bridge between:
- Assistant modules
- Tools
- Display system
- Animation system

This file only stores the current NEXUS activity.

It does NOT:
- print anything
- create animations
- control the terminal
"""


# =========================================================
# GLOBAL STATUS
# =========================================================

_current_status = None



# =========================================================
# SET STATUS
# =========================================================

def set_status(
    message: str
):
    """
    Updates the current NEXUS activity.

    Example:

    set_status("Searching memory")

    Animation displays:

    [NEXUS] ○──○──◉ Searching memory...
    """

    global _current_status


    if not message:

        _current_status = None

        return


    _current_status = message



# =========================================================
# GET STATUS
# =========================================================

def get_status():
    """
    Returns the current NEXUS activity.

    Example:

    "Searching memory"
    """

    return _current_status



# =========================================================
# CLEAR STATUS
# =========================================================

def clear_status():
    """
    Removes the current activity.

    Used when NEXUS finishes processing.
    """

    global _current_status


    _current_status = None



# =========================================================
# CHECK STATUS
# =========================================================

def is_active():
    """
    Returns True if NEXUS currently has an active task.
    """

    return _current_status is not None
