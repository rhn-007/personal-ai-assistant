import os
import subprocess
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SystemTool:
    """
    Local Windows system control tool.

    Currently supports:
    - Opening common applications
    - Opening common folders
    """

    def __init__(self):
        self.name = "system"
        logger.info("SystemTool initialized")

    def open_target(self, query: str):
        """
        Open an approved application or folder based on the user's request.
        """

        if not query:
            return "No application or folder specified."

        q = query.lower().strip()

        # Remove common command words
        for word in ["open", "launch", "start"]:
            q = q.replace(word, "").strip()

        # -----------------------------
        # APPLICATIONS
        # -----------------------------

        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "paint": "mspaint.exe",
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "spotify": "spotify:",
        }

        if q in apps:
            try:
                if apps[q].endswith(":"):
                    os.startfile(apps[q])
                else:
                    subprocess.Popen(apps[q])

                return f"Opened {q}."

            except Exception as e:
                logger.error(f"Failed to open {q}: {e}")
                return f"Could not open {q}: {e}"

        # -----------------------------
        # COMMON FOLDERS
        # -----------------------------

        folders = {
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        }

        if q in folders:
            try:
                os.startfile(folders[q])
                return f"Opened {q}."

            except Exception as e:
                logger.error(f"Failed to open folder {q}: {e}")
                return f"Could not open {q}: {e}"

        return f"I don't know how to open '{q}' yet."

    def execute_action(self, action: str, query: str):
        """
        Execute a system action.
        """

        if action == "open":
            return self.open_target(query)

        return f"Unknown system action: {action}"

    def execute(self, query: str):
        """
        Compatibility method for the ToolManager.
        """

        return self.open_target(query)
