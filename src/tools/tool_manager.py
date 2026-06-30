class ToolManager:

    def __init__(self):
        self.tools = []

    def register(self, tool):
        self.tools.append(tool)

    def get_tool(self, query):

        for tool in self.tools:
            if tool.can_handle(query):
                return tool

        return None

    def execute(self, query):

        tool = self.get_tool(query)

        if tool:
            return tool.execute(query)

        return None
