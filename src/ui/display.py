"""
NEXUS Display Manager

Stable Windows terminal animation.
"""

import threading
import time
import sys

from src.ui.status import get_status, auto_clear_timeout


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

    def _frames(self, status):

        status = status.lower()

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

        sys.stdout.write("\r" + (" " * 120) + "\r")
        sys.stdout.flush()

        self.current_line = False

    def _loop(self):

        index = 0
        last_status = None

        while self.running:

            auto_clear_timeout()

            status = get_status()

            if not self.running:
                break

            if not status:

                if self.current_line:
                    self._clear_line()

                last_status = None
                index = 0

                time.sleep(0.05)
                continue

            if status != last_status:

                self._clear_line()

                last_status = status
                index = 0

            frames = self._frames(status)

            frame = frames[index % len(frames)]

            sys.stdout.write(
                f"\r[NEXUS] {frame} {status}..."
            )

            sys.stdout.flush()

            self.current_line = True

            index += 1

            for _ in range(6):

                if not self.running:
                    break

                if get_status() != status:
                    break

                time.sleep(0.05)

        self._clear_line()

    def stop(self):

        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)

        self._clear_line()

        self.thread = None
