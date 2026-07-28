"""
NEXUS Display System

Handles:
- Processing animations
- Status messages
- Future UI elements

Keeps display logic separate from:
- main.py
- assistant.py
"""


import sys
import threading
import time


# =========================================================
# NEXUS PROCESSING ANIMATION
# =========================================================

class NexusDisplay:
    """
    Controls NEXUS terminal display.
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


        self.current_index = 0



    # =====================================================
    # START PROCESSING DISPLAY
    # =====================================================

    def start_processing(
        self,
        message="Processing..."
    ):

        """
        Starts the NEXUS loading animation.

        Example:

        [NEXUS] ○──○──◉ Processing...
        """

        self.stop_event.clear()


        self.animation_thread = threading.Thread(

            target=self._animate,

            args=(message,),

            daemon=True

        )


        self.animation_thread.start()



    # =====================================================
    # ANIMATION LOOP
    # =====================================================

    def _animate(
        self,
        message
    ):


        while not self.stop_event.is_set():


            frame = self.frames[
                self.current_index
            ]


            sys.stdout.write(

                f"\r[NEXUS] {frame} {message}"

            )


            sys.stdout.flush()


            self.current_index = (

                self.current_index + 1

            ) % len(self.frames)



            time.sleep(
                0.25
            )



    # =====================================================
    # STOP PROCESSING DISPLAY
    # =====================================================

    def stop_processing(self):

        """
        Removes animation when response is ready.
        """


        self.stop_event.set()


        if self.animation_thread:

            self.animation_thread.join()



        # Clear animation line

        sys.stdout.write(

            "\r" + " " * 60 + "\r"

        )


        sys.stdout.flush()



    # =====================================================
    # STATIC STATUS MESSAGE
    # =====================================================

    @staticmethod
    def status(
        message
    ):

        """
        Display normal NEXUS status messages.

        Example:

        [NEXUS] Searching memory...
        """

        print(

            f"[NEXUS] {message}"

        )
