class Planner:

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    def execute(self, user_input):

        tool = self.tool_manager.get_tool(user_input)

        if tool:
            return tool.execute(user_input)

        return None
