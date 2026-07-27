import re


class Planner:

    def __init__(self, tool_manager):

        self.tool_manager = tool_manager

    # =====================================================
    # HELPER METHODS
    # =====================================================

    def _contains_any(self, text, phrases):

        return any(
            phrase in text
            for phrase in phrases
        )

    def _create_step(
        self,
        tool,
        action,
        query
    ):

        return {
            "tool": tool,
            "action": action,
            "input": {
                "query": query
            }
        }

    # =====================================================
    # CREATE PLAN
    # =====================================================

    def create_plan(self, query: str):

        if not query or not isinstance(query, str):

            return None

        original_query = query.strip()

        if not original_query:

            return None

        t = original_query.lower()

        plan = []

        # =================================================
        # BROWSER - SUMMARY FOLLOW-UP
        # =================================================

        summary_follow_up_phrases = [

            "longer summary",
            "longer summarize",
            "give a longer summary",
            "give me a longer summary",
            "expand the summary",
            "expand that summary",
            "make the summary longer",
            "make it longer",
            "make the summary more detailed",
            "more detailed summary",
            "expand it",
            "elaborate on the summary",
            "explain the summary in more detail",
            "give more details"

        ]

        contains_word_count = bool(

            re.search(
                r"\b\d+\s*words?\b",
                t
            )

        )

        contains_summary_context = self._contains_any(

            t,

            [

                "summary",
                "summarize",
                "summarise",
                "summarization",
                "summarisation"

            ]

        )

        if (

            self._contains_any(
                t,
                summary_follow_up_phrases
            )

            or (

                contains_word_count

                and contains_summary_context

                and "http://" not in t

                and "https://" not in t

            )

        ):

            plan.append(

                self._create_step(

                    "browser",
                    "summarize_last",
                    original_query

                )

            )

            return plan

        # =================================================
        # BROWSER - OPEN / READ SEARCH RESULT
        # =================================================

        if (

            self._contains_any(

                t,

                [

                    "open result",
                    "read result",
                    "open search result",
                    "read search result"

                ]

            )

            and any(
                char.isdigit()
                for char in t
            )

        ):

            number_match = re.search(

                r"\b(\d+)\b",
                t

            )

            if not number_match:

                return None

            result_number = number_match.group(1)

            if self._contains_any(

                t,

                [

                    "read result",
                    "read search result"

                ]

            ):

                plan.append(

                    self._create_step(

                        "browser",
                        "read_result",
                        result_number

                    )

                )

            else:

                plan.append(

                    self._create_step(

                        "browser",
                        "open_result",
                        result_number

                    )

                )

            return plan

        # =================================================
        # BROWSER - SUMMARIZE WEBPAGE
        # =================================================

        if (

            t.startswith("summarize ")

            or t.startswith("summarise ")

            or t.startswith("summarize this ")

            or t.startswith("summarise this ")

        ):

            plan.append(

                self._create_step(

                    "browser",
                    "summarize",
                    original_query

                )

            )

            return plan

        # =================================================
        # BROWSER - READ WEBPAGE
        # =================================================

        if (

            t.startswith("read ")

            or t.startswith("read this webpage")

            or t.startswith("read this website")

            or t.startswith("read webpage")

            or t.startswith("read website")

            or t.startswith("extract text from")

            or (

                "https://" in t

                and self._contains_any(

                    t,

                    [

                        "read",
                        "extract"

                    ]

                )

            )

        ):

            plan.append(

                self._create_step(

                    "browser",
                    "read",
                    original_query

                )

            )

            return plan

        # =================================================
        # BROWSER - SEARCH
        # =================================================

        if self._contains_any(

            t,

            [

                "search for",
                "search",
                "look up",
                "find online",
                "google"

            ]

        ):

            plan.append(

                self._create_step(

                    "browser",
                    "search",
                    original_query

                )

            )

            return plan

        # =================================================
        # BROWSER - OPEN WEBSITE
        # =================================================

        if self._contains_any(

            t,

            [

                "open youtube",
                "open google",
                "open github",
                "open wikipedia",
                "open chatgpt",
                "open reddit",
                "open instagram",
                "open facebook",
                "open twitter",
                "open x",
                "open website",
                "open browser",
                "go to",
                "visit",
                "browse"

            ]

        ):

            plan.append(

                self._create_step(

                    "browser",
                    "open",
                    original_query

                )

            )

            return plan

        # =================================================
        # SPOTIFY - PAUSE
        # =================================================

        if self._contains_any(

            t,

            [

                "pause music",
                "pause song",
                "pause spotify",
                "pause playback"

            ]

        ):

            plan.append(

                self._create_step(

                    "spotify",
                    "pause",
                    original_query

                )

            )

            return plan

        # =================================================
        # SPOTIFY - NEXT
        # =================================================

        if self._contains_any(

            t,

            [

                "next song",
                "next track",
                "skip song",
                "skip track"

            ]

        ):

            plan.append(

                self._create_step(

                    "spotify",
                    "next",
                    original_query

                )

            )

            return plan

        # =================================================
        # SPOTIFY - PREVIOUS
        # =================================================

        if self._contains_any(

            t,

            [

                "previous song",
                "previous track",
                "last song",
                "go back"

            ]

        ):

            plan.append(

                self._create_step(

                    "spotify",
                    "previous",
                    original_query

                )

            )

            return plan

        # =================================================
        # SPOTIFY - PLAY
        # =================================================

        if self._contains_any(

            t,

            [

                "spotify",
                "play music",
                "play song",
                "play ",
                "listen to",
                "put on some music"

            ]

        ):

            plan.append(

                self._create_step(

                    "spotify",
                    "play",
                    original_query

                )

            )

            return plan

        # =================================================
        # CALENDAR - DELETE
        # =================================================

        if (

            self._contains_any(

                t,

                [

                    "calendar",
                    "schedule",
                    "meeting",
                    "reminder",
                    "event",
                    "appointment"

                ]

            )

            and self._contains_any(

                t,

                [

                    "delete",
                    "remove",
                    "cancel"

                ]

            )

        ):

            plan.append(

                self._create_step(

                    "calendar",
                    "delete",
                    original_query

                )

            )

            return plan

        # =================================================
        # CALENDAR - LIST
        # =================================================

        if (

            self._contains_any(

                t,

                [

                    "calendar",
                    "schedule",
                    "reminder",
                    "event",
                    "appointment"

                ]

            )

            and self._contains_any(

                t,

                [

                    "show",
                    "list",
                    "view",
                    "what do i have",
                    "what's on",
                    "whats on"

                ]

            )

        ):

            plan.append(

                {

                    "tool": "calendar",

                    "action": "list",

                    "input": {}

                }

            )

            return plan

        # =================================================
        # CALENDAR - CREATE
        # =================================================

        if self._contains_any(

            t,

            [

                "calendar",
                "schedule",
                "meeting",
                "reminder",
                "event",
                "appointment",
                "remind me"

            ]

        ):

            plan.append(

                self._create_step(

                    "calendar",
                    "create",
                    original_query

                )

            )

            return plan

        # =================================================
        # SYSTEM - OPEN APPLICATION OR FOLDER
        # =================================================

        if self._contains_any(

            t,

            [

                "open",
                "launch",
                "start",
                "folder",
                "file"

            ]

        ):

            plan.append(

                self._create_step(

                    "system",
                    "open",
                    original_query

                )

            )

            return plan

        # =================================================
        # EMAIL
        # =================================================

        if self._contains_any(

            t,

            [

                "email",
                "mail",
                "gmail",
                "inbox",
                "from:"

            ]

        ):

            plan.append(

                self._create_step(

                    "email",
                    "default",
                    original_query

                )

            )

            return plan

        # =================================================
        # FALLBACK
        # =================================================

        return None
    
