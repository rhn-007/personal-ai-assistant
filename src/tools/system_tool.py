import os
import subprocess

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class SystemTool:

    def __init__(self):

        self.name = "system"

        logger.info(
            "SystemTool initialized"
        )

    def open_target(self, query: str):

        if not query:

            return (
                "No application or folder specified."
            )

        q = query.lower().strip()

        # Remove common command words
        for word in [
            "open",
            "launch",
            "start"
        ]:

            q = q.replace(
                word,
                ""
            ).strip()

        # =====================================================
        # APPLICATIONS
        # =====================================================

        apps = {

            "notepad": "notepad.exe",

            "calculator": "calc.exe",

            "calc": "calc.exe",

            "paint": "mspaint.exe",

            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ],

            "google chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ],

            "spotify": [

                os.path.expandvars(
                    r"%APPDATA%\Spotify\Spotify.exe"
                ),

                os.path.expandvars(
                    r"%LOCALAPPDATA%\Spotify\Spotify.exe"
                ),

                os.path.expandvars(
                    r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Spotify.lnk"
                )

            ]

        }

        if q in apps:

            try:

                app = apps[q]

                # =================================================
                # MULTIPLE POSSIBLE PATHS
                # =================================================

                if isinstance(app, list):

                    for path in app:

                        if os.path.exists(path):

                            os.startfile(path)

                            logger.info(
                                f"Opened {q}: {path}"
                            )

                            return (
                                f"Opened {q}."
                            )

                    # Spotify URI fallback
                    if q == "spotify":

                        try:

                            os.startfile(
                                "spotify:"
                            )

                            logger.info(
                                "Opened Spotify using URI"
                            )

                            return (
                                "Opened Spotify."
                            )

                        except Exception:

                            pass

                    return (
                        f"Could not find the installed "
                        f"{q} application."
                    )

                # =================================================
                # URI
                # =================================================

                if isinstance(app, str) and app.endswith(":"):

                    os.startfile(app)

                    return (
                        f"Opened {q}."
                    )

                # =================================================
                # EXECUTABLE
                # =================================================

                subprocess.Popen(
                    [app]
                )

                logger.info(
                    f"Opened application: {q}"
                )

                return (
                    f"Opened {q}."
                )

            except Exception as e:

                logger.error(
                    f"Failed to open {q}: {e}"
                )

                return (
                    f"Could not open {q}: {e}"
                )

        # =====================================================
        # COMMON FOLDERS
        # =====================================================

        folders = {

            "downloads": os.path.join(
                os.path.expanduser("~"),
                "Downloads"
            ),

            "documents": os.path.join(
                os.path.expanduser("~"),
                "Documents"
            ),

            "desktop": os.path.join(
                os.path.expanduser("~"),
                "Desktop"
            )

        }

        if q in folders:

            try:

                os.startfile(
                    folders[q]
                )

                logger.info(
                    f"Opened folder: {q}"
                )

                return (
                    f"Opened {q}."
                )

            except Exception as e:

                logger.error(
                    f"Failed to open folder {q}: {e}"
                )

                return (
                    f"Could not open {q}: {e}"
                )

        return (
            f"I don't know how to open "
            f"'{q}' yet."
        )

    def execute_action(
        self,
        action: str,
        query: str
    ):

        if action == "open":

            return self.open_target(
                query
            )

        return (
            f"Unknown system action: "
            f"{action}"
        )

    def execute(
        self,
        query: str
    ):

        return self.open_target(
            query
        )
