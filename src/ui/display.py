"""
NEXUS Display System

Controls:
- Terminal animation
- Status monitoring
- Automatic start/stop behaviour

This file connects:
status.py  →  animation display
"""


import sys
import threading
import time


from src.ui.status import (
    get_status,
    is_active
)



class NexusDisplay:
    """
    Main NEXUS terminal display controller.
    """


    def __init__(self):

        self.stop_event = threading.Event()

        self.animation_thread = None


        self.frames = [

            "○──○──◉",

            "○──◉──○",

            "◉──○──○",

            "○──◉──○"

        ]


        self.frame_index = 0



    # =====================================================
    # START DISPLAY MONITOR
    # =====================================================

    def start(self):
        """
        Starts monitoring the NEXUS status.

        Animation only appears when
        status.py contains an active status.
        """


        self.stop_event.clear()


        self.animation_thread = threading.Thread(

            target=self._monitor_status,

            daemon=True

        )


        self.animation_thread.start()



    # =====================================================
    # STATUS MONITOR
    # =====================================================

    def _monitor_status(self):


        while not self.stop_event.is_set():


            if is_active():

                self._draw_animation()


            time.sleep(
                0.25
            )



    # =====================================================
    # DRAW ANIMATION
    # =====================================================

    def _draw_animation(self):


        status = get_status()


        if not status:

            return


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
    # CLEAR DISPLAY
    # =====================================================

    def clear(self):
        """
        Removes animation from terminal.
        """


        sys.stdout.write(

            "\r" + " " * 80 + "\r"

        )


        sys.stdout.flush()



    # =====================================================
    # STOP DISPLAY
    # =====================================================

    def stop(self):


        self.stop_event.set()


        if self.animation_thread:

            self.animation_thread.join()



        self.clear()
