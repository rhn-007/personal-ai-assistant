"""
NEXUS Display Controller

Handles the live status animation display.
"""


import threading
import time

from src.ui.status import get_status



class NexusDisplay:


    def __init__(self):

        self.running = False

        self.thread = None



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

        last_status = None


        while self.running:


            status = get_status()


            if status and status != last_status:


                print(

                    f"\n[NEXUS] ○──◉──○ {status}..."

                )


                last_status = status



            time.sleep(
                0.1
            )



    # =====================================================
    # STOP DISPLAY
    # =====================================================

    def stop(self):

        self.running = False


        if self.thread:

            self.thread.join(

                timeout=1

            )


        self.thread = None
