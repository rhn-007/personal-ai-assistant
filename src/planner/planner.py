class Planner:

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def execute(self, user_input: str):
        tool = self.tool_manager.get_tool(user_input)

        if tool:
            return tool.execute(user_input)

        return None

    # ✅ STANDARD METHOD (THIS IS WHAT EVERYTHING MUST USE)
    def create_plan(self, query: str):
        query = query.lower()

        plan = []

        if any(k in query for k in ["email", "mail", "inbox"]):
            plan.append({
                "tool": "email",
                "input": query
            })

        # fallback step
        plan.append({
            "tool": "email",
            "input": query
        })

        return plan
