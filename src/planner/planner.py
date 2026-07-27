"""
Planner - Decides whether a user request requires a tool
"""

import re

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class Planner:

    def __init__(self, tool_manager=None):

        self.tool_manager = tool_manager

        logger.info(
            "Planner initialized."
        )

    # =====================================================
    # MAIN PLANNER
    # =====================================================

    def plan(self, query: str):

        if not query:

            return None

        text = query.lower().strip()

        # =================================================
        # SPOTIFY
        # =================================================

        spotify_action = self._plan_spotify(text)

        if spotify_action:

            return spotify_action

        # =================================================
        # CALENDAR
        # =================================================

        calendar_action = self._plan_calendar(text)

        if calendar_action:

            return calendar_action

        # =================================================
        # SYSTEM
        # =================================================

        system_action = self._plan_system(text)

        if system_action:

            return system_action

        # =================================================
        # BROWSER
        # =================================================

        browser_action = self._plan_browser(text)

        if browser_action:

            return browser_action

        # =================================================
        # EMAIL
        # =================================================

        email_action = self._plan_email(text)

        if email_action:

            return email_action

        # =================================================
        # NO TOOL REQUIRED
        # =================================================

        return None

    # =====================================================
    # SPOTIFY PLANNER
    # =====================================================

    def _plan_spotify(self, text):

        # -------------------------------------------------
        # IMPORTANT:
        # Mentioning Spotify alone is NOT a command.
        #
        # Example:
        # "I am building an assistant integrated with Spotify"
        #
        # Must NOT trigger Spotify.
        # -------------------------------------------------

        spotify_command_words = [

            "play",

            "pause",

            "resume",

            "stop",

            "skip",

            "next song",

            "previous song",

            "previous track",

            "next track",

            "volume up",

            "volume down",

            "increase volume",

            "decrease volume",

            "mute",

            "unmute",

            "shuffle",

            "repeat"

        ]

        spotify_search_phrases = [

            "play song",

            "play music",

            "play track",

            "play artist",

            "play album",

            "listen to",

            "search spotify for",

            "find on spotify"

        ]

        # -------------------------------------------------
        # PLAYBACK COMMANDS
        # -------------------------------------------------

        for command in spotify_command_words:

            if re.search(

                rf"\b{re.escape(command)}\b",

                text

            ):

                # Avoid treating normal conversational
                # sentences containing "play" as commands.

                if command in [

                    "play",

                    "pause",

                    "resume",

                    "stop"

                ]:

                    if not any(

                        phrase in text

                        for phrase in [

                            "play music",

                            "play song",

                            "play track",

                            "play album",

                            "play artist",

                            "pause spotify",

                            "resume spotify",

                            "stop spotify",

                            "stop music",

                            "pause music",

                            "resume music"

                        ]

                    ):

                        continue

                return {

                    "tool": "spotify",

                    "action": self._spotify_action(

                        text

                    ),

                    "query": text

                }

        # -------------------------------------------------
        # SEARCH / PLAY MUSIC
        # -------------------------------------------------

        for phrase in spotify_search_phrases:

            if phrase in text:

                return {

                    "tool": "spotify",

                    "action": "play",

                    "query": text

                }

        return None

    # =====================================================
    # SPOTIFY ACTION
    # =====================================================

    def _spotify_action(self, text):

        if (

            "pause" in text

        ):

            return "pause"

        if (

            "resume" in text

            or "continue" in text

        ):

            return "resume"

        if (

            "stop" in text

        ):

            return "stop"

        if (

            "next" in text

            or "skip" in text

        ):

            return "next"

        if (

            "previous" in text

            or "back" in text

        ):

            return "previous"

        if (

            "volume up" in text

            or "increase volume" in text

        ):

            return "volume_up"

        if (

            "volume down" in text

            or "decrease volume" in text

        ):

            return "volume_down"

        if (

            "shuffle" in text

        ):

            return "shuffle"

        if (

            "repeat" in text

        ):

            return "repeat"

        return "play"

    # =====================================================
    # CALENDAR
    # =====================================================

    def _plan_calendar(self, text):

        calendar_words = [

            "remind me",

            "set a reminder",

            "create a reminder",

            "schedule",

            "calendar",

            "appointment",

            "event"

        ]

        if any(

            word in text

            for word in calendar_words

        ):

            return {

                "tool": "calendar",

                "action": "create",

                "query": text

            }

        return None

    # =====================================================
    # SYSTEM
    # =====================================================

    def _plan_system(self, text):

        system_words = [

            "open",

            "launch",

            "start"

        ]

        known_targets = [

            "notepad",

            "calculator",

            "calc",

            "paint",

            "spotify",

            "opera",

            "downloads",

            "documents",

            "desktop"

        ]

        if (

            any(

                word in text

                for word in system_words

            )

            and any(

                target in text

                for target in known_targets

            )

        ):

            return {

                "tool": "system",

                "action": "open",

                "query": text

            }

        return None

    # =====================================================
    # BROWSER
    # =====================================================

    def _plan_browser(self, text):

        browser_words = [

            "search for",

            "search",

            "look up",

            "google",

            "visit",

            "go to",

            "open youtube",

            "open google",

            "open github",

            "open wikipedia",

            "open website"

        ]

        if any(

            word in text

            for word in browser_words

        ):

            return {

                "tool": "browser",

                "action": "search",

                "query": text

            }

        return None

    # =====================================================
    # EMAIL
    # =====================================================

    def _plan_email(self, text):

        email_words = [

            "send an email",

            "send email",

            "compose email",

            "email to"

        ]

        if any(

            word in text

            for word in email_words

        ):

            return {

                "tool": "email",

                "action": "send",

                "query": text

            }

        return None
