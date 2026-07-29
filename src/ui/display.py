"""
NEXUS Display Manager

Single-owner terminal animation system.

Responsibilities:
- Render assistant status animation
- Read status.py state
- Avoid terminal conflicts
- Handle clean startup/shutdown
"""

import sys
import threading
import time

from src.ui.status import (
    get_status,
    auto_clear_timeout
)


class NexusDisplay:

    def __init__(self):

        self.running = False

        self.thread = None

        self.lock = threading.RLock()

        self.line_visible = False



    # =====================================================
    # START DISPLAY ENGINE
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
    # ANIMATION FRAMES
    # =====================================================

    def _frames(self):

        return [

            "○──○──●",

            "○──●──○",

            "●──○──○",

            "○──●──○"

        ]



    # =====================================================
    # WRITE LINE
    # =====================================================

    def _render(self, text):

        with self.lock:

            sys.stdout.write(

                "\r[NEXUS] " + text

            )

            sys.stdout.flush()


            self.line_visible = True



    # =====================================================
    # CLEAR LINE
    # =====================================================

    def clear_now(self):

        with self.lock:

            if not self.line_visible:

                return


            sys.stdout.write(

                "\r" + (" " * 120) + "\r"

            )


            sys.stdout.flush()


            self.line_visible = False



    # =====================================================
    # DISPLAY LOOP
    # =====================================================

    def _loop(self):

        frames = self._frames()

        index = 0


        while self.running:


            try:

                auto_clear_timeout()


                status = get_status()



                if not status:

                    self.clear_now()

                    index = 0


                    time.sleep(
                        0.05
                    )

                    continue



                frame = frames[

                    index % len(frames)

                ]


                self._render(

                    f"{frame} {status}..."

                )


                index += 1


                time.sleep(
                    0.30
                )



            except Exception:


                self.clear_now()


                time.sleep(
                    0.1
                )



    # =====================================================
    # STOP
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
