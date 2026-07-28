"""
NEXUS Display Manager

Windows-compatible animated status display.

Features:
- Separate animation thread
- Does not freeze
- Handles status changes
- Clears animation correctly
- Prevents terminal corruption
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
    # ANIMATION TYPES
    # =====================================================

    def _get_frames(self, status):

        status = status.lower()



        if "memory" in status:

            return [

                "◉──○──○",

                "○──◉──○",

                "○──○──◉"

            ]



        if "thinking" in status:

            return [

                "◉",

                "◉.",

                "◉..",

                "◉..."

            ]



        if "browser" in status or "search" in status:

            return [

                "🌐 ○──○",

                "🌐 ─○─",

                "🌐 ○──◉"

            ]



        if "spotify" in status:

            return [

                "♫ ○──○",

                "♫ ─○─",

                "♫ ○──◉"

            ]



        if "email" in status:

            return [

                "✉ ○──○",

                "✉ ─○─",

                "✉ ○──◉"

            ]



        if "calendar" in status:

            return [

                "📅 ○──○",

                "📅 ─○─",

                "📅 ○──◉"

            ]



        if "tool" in status:

            return [

                "⚙ ○──○",

                "⚙ ─○─",

                "⚙ ○──◉"

            ]



        return [

            "○──○──◉",

            "○──◉──○",

            "◉──○──○"

        ]





    # =====================================================
    # CLEAR LINE
    # =====================================================

    def _clear_line(self):

        if self.current_line:

            sys.stdout.write(

                "\r" + (" " * 120) + "\r"

            )

            sys.stdout.flush()


            self.current_line = False





    # =====================================================
    # DISPLAY LOOP
    # =====================================================

    def _loop(self):


        frame_index = 0



        while self.running:


            # Prevent infinite animation

            auto_clear_timeout()



            status = get_status()



            # No task

            if not status:


                self._clear_line()


                self.last_status = None


                frame_index = 0


                time.sleep(0.1)

                continue




            # New status

            if status != self.last_status:


                self._clear_line()


                frame_index = 0



            frames = self._get_frames(status)



            frame = frames[

                frame_index % len(frames)

            ]



            # Write animation

            sys.stdout.write(

                f"\r[NEXUS] {frame} {status}..."

            )


            sys.stdout.flush()



            self.current_line = True


            self.last_status = status


            frame_index += 1



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
