class Planner:

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def execute(self, user_input: str):
        """
        Direct execution (fast path fallback)
        """
        tool = self.tool_manager.get_tool(user_input)

        if tool:
            return tool.execute(user_input)

        return None

    # ✅ FIX: standard method name expected by AgentLoop
    def create_plan(self, query: str):
        """
        Convert user request → multi-step execution plan
        """

        query = query.lower()

        plan = []

        # email-related planning
        if any(k in query for k in ["email", "mail", "inbox"]):
            plan.append({
                "tool": "email",
                "input": query
            })

        # generic fallback tool attempt
        plan.append({
            "tool": "auto",
            "input": query
        })

        return plan
