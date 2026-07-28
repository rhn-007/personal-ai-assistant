"""
NEXUS Status Manager

Controls temporary visual states.

The display system reads these states
and shows the correct animation.

Example:

set_status("Searching memory")

Display:

[NEXUS] ○──◉──○ Searching memory...


set_status("Opening browser")

Display:

[NEXUS] ◉──○──○ Opening browser...


clear_status()

Removes animation.
"""


import threading
import time



# =========================================================
# GLOBAL STATUS STORAGE
# =========================================================


_current_status = None


_status_start_time = None


_status_lock = threading.Lock()



# =========================================================
# STATUS SET
# =========================================================


def set_status(status: str):

    """
    Updates current NEXUS operation.

    Example:

    set_status("Thinking")

    set_status("Opening Spotify")

    set_status("Searching memory")
    """


    global _current_status
    global _status_start_time


    if not status:

        return



    with _status_lock:


        _current_status = status


        _status_start_time = time.time()




# =========================================================
# GET STATUS
# =========================================================


def get_status():

    """
    Returns current active status.

    Returns:

    str
        Current task

    None
        No active task
    """


    with _status_lock:

        return _current_status





# =========================================================
# CLEAR STATUS
# =========================================================


def clear_status():

    """
    Clears current animation.

    Called when:

    - Tool finishes
    - Memory search finishes
    - AI response completes
    """


    global _current_status
    global _status_start_time


    with _status_lock:


        _current_status = None


        _status_start_time = None





# =========================================================
# ACTIVE CHECK
# =========================================================


def is_active():

    """
    Checks if NEXUS is performing a task.
    """


    with _status_lock:

        return _current_status is not None





# =========================================================
# STATUS AGE
# =========================================================


def get_status_age():

    """
    Returns how long current task
    has been running.
    """


    with _status_lock:


        if not _status_start_time:

            return 0



        return time.time() - _status_start_time





# =========================================================
# FORCE TIMEOUT
# =========================================================


def auto_clear_timeout(seconds=120):

    """
    Safety feature.

    Prevents animations freezing forever
    if a tool crashes.
    """


    global _current_status


    with _status_lock:


        if (

            _current_status

            and get_status_age() > seconds

        ):


            _current_status = None

            return True



    return False
