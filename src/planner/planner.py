class Planner:
    """
    Stage 6 Planner (Upgraded)

    Converts natural language → structured tool execution plan
    """

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def create_plan(self, query: str):

        if not query or not isinstance(query, str):
            return None

        t = query.lower().strip()
        plan = []

        # =====================================================
        # EMAIL INTENT
        # =====================================================
        if any(k in t for k in ["email", "mail", "gmail", "inbox"]):

            # SEND EMAIL
            if any(k in t for k in ["send", "compose", "write"]):
                plan.append({
                    "tool": "email",
                    "action": "send",
                    "input": {
                        "raw": query
                    }
                })

            # FROM FILTER
            elif "from:" in t:
                sender = t.split("from:")[-1].split()[0].strip()
                plan.append({
                    "tool": "email",
                    "action": "get_from",
                    "input": {
                        "sender": sender
                    }
                })

            # DEFAULT → unread
            else:
                plan.append({
                    "tool": "email",
                    "action": "get_unread",
                    "input": {}
                })

        # =====================================================
        # SPOTIFY / MUSIC INTENT
        # =====================================================
        elif any(k in t for k in ["spotify", "play", "song", "music", "audio"]):

            plan.append({
                "tool": "spotify",
                "action": "play",
                "input": {
                    "query": query
                }
            })

        # =====================================================
        # CALENDAR INTENT
        # =====================================================
        elif any(k in t for k in ["calendar", "schedule", "meeting", "reminder", "event"]):

            plan.append({
                "tool": "calendar",
                "action": "create",
                "input": {
                    "query": query
                }
            })

        # =====================================================
        # SYSTEM / DEVICE CONTROL
        # =====================================================
        elif any(k in t for k in ["open", "file", "folder", "system", "launch"]):

            plan.append({
                "tool": "system",
                "action": "open",
                "input": {
                    "query": query
                }
            })

        # =====================================================
        # FALLBACK (IMPORTANT FOR AI FLOW)
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
