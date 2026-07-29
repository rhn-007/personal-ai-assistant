"""
NEXUS Display Manager

Universal pulse animation system.
Handles terminal status display safely.
"""

import sys
import threading
import time

from src.ui.status import (
    get_status,
    auto_clear_timeout
    register_clear_callback
)


class NexusDisplay:


    def __init__(self):

        self.running = False

        self.thread = None

        self.current_line = False

        self.lock = threading.RLock()

        
        register_clear_callback(
            self.clear_now
        )


    def clear_now(self):

        self._clear_line()
    
        sys.stderr.write("\n")
    
        sys.stderr.flush()

    
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
    # UNIVERSAL PULSE
    # =====================================================


    def _frames(self):

        return [

            "◉──○──○",

            "○──◉──○",

            "○──○──◉",

            "○──◉──○"

        ]



    # =====================================================
    # CLEAR TERMINAL LINE
    # =====================================================


    def _clear_line(self):

        if not self.current_line:

            return


        sys.stderr.write(

            "\r" + (" " * 120) + "\r"

        )

        sys.stderr.flush()


        self.current_line = False



    # =====================================================
    # WRITE STATUS
    # =====================================================


    def _write(self, frame, status):

        sys.stderr.write(

            f"\r[NEXUS] {frame} {status}..."

        )

        sys.stderr.flush()


        self.current_line = True



    # =====================================================
    # ANIMATION LOOP
    # =====================================================


    def _loop(self):


        index = 0

        last_status = None


        while self.running:


            try:


                auto_clear_timeout()


                status = get_status()



                if not status:


                    self._clear_line()


                    index = 0

                    last_status = None


                    time.sleep(0.1)

                    continue



                if status != last_status:


                    self._clear_line()


                    index = 0



                frames = self._frames()



                frame = frames[

                    index % len(frames)

                ]



                self._write(

                    frame,

                    status

                )



                index += 1


                last_status = status



                time.sleep(0.35)



            except Exception:


                self._clear_line()

                time.sleep(0.2)



    # =====================================================
    # STOP
    # =====================================================



    def clear_now(self):

        self._clear_line()
    
        sys.stderr.write("\n")
        sys.stderr.flush()
    
    def stop(self):


        with self.lock:


            self.running = False



        if self.thread:


            self.thread.join(

                timeout=1

            )



        self._clear_line()


        # IMPORTANT:
        # move cursor to next line

        sys.stderr.write("\n")

        sys.stderr.flush()


        self.thread = None


