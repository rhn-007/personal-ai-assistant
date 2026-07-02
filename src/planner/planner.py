class Planner:
    """
    Stage 6 Planner (Upgraded)

    Converts natural language → structured tool execution plan
    """

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def create_plan(self, query: str):

        if not query:
            return None

        t = query.lower()
        plan = []

        # =====================================================
        # EMAIL INTENT
        # =====================================================
        if any(k in t for k in ["email", "mail", "gmail", "inbox"]):

            if "send" in t:
                plan.append({
                    "tool": "email",
                    "action": "send_email",
                    "input": {
                        "raw": query
                    }
                })

            elif "from:" in t:
                sender = t.split("from:")[-1].split()[0]
                plan.append({
                    "tool": "email",
                    "action": "get_from_sender",
                    "input": {
                        "sender": sender
                    }
                })

            else:
                plan.append({
                    "tool": "email",
                    "action": "get_unread",
                    "input": {}
                })

        # =====================================================
        # SPOTIFY INTENT (future-ready)
        # =====================================================
        elif any(k in t for k in ["spotify", "play", "song", "music"]):

            plan.append({
                "tool": "spotify",
                "action": "play_song",
                "input": {
                    "query": query
                }
            })

        # =====================================================
        # CALENDAR INTENT (future-ready)
        # =====================================================
        elif any(k in t for k in ["calendar", "schedule", "meeting", "reminder"]):

            plan.append({
                "tool": "calendar",
                "action": "create_event",
                "input": {
                    "query": query
                }
            })

        # =====================================================
        # SYSTEM INTENT (future-ready)
        # =====================================================
        elif any(k in t for k in ["open", "file", "folder", "system"]):

            plan.append({
                "tool": "system",
                "action": "open_app",
                "input": {
                    "query": query
                }
            })

        if not plan:
            return None

        return plan
