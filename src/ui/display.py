"""
NEXUS Display Manager

Stable terminal animation manager.

Features:
- Single universal pulse animation
- Thread-safe rendering
- Immediate clearing
- Prevents frozen status lines
- Does not interfere with user input
"""

import sys
import threading
import time

from src.ui.status import get_status, auto_clear_timeout


class NexusDisplay:

    def __init__(self):

        self.running = False
        self.thread = None

        self.current_line = False

        self.lock = threading.RLock()


    # =====================================================
    # START DISPLAY THREAD
    # =====================================================

    def start(self):

        with self.lock:

            if self.running:
                return

            self.running = True

            self.thread = threading.Thread(
                target=self._loop,
                daemon=True
            )

            self.thread.start()



    # =====================================================
    # UNIVERSAL PULSE ANIMATION
    # =====================================================

    def _frames(self):

        return [

            "◉",

            "◉.",

            "◉..",

            "◉...",

            "◉..",

            "◉."

        ]



    # =====================================================
    # WRITE STATUS LINE
    # =====================================================

    def _write(self, text):

        with self.lock:

            sys.stderr.write(
                "\r[NEXUS] " + text
            )

            sys.stderr.flush()

            self.current_line = True



    # =====================================================
    # CLEAR CURRENT LINE
    # =====================================================

    def clear_now(self):

        with self.lock:

            if not self.current_line:
                return


            sys.stderr.write(
                "\r" + (" " * 120) + "\r"
            )

            sys.stderr.flush()


            self.current_line = False



    # =====================================================
    # DISPLAY LOOP
    # =====================================================

    def _loop(self):

        index = 0


        while self.running:

            try:

                auto_clear_timeout()


                status = get_status()


                # No active status

                if not status:

                    self.clear_now()

                    index = 0

                    time.sleep(
                        0.05
                    )

                    continue



                frames = self._frames()


                frame = frames[
                    index % len(frames)
                ]


                self._write(

                    f"{frame} {status}..."

                )


                index += 1


                time.sleep(
                    0.35
                )



            except Exception as e:


                self.clear_now()


                time.sleep(
                    0.1
                )



    # =====================================================
    # STOP DISPLAY
    # =====================================================

    def stop(self):

        with self.lock:

            self.running = False



        if self.thread:

            self.thread.join(
                timeout=1
            )


        self.clear_now()


        self.thread = None
