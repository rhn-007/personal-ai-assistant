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
        # BROWSER INTENT
        # =====================================================

        elif any(

            word in t

            for word in [

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
