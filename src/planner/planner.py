class Planner:
    """
    Stage 5 Planner:
    - Converts user input into structured execution steps
    - Tool-aware planning (safe)
    """

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    # =========================================================
    # OPTIONAL DIRECT EXECUTION (FAST PATH)
    # =========================================================
    def execute(self, user_input):
        """
        Direct tool execution (bypass planning)
        """

        tool = self.tool_manager.get_tool(user_input)

        if tool:
            return tool.execute(user_input)

        return None

    # =========================================================
    # MAIN PLANNING METHOD (STANDARD INTERFACE)
    # =========================================================
    def create_plan(self, query: str):
        """
        Standard planner interface used by:
        - AgentLoop
        - Assistant
        """

        query_lower = query.lower()

        plan = []

        # ================= EMAIL RELATED =================
        if any(k in query_lower for k in ["email", "mail", "inbox", "from:"]):
            plan.append({
                "tool": "email",
                "input": query
            })

        # ================= WEB / SEARCH =================
        if any(k in query_lower for k in ["search", "google", "find", "look up"]):
            plan.append({
                "tool": "web_search",
                "input": query
            })

        # ================= DEFAULT TOOL GUESS =================
        tool = self.tool_manager.get_tool(query)

        if tool:
            plan.append({
                "tool": tool.__class__.__name__.lower(),
                "input": query
            })

        # ================= FALLBACK =================
        if not plan:
            return None

        return plan
