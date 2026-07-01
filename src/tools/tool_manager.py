from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ToolManager:
    """
    Clean Tool Manager (Fixed Architecture)

    - register tools
    - get tool by name
    - route tool by query
    - execute safely
    """

    def __init__(self):
        self.tools = {}

    # ---------------- REGISTER ----------------

    def register(self, tool):
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    # ---------------- GET BY NAME ----------------

    def get_tool_by_name(self, name: str):
        return self.tools.get(name)

    # ---------------- ROUTE BY QUERY ----------------

    def route(self, query: str):
        for tool in self.tools.values():
            try:
                if tool.can_handle(query):
                    return tool
            except Exception as e:
                logger.error(f"Tool check error ({tool.name}): {e}")
        return None

    # ---------------- EXECUTE TOOL ----------------

    def execute(self, query: str):
        tool = self.route(query)

        if not tool:
            return {
                "handled": False,
                "tool": None,
                "result": None
            }

        try:
            logger.info(f"Executing tool: {tool.name}")
            result = tool.execute(query)

            return {
                "handled": True,
                "tool": tool.name,
                "result": result
            }

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "handled": True,
                "tool": tool.name,
                "result": f"Tool Error: {e}"
            }

    # ---------------- LIST ----------------

    def list_tools(self):
        return list(self.tools.keys())
