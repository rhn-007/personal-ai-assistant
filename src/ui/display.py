"""
NEXUS Display Manager

Handles temporary animated status display.

Animation is temporary and disappears
when the current task is completed.

The animation does not remain frozen.
"""


import threading
import time
import sys


from src.ui.status import get_status




class NexusDisplay:


    def __init__(self):

        self.running = False

        self.thread = None

        self.current_line = False

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
    # CLEAR DISPLAY LINE
    # =====================================================

    def _clear_line(self):

        """
        Completely removes the animation line.
        """


        if self.current_line:

            sys.stderr.write(

                "\r" + (" " * 120) + "\r"

            )

            sys.stderr.flush()


            self.current_line = False



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



            # -------------------------------------------------
            # No active task
            # -------------------------------------------------

            if not status:


                self._clear_line()

                self.last_status = None


                time.sleep(0.1)

                continue




            # -------------------------------------------------
            # Status changed
            # -------------------------------------------------

            if status != self.last_status:


                self._clear_line()


                index = 0



            frame = frames[index % len(frames)]


            sys.stderr.write(

                f"\r[NEXUS] {frame} {status}..."

            )


            sys.stderr.flush()



            self.current_line = True


            self.last_status = status


            index += 1


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



        self._clear_line()



        self.thread = None
