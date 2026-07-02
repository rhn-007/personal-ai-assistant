class Planner:
    """
    Stage 6 Planner (Upgraded - Stable Agent Version)

    Converts natural language → structured tool execution plan
    """

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    # =========================================================
    # MAIN FUNCTION
    # =========================================================
    def create_plan(self, query: str):

        if not query or not isinstance(query, str):
            return None

        t = query.lower().strip()
        plan = []

        # =====================================================
        # EMAIL INTENT (HIGH PRIORITY)
        # =====================================================
        if any(k in t for k in ["email", "mail", "gmail", "inbox"]):

            if any(k in t for k in ["send", "compose", "write"]):
                plan.append({
                    "tool": "email",
                    "action": "send_email",
                    "input": {"raw": query}
                })

            elif "from:" in t:
                sender = t.split("from:")[-1].split()[0].strip()
                plan.append({
                    "tool": "email",
                    "action": "get_from",
                    "input": {"sender": sender}
                })

            else:
                plan.append({
                    "tool": "email",
                    "action": "get_unread",
                    "input": {}
                })

        # =====================================================
        # CALENDAR INTENT (IMPORTANT PRODUCTIVITY LAYER)
        # =====================================================
        elif any(k in t for k in ["calendar", "schedule", "meeting", "reminder", "event"]):

            if any(k in t for k in ["delete", "remove"]):
                plan.append({
                    "tool": "calendar",
                    "action": "delete",
                    "input": {"query": query}
                })

            elif any(k in t for k in ["show", "view", "list"]):
                plan.append({
                    "tool": "calendar",
                    "action": "view",
                    "input": {}
                })

            else:
                plan.append({
                    "tool": "calendar",
                    "action": "create",
                    "input": {"query": query}
                })

        # =====================================================
        # SPOTIFY / MUSIC INTENT
        # =====================================================
        elif any(k in t for k in [
            "spotify", "play", "song", "music", "audio", "listen"
        ]):

            plan.append({
                "tool": "spotify",
                "action": "play",
                "input": {
                    "query": query
                }
            })

        # =====================================================
        # SYSTEM / DEVICE CONTROL
        # =====================================================
        elif any(k in t for k in [
            "open", "file", "folder", "system", "launch", "run"
        ]):

            plan.append({
                "tool": "system",
                "action": "open",
                "input": {
                    "query": query
                }
            })

        # =====================================================
        # FALLBACK (LLM HANDLING - IMPORTANT)
        # =====================================================
        else:
            plan.append({
                "tool": "llm",
                "action": "chat",
                "input": {
                    "query": query
                }
            })

        return plan
