from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ToolManager:
    """
    Unified Tool Manager (FINAL FIXED VERSION)

    - register tools
    - get tool by name
    - route query → tool
    - safe execution
    """

    def __init__(self):
        self.tools = {}

    # ---------------- REGISTER ----------------
    def register(self, tool):
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    # ---------------- GET TOOL (FIXED API) ----------------
    def get_tool_by_name(self, name):
        return self.get_tool(name)
    
    def get_tool(self, name: str):
        """
        FIX: restores compatibility with AgentLoop + Planner
        """
        return self.tools.get(name)

    # ---------------- ROUTER ----------------
    def route(self, query: str):
        for tool in self.tools.values():
            try:
                if hasattr(tool, "can_handle") and tool.can_handle(query):
                    return tool
            except Exception as e:
                logger.error(f"Tool check error ({tool.name}): {e}")
        return None

    # ---------------- EXECUTE (SAFE LAYER) ----------------
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

        def execute_by_name(self, name, action, query):
            tool = self.get_tool_by_name(name)
        
            if not tool:
                return {
                    "handled": False,
                    "tool": name,
                    "result": None
                }
        
            try:
                # ACTION-AWARE EXECUTION
                if hasattr(tool, "execute_action"):
                    result = tool.execute_action(action, query)
                else:
                    result = tool.execute(query)
        
                return {
                    "handled": True,
                    "tool": name,
                    "result": result
                }
        
            except Exception as e:
                return {
                    "handled": True,
                    "tool": name,
                    "result": f"Tool Error: {e}"
                }

    # ---------------- LIST ----------------
    def list_tools(self):
        return list(self.tools.keys())
