"""
NEXUS Animation System

Handles all terminal animations and status displays.
"""

import threading
import time
import sys


class NexusAnimation:
    """
    Controls NEXUS terminal animations.
    """

    def __init__(self):

        self.stop_event = threading.Event()

        self.thread = None

        self.current_message = "Processing"


    # =====================================================
    # ANIMATION FRAMES
    # =====================================================

    def _get_frames(self):

        return [

            "○──○──◉",

            "○──◉──○",

            "◉──○──○",

            "○──◉──○"

        ]


    # =====================================================
    # ANIMATION LOOP
    # =====================================================

    def _animate(self):

        frames = self._get_frames()

        index = 0


        while not self.stop_event.is_set():

            frame = frames[index]


            sys.stdout.write(

                f"\r[NEXUS] {frame} {self.current_message}..."

            )


            sys.stdout.flush()


            index = (

                index + 1

            ) % len(frames)


            time.sleep(0.25)


        # Clear animation line

        sys.stdout.write(

            "\r" + " " * 80 + "\r"

        )

        sys.stdout.flush()



    # =====================================================
    # START ANIMATION
    # =====================================================

    def start(
        self,
        message="Processing"
    ):

        self.current_message = message


        self.stop_event.clear()


        self.thread = threading.Thread(

            target=self._animate,

            daemon=True

        )


        self.thread.start()



    # =====================================================
    # CHANGE MESSAGE
    # =====================================================

    def update(
        self,
        message
    ):

        self.current_message = message



    # =====================================================
    # STOP ANIMATION
    # =====================================================

    def stop(self):

        self.stop_event.set()


        if self.thread:

            self.thread.join()


        self.thread = None



# =========================================================
# GLOBAL INSTANCE
# =========================================================

nexus_animation = NexusAnimation()
