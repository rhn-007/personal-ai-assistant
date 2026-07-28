"""
NEXUS Logger System

Handles application logging without interfering
with the terminal animation system.

Logs are written to:
logs/nexus.log

The terminal is kept clean for:
- User input
- NEXUS animations
- Assistant responses
"""

import logging
from pathlib import Path


# =========================================================
# LOG DIRECTORY
# =========================================================

LOG_DIR = Path("logs")

LOG_DIR.mkdir(
    exist_ok=True
)


LOG_FILE = LOG_DIR / "nexus.log"



# =========================================================
# LOGGER SETUP
# =========================================================

def setup_logger(name: str):

    logger = logging.getLogger(name)


    # Prevent duplicate handlers

    if logger.handlers:

        return logger



    logger.setLevel(
        logging.INFO
    )



    # =====================================================
    # FILE HANDLER
    # =====================================================

    file_handler = logging.FileHandler(

        LOG_FILE,

        encoding="utf-8"

    )


    file_formatter = logging.Formatter(

        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    )


    file_handler.setFormatter(

        file_formatter

    )


    logger.addHandler(

        file_handler

    )



    # =====================================================
    # OPTIONAL ERROR CONSOLE
    # =====================================================

    error_handler = logging.StreamHandler()

    error_handler.setLevel(
        logging.ERROR
    )


    error_formatter = logging.Formatter(

        "ERROR: %(message)s"

    )


    error_handler.setFormatter(

        error_formatter

    )


    logger.addHandler(

        error_handler

    )



    # Prevent logs propagating
    # to root logger

    logger.propagate = False



    return logger
