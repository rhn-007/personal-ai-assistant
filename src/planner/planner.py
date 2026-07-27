"""
Planner - Decides whether a user request requires a tool.

The planner is intentionally conservative.

Mentioning a tool or application does not automatically
mean the user wants to use it.
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
    # COMPATIBILITY METHOD
    # =====================================================

    def create_plan(self, query: str):

        return self.plan(query)

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

        spotify_plan = self._plan_spotify(text)

        if spotify_plan:

            return spotify_plan

        # =================================================
        # CALENDAR
        # =================================================

        calendar_plan = self._plan_calendar(text)

        if calendar_plan:

            return calendar_plan

        # =================================================
        # SYSTEM
        # =================================================

        system_plan = self._plan_system(text)

        if system_plan:

            return system_plan

        # =================================================
        # BROWSER
        # =================================================

        browser_plan = self._plan_browser(text)

        if browser_plan:

            return browser_plan

        # =================================================
        # EMAIL
        # =================================================

        email_plan = self._plan_email(text)

        if email_plan:

            return email_plan

        return None

    # =====================================================
    # SPOTIFY
    # =====================================================

    def _plan_spotify(self, text):

        # -------------------------------------------------
        # PAUSE
        # -------------------------------------------------

        if (

            text == "pause"

            or "pause spotify" in text

            or "pause music" in text

            or "pause the music" in text

        ):

            return {

                "tool": "spotify",

                "action": "pause",

                "query": text

            }

        # -------------------------------------------------
        # RESUME
        # -------------------------------------------------

        if (

            text == "resume"

            or text == "continue"

            or "resume spotify" in text

            or "resume music" in text

        ):

            return {

                "tool": "spotify",

                "action": "resume",

                "query": text

            }

        # -------------------------------------------------
        # STOP
        # -------------------------------------------------

        if (

            text == "stop"

            or "stop spotify" in text

            or "stop music" in text

        ):

            return {

                "tool": "spotify",

                "action": "stop",

                "query": text

            }

        # -------------------------------------------------
        # NEXT
        # -------------------------------------------------

        if (

            text == "next"

            or text == "skip"

            or "next song" in text

            or "next track" in text

            or "skip song" in text

            or "skip track" in text

        ):

            return {

                "tool": "spotify",

                "action": "next",

                "query": text

            }

        # -------------------------------------------------
        # PREVIOUS
        # -------------------------------------------------

        if (

            text == "previous"

            or text == "back"

            or "previous song" in text

            or "previous track" in text

            or "previous music" in text

        ):

            return {

                "tool": "spotify",

                "action": "previous",

                "query": text

            }

        # -------------------------------------------------
        # VOLUME UP
        # -------------------------------------------------

        if (

            "volume up" in text

            or "increase volume" in text

            or "turn up the volume" in text

            or "louder" in text

        ):

            return {

                "tool": "spotify",

                "action": "volume_up",

                "query": text

            }

        # -------------------------------------------------
        # VOLUME DOWN
        # -------------------------------------------------

        if (

            "volume down" in text

            or "decrease volume" in text

            or "turn down the volume" in text

            or "quieter" in text

        ):

            return {

                "tool": "spotify",

                "action": "volume_down",

                "query": text

            }

        # -------------------------------------------------
        # SHUFFLE
        # -------------------------------------------------

        if (

            text == "shuffle"

            or "shuffle spotify" in text

            or "shuffle music" in text

        ):

            return {

                "tool": "spotify",

                "action": "shuffle",

                "query": text

            }

        # -------------------------------------------------
        # REPEAT
        # -------------------------------------------------

        if (

            text == "repeat"

            or "repeat song" in text

            or "repeat track" in text

            or "repeat music" in text

        ):

            return {

                "tool": "spotify",

                "action": "repeat",

                "query": text

            }

        # =================================================
        # PLAY MUSIC
        # =================================================

        # Explicit play commands
        #
        # Examples:
        #
        # play blinding lights
        # play the weeknd
        # play some music
        # play music
        # play song blinding lights
        # listen to blinding lights
        # put on blinding lights

        play_match = re.match(

            r"^(?:please\s+)?"

            r"(?:play|listen to|put on)"

            r"(?:\s+(?:the|song|music|track|album|artist))?"

            r"\s+(.+)$",

            text

        )

        if play_match:

            query = play_match.group(1).strip()

            if query:

                return {

                    "tool": "spotify",

                    "action": "play",

                    "query": query

                }

        # =================================================
        # SEARCH SPOTIFY
        # =================================================

        search_patterns = [

            r"search spotify for (.+)",

            r"search on spotify for (.+)",

            r"find on spotify (.+)",

            r"find (.+) on spotify"

        ]

        for pattern in search_patterns:

            match = re.match(

                pattern,

                text

            )

            if match:

                query = match.group(1).strip()

                return {

                    "tool": "spotify",

                    "action": "play",

                    "query": query

                }

        # -------------------------------------------------
        # IMPORTANT
        # -------------------------------------------------

        # These must NOT activate Spotify:
        #
        # I am working on an AI assistant integrated with Spotify
        # I am building a Spotify project
        # Spotify is my favorite app
        # I use Spotify every day
        #
        # Because they do not contain a direct play/control command.

        return None

    # =====================================================
    # CALENDAR
    # =====================================================

    def _plan_calendar(self, text):

        calendar_phrases = [

            "remind me",

            "set a reminder",

            "create a reminder",

            "schedule a reminder",

            "schedule an event",

            "create an event",

            "calendar event",

            "appointment"

        ]

        if any(

            phrase in text

            for phrase in calendar_phrases

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

        command_words = [

            "open",

            "launch",

            "start"

        ]

        targets = [

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

        has_command = any(

            re.search(

                rf"\b{re.escape(word)}\b",

                text

            )

            for word in command_words

        )

        has_target = any(

            re.search(

                rf"\b{re.escape(target)}\b",

                text

            )

            for target in targets

        )

        if has_command and has_target:

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

        browser_phrases = [

            "search for",

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

            phrase in text

            for phrase in browser_phrases

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

        email_phrases = [

            "send an email",

            "send email",

            "compose an email",

            "compose email",

            "write an email"

        ]

        if any(

            phrase in text

            for phrase in email_phrases

        ):

            return {

                "tool": "email",

                "action": "send",

                "query": text

            }

        return None
