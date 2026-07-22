import re


class Planner:

    def __init__(self, tool_manager):

        self.tool_manager = tool_manager

    # =====================================================
    # CREATE PLAN
    # =====================================================

    def create_plan(self, query: str):

        if not query or not isinstance(query, str):

            return None

        t = query.lower().strip()

        plan = []

        # =====================================================
        # BROWSER SUMMARY FOLLOW-UP INTENT
        #
        # IMPORTANT:
        # This must come BEFORE calendar, Spotify, and
        # normal browser intents.
        #
        # Examples:
        # - give a longer summary
        # - give a longer summary in about 200 words
        # - make the summary longer
        # - expand the summary
        # - make it more detailed
        # =====================================================

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

        is_summary_follow_up = any(

            phrase in t

            for phrase in summary_follow_up_phrases

        )

        # Also detect requests such as:
        #
        # "give me a 200 word summary"
        # "make it around 300 words"
        # "summarize it in 250 words"

        contains_word_count = bool(

            re.search(

                r"\b\d+\s*words?\b",

                t

            )

        )

        summary_context_words = [

            "summary",

            "summarize",

            "summarise",

            "summarization",

            "summarisation"

        ]

        contains_summary_context = any(

            word in t

            for word in summary_context_words

        )

        if (

            is_summary_follow_up

            or (

                contains_word_count

                and contains_summary_context

                and not (

                    "http://" in t

                    or "https://" in t

                )

            )

        ):

            plan.append(

                {

                    "tool": "browser",

                    "action": "summarize_last",

                    "input": {

                        "query": query

                    }

                }

            )

            return plan

        # =====================================================
        # CALENDAR INTENT
        # =====================================================

        if any(

            word in t

            for word in [

                "calendar",

                "schedule",

                "meeting",

                "reminder",

                "event"

            ]

        ):

            # ---------------------------------------------
            # DELETE EVENT
            # ---------------------------------------------

            if any(

                word in t

                for word in [

                    "delete",

                    "remove",

                    "cancel"

                ]

            ):

                plan.append(

                    {

                        "tool": "calendar",

                        "action": "delete",

                        "input": {

                            "query": query

                        }

                    }

                )

            # ---------------------------------------------
            # SHOW CALENDAR
            # ---------------------------------------------

            elif any(

                word in t

                for word in [

                    "show",

                    "list",

                    "view",

                    "what do i have",

                    "what's on"

                ]

            ):

                plan.append(

                    {

                        "tool": "calendar",

                        "action": "list",

                        "input": {}

                    }

                )

            # ---------------------------------------------
            # CREATE EVENT
            # ---------------------------------------------

            else:

                plan.append(

                    {

                        "tool": "calendar",

                        "action": "create",

                        "input": {

                            "query": query

                        }

                    }

                )

        # =====================================================
        # SPOTIFY INTENT
        # =====================================================

        elif any(

            word in t

            for word in [

                "spotify",

                "play",

                "song",

                "music",

                "audio"

            ]

        ):

            plan.append(

                {

                    "tool": "spotify",

                    "action": "play",

                    "input": {

                        "query": query

                    }

                }

            )

        # =====================================================
        # BROWSER SEARCH RESULT INTENT
        # =====================================================

        elif (

            (

                "open result" in t

                or "read result" in t

                or "open search result" in t

                or "read search result" in t

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

            result_number = (

                number_match.group(1)

            )

            # ---------------------------------------------
            # READ RESULT
            # ---------------------------------------------

            if (

                "read result" in t

                or "read search result" in t

            ):

                plan.append(

                    {

                        "tool": "browser",

                        "action": "read_result",

                        "input": {

                            "query": result_number

                        }

                    }

                )

            # ---------------------------------------------
            # OPEN RESULT
            # ---------------------------------------------

            else:

                plan.append(

                    {

                        "tool": "browser",

                        "action": "open_result",

                        "input": {

                            "query": result_number

                        }

                    }

                )

        # =====================================================
        # BROWSER SUMMARIZE NEW WEBPAGE INTENT
        # =====================================================

        elif (

            t.startswith("summarize ")

            or t.startswith("summarise ")

            or t.startswith("summarize this ")

            or t.startswith("summarise this ")

        ):

            plan.append(

                {

                    "tool": "browser",

                    "action": "summarize",

                    "input": {

                        "query": query

                    }

                }

            )

        # =====================================================
        # BROWSER READ INTENT
        # =====================================================

        elif (

            t.startswith("read ")

            or t.startswith("read this webpage")

            or t.startswith("read this website")

            or t.startswith("read webpage")

            or t.startswith("read website")

            or t.startswith("extract text from")

            or (

                "https://" in t

                and any(

                    word in t

                    for word in [

                        "read",

                        "extract"

                    ]

                )

            )

        ):

            plan.append(

                {

                    "tool": "browser",

                    "action": "read",

                    "input": {

                        "query": query

                    }

                }

            )

        # =====================================================
        # BROWSER SEARCH INTENT
        # =====================================================

        elif any(

            phrase in t

            for phrase in [

                "search for",

                "search",

                "look up",

                "find online",

                "google"

            ]

        ):

            plan.append(

                {

                    "tool": "browser",

                    "action": "search",

                    "input": {

                        "query": query

                    }

                }

            )

        # =====================================================
        # BROWSER OPEN INTENT
        # =====================================================

        elif any(

            phrase in t

            for phrase in [

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

                {

                    "tool": "browser",

                    "action": "open",

                    "input": {

                        "query": query

                    }

                }

            )

        # =====================================================
        # SYSTEM INTENT
        # =====================================================

        elif any(

            word in t

            for word in [

                "open",

                "launch",

                "start",

                "folder",

                "file"

            ]

        ):

            plan.append(

                {

                    "tool": "system",

                    "action": "open",

                    "input": {

                        "query": query

                    }

                }

            )

        # =====================================================
        # EMAIL INTENT
        # =====================================================

        elif any(

            word in t

            for word in [

                "email",

                "mail",

                "gmail",

                "inbox"

            ]

        ):

            plan.append(

                {

                    "tool": "email",

                    "action": "default",

                    "input": {

                        "query": query

                    }

                }

            )

        # =====================================================
        # FALLBACK
        # =====================================================

        else:

            return None

        return plan
