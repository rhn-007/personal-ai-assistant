"""
NEXUS Status Manager

Stores the current temporary operation state.
"""


import threading



_current_status = None

_status_changed = False

_status_lock = threading.Lock()



def set_status(status: str):

    global _current_status
    global _status_changed


    with _status_lock:

        _current_status = status

        _status_changed = True




def get_status():

    with _status_lock:

        return _current_status




def clear_status():

    global _current_status
    global _status_changed


    with _status_lock:

        _current_status = None

        _status_changed = True




def has_changed():

    global _status_changed


    with _status_lock:

        value = _status_changed

        _status_changed = False

        return value




def is_active():

    with _status_lock:

        return _current_status is not None
