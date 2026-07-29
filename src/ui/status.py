"""
NEXUS Status Manager

Thread-safe assistant state manager.

Features:
- Thread-safe status updates
- Status timeout protection
- Automatic stale-state recovery
"""


import threading
import time


_current_status = None

_status_start_time = None

_status_lock = threading.RLock()


DEFAULT_TIMEOUT = 120



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


        _current_status = status

        _status_start_time = time.monotonic()



# =====================================================
# GET STATUS
# =====================================================

def get_status():

    auto_clear_timeout()

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
# ACTIVE CHECK
# =====================================================

def is_active():

    auto_clear_timeout()

    with _status_lock:

        return _current_status is not None



# =====================================================
# AGE
# =====================================================

def get_status_age():

    with _status_lock:

        if _status_start_time is None:

            return 0


        return (
            time.monotonic()
            -
            _status_start_time
        )



# =====================================================
# TIMEOUT PROTECTION
# =====================================================

def auto_clear_timeout(
    seconds=DEFAULT_TIMEOUT
):

    global _current_status
    global _status_start_time


    with _status_lock:


        if not _current_status:

            return False



        if not _status_start_time:

            return False



        age = (
            time.monotonic()
            -
            _status_start_time
        )


        if age > seconds:


            _current_status = None

            _status_start_time = None


            return True



    return False
