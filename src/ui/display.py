"""
NEXUS Display System

Temporary terminal HUD.

The animation is NOT a log.
It exists only while NEXUS is performing a task.

Flow:

status.py
    ↓
display.py
    ↓
temporary animation
    ↓
clear when finished
"""


import sys
import threading
import time


from src.ui.status import get_status



class NexusDisplay:


    def __init__(self):

        self.running = False

        self.thread = None

        self.current_status = None


        self.frames = [

            "○──○──◉",

            "○──◉──○",

            "◉──○──○",

            "○──◉──○"

        ]


        self.frame_index = 0



    # =====================================================
    # START DISPLAY
    # =====================================================


    def start(self):

        if self.running:

            return


        self.running = True


        self.thread = threading.Thread(

            target=self._display_loop,

            daemon=True

        )


        self.thread.start()



    # =====================================================
    # DISPLAY LOOP
    # =====================================================


    def _display_loop(self):


        while self.running:


            status = get_status()



            # -------------------------------------------------
            # STATUS ACTIVE
            # -------------------------------------------------

            if status:


                if status != self.current_status:


                    self.clear()


                    self.current_status = status



                self.draw(status)



            # -------------------------------------------------
            # NO STATUS
            # -------------------------------------------------

            else:


                if self.current_status:


                    self.clear()


                    self.current_status = None



            time.sleep(0.25)



    # =====================================================
    # DRAW ANIMATION
    # =====================================================


    def draw(
        self,
        status
    ):


        frame = self.frames[

            self.frame_index

        ]


        sys.stdout.write(

            f"\r[NEXUS] {frame} {status}..."

        )


        sys.stdout.flush()



        self.frame_index = (

            self.frame_index + 1

        ) % len(self.frames)



    # =====================================================
    # CLEAR CURRENT ANIMATION
    # =====================================================


    def clear(self):


        sys.stdout.write(

            "\r" + " " * 80 + "\r"

        )


        sys.stdout.flush()



    # =====================================================
    # STOP
    # =====================================================


    def stop(self):


        self.running = False


        self.clear()


        if self.thread:


            self.thread.join(
                timeout=1
            )
