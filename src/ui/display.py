"""
NEXUS Display Manager

Handles temporary animated status display.

The animation disappears automatically
when status.py clears the status.
"""


import threading
import time
import sys


from src.ui.status import get_status




class NexusDisplay:


    def __init__(self):

        self.running = False

        self.thread = None

        self.last_status = None



    # =====================================================
    # START
    # =====================================================

    def start(self):

        if self.running:

            return


        self.running = True


        self.thread = threading.Thread(

            target=self._loop,

            daemon=True

        )


        self.thread.start()



    # =====================================================
    # ANIMATION LOOP
    # =====================================================

    def _loop(self):

        frames = [

            "○──○──◉",

            "○──◉──○",

            "◉──○──○"

        ]


        index = 0



        while self.running:


            status = get_status()



            if status:


                animation = frames[index % len(frames)]


                text = (

                    f"[NEXUS] {animation} {status}..."

                )


                sys.stdout.write(

                    "\r" + text

                )


                sys.stdout.flush()



                index += 1



            else:


                if self.last_status:


                    sys.stdout.write(

                        "\r" + (" " * 80) + "\r"

                    )


                    sys.stdout.flush()



                index = 0



            self.last_status = status


            time.sleep(
                0.3
            )



    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.running = False


        if self.thread:


            self.thread.join(

                timeout=1

            )


        sys.stdout.write(

            "\r" + (" " * 80) + "\r"

        )


        sys.stdout.flush()


        self.thread = None
