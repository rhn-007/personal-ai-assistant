"""
NEXUS Display Manager

Handles animated temporary status display.

Features:

- Smooth animation
- Different animations for different tasks
- Automatic cleanup
- No freezing
- Does not interfere with logs
- Works with stderr output
"""


import threading
import time
import sys


from src.ui.status import (
    get_status,
    auto_clear_timeout
)



class NexusDisplay:


    def __init__(self):

        self.running = False

        self.thread = None

        self.last_status = None

        self.current_line = False

        self.lock = threading.Lock()



    # =====================================================
    # START DISPLAY
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
    # ANIMATION DATABASE
    # =====================================================

    def _get_animation(self, status):


        status = status.lower()



        # MEMORY

        if "memory" in status:

            return [

                "○──○──◉",

                "○──◉──○",

                "◉──○──○"

            ]



        # THINKING

        if "thinking" in status:

            return [

                "◉",

                "◉.",

                "◉..",

                "◉..."

            ]



        # BROWSER

        if (

            "browser" in status

            or "search" in status

        ):

            return [

                "🌐○──○",

                "🌐─○─○",

                "🌐──○◉"

            ]



        # SPOTIFY

        if "spotify" in status:

            return [

                "♫ ○──○",

                "♫ ─○─",

                "♫ ○──◉"

            ]



        # EMAIL

        if "email" in status:

            return [

                "✉ ○──○",

                "✉ ─○─",

                "✉ ○──◉"

            ]



        # CALENDAR

        if "calendar" in status:

            return [

                "📅 ○──○",

                "📅 ─○─",

                "📅 ○──◉"

            ]



        # TOOLS

        if "tool" in status:

            return [

                "⚙ ○──○",

                "⚙ ─○─",

                "⚙ ○──◉"

            ]



        # SYSTEM

        if (

            "opening" in status

            or "launching" in status

        ):

            return [

                "▶ ○──○",

                "▶ ─○─",

                "▶ ○──◉"

            ]



        # DEFAULT

        return [

            "○──○──◉",

            "○──◉──○",

            "◉──○──○"

        ]





    # =====================================================
    # CLEAR CURRENT LINE
    # =====================================================

    def _clear_line(self):


        if self.current_line:


            sys.stderr.write(

                "\r" + (" " * 120) + "\r"

            )


            sys.stderr.flush()


            self.current_line = False





    # =====================================================
    # MAIN LOOP
    # =====================================================

    def _loop(self):


        frame_index = 0



        while self.running:



            # Safety timeout

            auto_clear_timeout()



            status = get_status()



            # ------------------------------------------------
            # NO ACTIVE TASK
            # ------------------------------------------------

            if not status:


                self._clear_line()


                self.last_status = None


                frame_index = 0


                time.sleep(0.1)


                continue





            # ------------------------------------------------
            # STATUS CHANGED
            # ------------------------------------------------

            if status != self.last_status:


                self._clear_line()


                frame_index = 0




            animation = self._get_animation(

                status

            )



            frame = animation[

                frame_index % len(animation)

            ]



            sys.stderr.write(

                f"\r[NEXUS] {frame} {status}..."

            )


            sys.stderr.flush()



            self.current_line = True



            self.last_status = status



            frame_index += 1



            time.sleep(0.3)






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
