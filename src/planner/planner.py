class Planner:

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def create_plan(self, query: str):

        if not query or not isinstance(query, str):
            return None

        t = query.lower().strip()

        # =====================================================
        # SYSTEM / APP OPENING
        # =====================================================

        if any(
            phrase in t
            for phrase in [
                "open ",
                "launch ",
                "start "
            ]
        ):

            return [
                {
                    "tool": "system",
                    "action": "open",
                    "input": {
                        "query": query
                    }
                }
            ]

        # =====================================================
        # EMAIL INTENT
        # =====================================================

        if any(
            k in t
            for k in [
                "email",
                "mail",
                "gmail",
                "inbox"
            ]
        ):

            if any(
                k in t
                for k in [
                    "send",
                    "compose",
                    "write"
                ]
            ):

                return [
                    {
                        "tool": "email",
                        "action": "send",
                        "input": {
                            "raw": query
                        }
                    }
                ]

            if "from:" in t:

                sender = (
                    t.split("from:")[-1]
                    .split()[0]
                    .strip()
                )

                return [
                    {
                        "tool": "email",
                        "action": "get_from",
                        "input": {
                            "sender": sender
                        }
                    }
                ]

            return [
                {
                    "tool": "email",
                    "action": "get_unread",
                    "input": {}
                }
            ]

        # =====================================================
        # SPOTIFY / MUSIC INTENT
        # =====================================================

        if any(
            k in t
            for k in [
                "spotify",
                "play",
                "song",
                "music",
                "audio"
            ]
        ):

            return [
                {
                    "tool": "spotify",
                    "action": "play",
                    "input": {
                        "query": query
                    }
                }
            ]

        # =====================================================
        # CALENDAR INTENT
        # =====================================================

        if any(
            k in t
            for k in [
                "calendar",
                "schedule",
                "meeting",
                "reminder",
                "event"
            ]
        ):

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
        # FALLBACK
        # =====================================================

        return [
            {
                "tool": "llm",
                "action": "chat",
                "input": {
                    "query": query
                }
            }
        ]
