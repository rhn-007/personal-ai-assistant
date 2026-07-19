import os
import subprocess

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class SystemTool:

    def __init__(self):

        self.name = "system"

        logger.info("SystemTool initialized")

    def open_target(self, query: str):

        if not query:
            return "No application or folder specified."

        q = query.lower().strip()

        # Remove common command words
        for word in ["open", "launch", "start"]:
            q = q.replace(word, "").strip()

        # =====================================================
        # APPLICATIONS
        # =====================================================

        apps = {

            "notepad": "notepad.exe",

            "calculator": "calc.exe",

            "calc": "calc.exe",

            "paint": "mspaint.exe",

            # OPERA
            "opera": [
                r"C:\Users\%USERNAME%\AppData\Local\Programs\Opera\opera.exe",
                r"C:\Program Files\Opera\launcher.exe",
                r"C:\Program Files (x86)\Opera\launcher.exe"
            ],

            # SPOTIFY
            "spotify": [

                r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",

                r"C:\Users\%USERNAME%\AppData\Local\Spotify\Spotify.exe",

                r"C:\Program Files\Spotify\Spotify.exe",

                r"C:\Program Files (x86)\Spotify\Spotify.exe",

                r"C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Spotify.lnk"

            ]

        }

        if q in apps:

            try:

                app_paths = apps[q]

                # =================================================
                # MULTIPLE POSSIBLE PATHS
                # =================================================

                if isinstance(app_paths, list):

                    for path in app_paths:

                        # Expand %USERNAME% and environment variables
                        path = os.path.expandvars(path)

                        if os.path.exists(path):

                            if path.lower().endswith(".lnk"):

                                os.startfile(path)

                            else:

                                subprocess.Popen([path])

                            logger.info(
                                f"Opened {q}: {path}"
                            )

                            return f"Opened {q}."

                    # =================================================
                    # SPOTIFY URI FALLBACK
                    # =================================================

                    if q == "spotify":

                        try:

                            os.startfile("spotify:")

                            logger.info(
                                "Opened Spotify using spotify URI"
                            )

                            return "Opened spotify."

                        except Exception as e:

                            logger.error(
                                f"Spotify URI failed: {e}"
                            )

                    return (
                        f"Could not find the installed "
                        f"{q} application."
                    )

                # =================================================
                # NORMAL EXECUTABLE
                # =================================================

                subprocess.Popen([app_paths])

                logger.info(
                    f"Opened application: {q}"
                )

                return f"Opened {q}."

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

                os.startfile(folders[q])

                logger.info(
                    f"Opened folder: {q}"
                )

                return f"Opened {q}."

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

            return self.open_target(query)

        return (
            f"Unknown system action: "
            f"{action}"
        )

    def execute(self, query: str):

        return self.open_target(query)
