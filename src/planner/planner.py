class Planner:
    """
    Stage 6 Planner (Upgraded)

    Converts natural language → structured tool execution plan
    """

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    # =========================================================
    # MAIN FUNCTION
    # =========================================================

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
                    "action": "send",
                    "input": query
                })

            else:
                plan.append({
                    "tool": "email",
                    "action": "read",
                    "input": query
                })

        # =====================================================
        # SPOTIFY INTENT (future-ready)
        # =====================================================
        elif any(k in t for k in ["spotify", "play", "song", "music"]):

            plan.append({
                "tool": "spotify",
                "action": "play",
                "input": query
            })

        # =====================================================
        # CALENDAR INTENT (future-ready)
        # =====================================================
        elif any(k in t for k in ["calendar", "schedule", "meeting", "reminder"]):

            plan.append({
                "tool": "calendar",
                "action": "create",
                "input": query
            })

        # =====================================================
        # FILE / SYSTEM INTENT (future-ready)
        # =====================================================
        elif any(k in t for k in ["open", "file", "folder", "system"]):

            plan.append({
                "tool": "system",
                "action": "open",
                "input": query
            })

        # =====================================================
        # DEFAULT: no plan
        # =====================================================
        if not plan:
            return None

        return plan
