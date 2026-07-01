class Planner:

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def create_plan(self, query: str):

        t = query.lower()

        # EMAIL INTENT
        if any(k in t for k in ["email", "inbox", "from:", "mail"]):
            return [{
                "tool": "email",
                "input": query
            }]

        # DEFAULT SAFE PLAN (IMPORTANT FIX)
        return [{
            "tool": "chat",
            "input": query
        }]
