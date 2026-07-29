"""
NEXUS Status Manager

Thread-safe temporary operation states.

Controls:
- Current assistant state
- Status timing
- Automatic timeout clearing
"""


import threading
import time



_current_status = None

_status_start_time = None

_status_lock = threading.RLock()



# =====================================================
# SET STATUS
# =====================================================

def set_status(status: str):

    global _current_status
    global _status_start_time


    if not status:

        return


    status = str(status).strip()


    if not status:

        return



    with _status_lock:


        # Do not restart timer for same status

        if _current_status == status:

            return


        _current_status = status

        _status_start_time = time.monotonic()



# =====================================================
# GET STATUS
# =====================================================

def get_status():

    with _status_lock:

        return _current_status



# =====================================================
# CLEAR STATUS
# =====================================================

def clear_status():

    global _current_status
    global _status_start_time


    with _status_lock:


        _current_status = None

        _status_start_time = None



# =====================================================
# STATUS ACTIVE CHECK
# =====================================================

def is_active():

    with _status_lock:

        return _current_status is not None



# =====================================================
# STATUS AGE
# =====================================================

def get_status_age():

    with _status_lock:


        if _status_start_time is None:

            return 0


        return max(

            0,

            time.monotonic()
            -
            _status_start_time

        )



# =====================================================
# AUTOMATIC TIMEOUT
# =====================================================

def auto_clear_timeout(
    seconds=120
):

    global _current_status
    global _status_start_time


    with _status_lock:


        if (

            _current_status

            and

            _status_start_time

            and

            (
                time.monotonic()
                -
                _status_start_time
            )
            > seconds

        ):


            _current_status = None

            _status_start_time = None


            return True



    return False
