"""
NEXUS Display Manager

Stable Windows terminal animation.
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

        self.current_line = False



    def start(self):

        if self.running:
            return


        self.running = True


        self.thread = threading.Thread(

            target=self._loop,

            daemon=True

        )


        self.thread.start()



    def _frames(self,status):

        status=status.lower()


        if "memory" in status:

            return [

                "◉──○──○",

                "○──◉──○",

                "○──○──◉"

            ]


        if "browser" in status:

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


        if "thinking" in status:

            return [

                "◉",

                "◉.",

                "◉..",

                "◉..."

            ]


        return [

            "○──○──◉",

            "○──◉──○",

            "◉──○──○"

        ]



    def _clear_line(self):


        if self.current_line:

            sys.stderr.write(

                "\r" + (" "*100) + "\r"

            )

            sys.stderr.flush()


            self.current_line=False



    def _loop(self):


        index=0


        last=None


        while self.running:


            auto_clear_timeout()


            status=get_status()



            if not status:

                self._clear_line()

                index=0

                last=None

                time.sleep(0.1)

                continue



            if status != last:

                self._clear_line()

                index=0



            frame=self._frames(status)[

                index %
                len(self._frames(status))

            ]



            sys.stderr.write(

                f"\r[NEXUS] {frame} {status}..."

            )

            sys.stderr.flush()


            self.current_line=True


            last=status


            index+=1


            time.sleep(0.3)



    def stop(self):


        self.running=False


        if self.thread:

            self.thread.join(
                timeout=1
            )


        self._clear_line()


        self.thread=None
