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


        # Priority order:
        #
        # 1. Email
        # 2. Calendar
        # 3. Spotify
        # 4. System
        # 5. Browser


        email_plan = self._plan_email(text)

        if email_plan:
            return email_plan


        calendar_plan = self._plan_calendar(text)

        if calendar_plan:
            return calendar_plan


        spotify_plan = self._plan_spotify(text)

        if spotify_plan:
            return spotify_plan


        system_plan = self._plan_system(text)

        if system_plan:
            return system_plan


        browser_plan = self._plan_browser(text)

        if browser_plan:
            return browser_plan


        return None



    # =====================================================
    # SPOTIFY
    # =====================================================

    def _plan_spotify(self, text):


        commands = {


            "pause":
                "pause",

            "resume":
                "resume",

            "stop":
                "stop",

            "next":
                "next",

            "skip":
                "next",

            "previous":
                "previous"

        }


        for word, action in commands.items():

            if text == word:

                return {

                    "tool": "spotify",

                    "action": action,

                    "query": text

                }


        if (
            "pause spotify" in text
            or "pause music" in text
        ):

            return {

                "tool": "spotify",
                "action": "pause",
                "query": text

            }



        if (
            "resume spotify" in text
            or "resume music" in text
        ):

            return {

                "tool": "spotify",
                "action": "resume",
                "query": text

            }



        if (
            "stop spotify" in text
            or "stop music" in text
        ):

            return {

                "tool": "spotify",
                "action": "stop",
                "query": text

            }



        if (
            "volume up" in text
            or "increase volume" in text
            or "turn up volume" in text
            or "louder" in text
        ):

            return {

                "tool": "spotify",
                "action": "volume_up",
                "query": text

            }



        if (
            "volume down" in text
            or "decrease volume" in text
            or "turn down volume" in text
            or "quieter" in text
        ):

            return {

                "tool": "spotify",
                "action": "volume_down",
                "query": text

            }



        if (
            text == "shuffle"
            or "shuffle spotify" in text
        ):

            return {

                "tool": "spotify",
                "action": "shuffle",
                "query": text

            }



        if (
            text == "repeat"
            or "repeat song" in text
        ):

            return {

                "tool": "spotify",
                "action": "repeat",
                "query": text

            }



        # PLAY SONG

        play_match = re.match(

            r"^(?:please\s+)?"
            r"(?:play|listen to|put on)"
            r"(?:\s+(.+))?$",

            text

        )


        if play_match:

            song = play_match.group(1)


            if song:

                return {

                    "tool": "spotify",
                    "action": "play",
                    "query": song.strip()

                }


            return {

                "tool": "spotify",
                "action": "play",
                "query": "random music"

            }



        search_patterns = [

            r"search spotify for (.+)",

            r"search on spotify for (.+)",

            r"find on spotify (.+)"

        ]


        for pattern in search_patterns:

            match = re.match(
                pattern,
                text
            )


            if match:

                return {

                    "tool": "spotify",

                    "action": "play",

                    "query": match.group(1)

                }



        return None



    # =====================================================
    # CALENDAR
    # =====================================================

    def _plan_calendar(self, text):


        view = [

            "show my calendar",

            "view my calendar",

            "open my calendar",

            "check my calendar",

            "what is on my calendar",

            "show my events",

            "list my events",

            "show schedule"

        ]


        if any(
            x in text
            for x in view
        ):

            return {

                "tool": "calendar",

                "action": "view",

                "query": text

            }



        create = [

            "remind me",

            "set a reminder",

            "create reminder",

            "schedule event",

            "create event",

            "appointment"

        ]


        if any(
            x in text
            for x in create
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


        commands = [

            "open",

            "launch",

            "start"

        ]


        targets = [

            "calculator",

            "calc",

            "notepad",

            "paint",

            "spotify",

            "whatsapp",

            "opera",

            "downloads",

            "documents",

            "desktop"

        ]


        has_command = any(

            re.search(
                rf"\b{x}\b",
                text
            )

            for x in commands

        )


        has_target = any(

            re.search(
                rf"\b{x}\b",
                text
            )

            for x in targets

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


        phrases = [

            "search for",

            "look up",

            "google",

            "visit",

            "go to",

            "open youtube",

            "open github",

            "open wikipedia"

        ]


        if any(

            x in text

            for x in phrases

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


        phrases = [

            "send email",

            "send an email",

            "compose email",

            "compose an email",

            "write an email"

        ]


        if any(

            x in text

            for x in phrases

        ):

            return {

                "tool": "email",

                "action": "send",

                "query": text

            }


        return None
