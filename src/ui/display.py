"""
NEXUS Display Manager

Stable terminal animation manager.
Handles temporary status animations safely.
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


    def _frames(self, status):

        status = status.lower()

        if "memory" in status:
            return [
                "◉──○──○",
                "○──◉──○",
                "○──○──◉"
            ]

        if "running tools" in status:
            return [
                "○──○──◉",
                "○──◉──○",
                "◉──○──○"
            ]

        if "planning" in status:
            return [
                "○──◉──○",
                "◉──○──○",
                "○──○──◉"
            ]

        if "thinking" in status:

            return [
                "◉",
                "◉.",
                "◉..",
                "◉..."
            ]

        if "search" in status:

            return [
                "○──○──◉",
                "○──◉──○",
                "◉──○──○"
            ]

        return [
            "○──○──◉",
            "○──◉──○",
            "◉──○──○"
        ]


    def _clear_line(self):

        if not self.current_line:
            return

        sys.stderr.write(
            "\r" + (" " * 120) + "\r"
        )

        sys.stderr.flush()

        self.current_line = False


    def _write(self, text):

        sys.stderr.write(
            "\r[NEXUS] " + text
        )

        sys.stderr.flush()

        self.current_line = True


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


                frames = self._frames(status)

                frame = frames[
                    index % len(frames)
                ]


                self._write(
                    f"{frame} {status}..."
                )


                index += 1

                last_status = status


                time.sleep(0.35)


            except Exception:

                self._clear_line()

                time.sleep(0.2)



    def stop(self):

        with self.lock:

            self.running = False


        if self.thread:

            self.thread.join(
                timeout=1
            )


        self._clear_line()

        self.thread = None
