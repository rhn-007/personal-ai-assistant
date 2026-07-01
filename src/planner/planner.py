class Planner:

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def execute(self, user_input: str):
        tool = self.tool_manager.get_tool(user_input)
        if tool:
            return tool.execute(user_input)
        return None

    # =========================================================
    # INTENT CLASSIFIER
    # =========================================================
    def _classify_intent(self, text: str):

        t = text.lower()

        if any(k in t for k in [
            "email", "inbox", "unread", "mail", "from:", "send"
        ]):
            return "email", 0.95

        # EVERYTHING ELSE = CHAT (SAFE DEFAULT)
        return "chat", 1.0

    # =========================================================
    # PLAN GENERATION (NEVER BLOCK CHAT)
    # =========================================================
    def create_plan(self, query: str):

        intent, confidence = self._classify_intent(query)

        # EMAIL ONLY PLAN
        if intent == "email":
            return [{
                "tool": "email",
                "input": query
            }]

        # CHAT → ALWAYS RETURN EMPTY PLAN (NOT ERROR)
        return []
