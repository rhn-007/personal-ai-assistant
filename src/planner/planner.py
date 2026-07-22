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
        # BROWSER SUMMARIZE INTENT
        # IMPORTANT: MUST COME BEFORE READ INTENT
        # =====================================================

        elif (

            t.startswith("summarize ")

            or t.startswith("summarise ")

            or t.startswith("summary of ")

            or (

                "https://" in t

                and (

                    "summarize" in t

                    or "summarise" in t

                    or "summary" in t

                )

            )

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
