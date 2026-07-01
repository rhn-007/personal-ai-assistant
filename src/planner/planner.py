class Planner:

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def execute(self, user_input):

        tool = self.tool_manager.get_tool(user_input)

        if tool:
            return tool.execute(user_input)

        return None

    def create_task_plan(self, query: str):
        """
        Convert user request → multi-step tool plan
        """
    
        return [
            {"tool": "email", "input": query},
            {"tool": "web_search", "input": query}
        ]
