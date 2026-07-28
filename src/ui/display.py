"""
NEXUS Display Manager

Handles temporary animated status display.

Animation is written to stderr so it does not
conflict with application logs.
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
    # DISPLAY LOOP
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


                frame = frames[index % len(frames)]


                message = (

                    f"\r[NEXUS] {frame} {status}..."

                )


                sys.stderr.write(message)

                sys.stderr.flush()


                index += 1



            elif self.last_status:


                # erase animation line

                sys.stderr.write(

                    "\r" + (" " * 100) + "\r"

                )

                sys.stderr.flush()


                index = 0



            self.last_status = status


            time.sleep(0.25)



    # =====================================================
    # STOP
    # =====================================================

    def stop(self):


        self.running = False


        if self.thread:

            self.thread.join(

                timeout=1

            )


        sys.stderr.write(

            "\r" + (" " * 100) + "\r"

        )

        sys.stderr.flush()


        self.thread = None
