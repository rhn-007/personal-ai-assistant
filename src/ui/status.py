"""
NEXUS Status Manager

Thread-safe temporary operation states.
"""


import threading
import time



_current_status = None

_status_start_time = None

_status_lock = threading.RLock()



def set_status(status: str):

    global _current_status
    global _status_start_time


    if not status:
        return


    with _status_lock:

        _current_status = status

        _status_start_time = time.time()



def get_status():

    with _status_lock:

        return _current_status



def clear_status():

    global _current_status
    global _status_start_time


    with _status_lock:

        _current_status = None

        _status_start_time = None



def is_active():

    with _status_lock:

        return _current_status is not None



def get_status_age():

    with _status_lock:

        if _status_start_time is None:

            return 0


        return time.time() - _status_start_time



def auto_clear_timeout(seconds=120):

    global _current_status
    global _status_start_time


    with _status_lock:


        if (

            _current_status

            and _status_start_time

            and (
                time.time()
                -
                _status_start_time
            )
            > seconds

        ):

            _current_status = None

            _status_start_time = None

            return True



    return False
