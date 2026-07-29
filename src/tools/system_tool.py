import os
import subprocess
import re

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class SystemTool:


    def __init__(self):

        self.name = "system"

        logger.info(
            "SystemTool initialized"
        )



    def can_handle(self, query):

        if not query:
            return False


        text = query.lower()


        return any(
            cmd in text
            for cmd in [
                "open",
                "launch",
                "start"
            ]
        )



    def clean_query(self, query):

        q = query.lower().strip()


        q = re.sub(
            r"\b(open|launch|start)\b",
            "",
            q
        )


        return q.strip()



    def open_target(self, query):

        if not query:

            return (
                "No application specified."
            )


        q = self.clean_query(query)



        apps = {


            "notepad":
                "notepad.exe",


            "calculator":
                "calc.exe",


            "calc":
                "calc.exe",


            "paint":
                "mspaint.exe",



            "spotify":

                [

                    r"%APPDATA%\Spotify\Spotify.exe",

                    r"%LOCALAPPDATA%\Spotify\Spotify.exe"

                ],



            "whatsapp":

                [

                    r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"

                ]

        }



        if q in apps:


            try:


                paths = apps[q]



                if isinstance(
                    paths,
                    list
                ):


                    for path in paths:


                        path = os.path.expandvars(
                            path
                        )


                        if os.path.exists(path):


                            subprocess.Popen(
                                [path]
                            )


                            logger.info(
                                f"Opened {q}"
                            )


                            return (
                                f"Opened {q}."
                            )



                    # URI fallback

                    if q == "spotify":

                        os.startfile(
                            "spotify:"
                        )

                        return (
                            "Opened spotify."
                        )



                    if q == "whatsapp":

                        os.startfile(
                            "whatsapp:"
                        )

                        return (
                            "Opened whatsapp."
                        )



                    return (
                        f"{q} application not found."
                    )



                subprocess.Popen(
                    [paths]
                )


                return (
                    f"Opened {q}."
                )



            except Exception as e:


                logger.error(
                    f"Failed opening {q}: {e}"
                )


                return (
                    f"Could not open {q}: {e}"
                )




        folders = {


            "downloads":
                os.path.join(
                    os.path.expanduser("~"),
                    "Downloads"
                ),


            "documents":
                os.path.join(
                    os.path.expanduser("~"),
                    "Documents"
                ),


            "desktop":
                os.path.join(
                    os.path.expanduser("~"),
                    "Desktop"
                )

        }



        if q in folders:


            try:


                os.startfile(
                    folders[q]
                )


                return (
                    f"Opened {q}."
                )


            except Exception as e:


                return (
                    f"Could not open {q}: {e}"
                )



        return (
            f"I don't know how to open '{q}' yet."
        )



    def execute_action(
        self,
        action,
        query
    ):


        if action == "open":

            return self.open_target(
                query
            )


        return (
            f"Unknown system action: {action}"
        )



    def execute(self, query):

        return self.open_target(
            query
        )
