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

        """
        Compatibility method.

        Existing ToolManager and AgentLoop code expect
        Planner.create_plan().
        """

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

        # =================================================
        # NORMAL CONVERSATION
        # =================================================

        return None

    # =====================================================
    # SPOTIFY
    # =====================================================

    def _plan_spotify(self, text):

        """
        Spotify should only activate when the user clearly
        intends to control or search Spotify.

        Merely mentioning Spotify is not enough.
        """

        # -------------------------------------------------
        # CLEAR PLAY COMMANDS
        # -------------------------------------------------

        play_phrases = [

            "play music",

            "play a song",

            "play song",

            "play some music",

            "play track",

            "play album",

            "play artist",

            "listen to",

            "put on"

        ]

        for phrase in play_phrases:

            if phrase in text:

                return {

                    "tool": "spotify",

                    "action": "play",

                    "query": text

                }

        # -------------------------------------------------
        # CLEAR PAUSE COMMANDS
        # -------------------------------------------------

        if (

            "pause spotify" in text

            or "pause music" in text

            or text == "pause"

        ):

            return {

                "tool": "spotify",

                "action": "pause",

                "query": text

            }

        # -------------------------------------------------
        # CLEAR RESUME COMMANDS
        # -------------------------------------------------

        if (

            "resume spotify" in text

            or "resume music" in text

            or text == "resume"

            or text == "continue"

        ):

            return {

                "tool": "spotify",

                "action": "resume",

                "query": text

            }

        # -------------------------------------------------
        # CLEAR STOP COMMANDS
        # -------------------------------------------------

        if (

            "stop spotify" in text

            or "stop music" in text

            or text == "stop"

        ):

            return {

                "tool": "spotify",

                "action": "stop",

                "query": text

            }

        # -------------------------------------------------
        # NEXT TRACK
        # -------------------------------------------------

        if (

            "next song" in text

            or "next track" in text

            or "skip song" in text

            or "skip track" in text

            or text == "next"

            or text == "skip"

        ):

            return {

                "tool": "spotify",

                "action": "next",

                "query": text

            }

        # -------------------------------------------------
        # PREVIOUS TRACK
        # -------------------------------------------------

        if (

            "previous song" in text

            or "previous track" in text

            or "previous song" in text

            or text == "previous"

            or text == "back"

        ):

            return {

                "tool": "spotify",

                "action": "previous",

                "query": text

            }

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        if (

            "volume up" in text

            or "increase volume" in text

            or "turn up the volume" in text

        ):

            return {

                "tool": "spotify",

                "action": "volume_up",

                "query": text

            }

        if (

            "volume down" in text

            or "decrease volume" in text

            or "turn down the volume" in text

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

            "shuffle spotify" in text

            or "shuffle music" in text

            or text == "shuffle"

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

            "repeat song" in text

            or "repeat track" in text

            or "repeat music" in text

            or text == "repeat"

        ):

            return {

                "tool": "spotify",

                "action": "repeat",

                "query": text

            }

        # -------------------------------------------------
        # SEARCH SPOTIFY
        # -------------------------------------------------

        if (

            "search spotify for" in text

            or "find on spotify" in text

            or "search on spotify" in text

        ):

            return {

                "tool": "spotify",

                "action": "play",

                "query": text

            }

        # -------------------------------------------------
        # IMPORTANT
        # -------------------------------------------------

        # The following must return None:
        #
        # "I am building an AI assistant integrated with Spotify"
        #
        # "I am working on a Spotify project"
        #
        # "Spotify is my favorite music app"

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
