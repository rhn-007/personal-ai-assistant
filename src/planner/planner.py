class Planner:

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def execute(self, user_input: str):
        tool = self.tool_manager.get_tool(user_input)
        if tool:
            return tool.execute(user_input)
        return None

    def create_plan(self, query: str):
        query = query.lower()

        plan = []

        # ONLY trigger email if clearly email-related
        email_keywords = ["email", "inbox", "unread", "mail", "from:", "send"]

        if any(k in query for k in email_keywords):
            plan.append({
                "tool": "email",
                "input": query
            })
            return plan

        # OTHERWISE: no tool or generic fallback
        return []
