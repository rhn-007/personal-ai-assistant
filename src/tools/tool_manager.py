"""
Tool Manager (FIXED - Unified Tool Response System)
"""

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ToolManager:
    """Central manager for all assistant tools."""

    def __init__(self):
        self.tools = {}

    # ----------------------------------------------------
    # Register Tools
    # ----------------------------------------------------

    def register(self, tool):
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    # ----------------------------------------------------
    # Find Matching Tool
    # ----------------------------------------------------

    def get_tool(self, query):
        for tool in self.tools.values():
            try:
                if tool.can_handle(query):
                    return tool
            except Exception as e:
                logger.error(f"Tool check error '{tool.name}': {e}")

        return None

    # ----------------------------------------------------
    # STANDARDIZED EXECUTION (FIXED)
    # ----------------------------------------------------

    def execute(self, query):
        """
        ALWAYS returns:

        {
            "handled": bool,
            "tool": str | None,
            "type": "text" | "list" | "dict" | "error" | "none",
            "data": any
        }
        """

        tool = self.get_tool(query)

        if tool is None:
            return {
                "handled": False,
                "tool": None,
                "type": "none",
                "data": None
            }

        try:
            logger.info(f"Executing tool: {tool.name}")

            result = tool.execute(query)

            # -------------------------------
            # NORMALIZATION LAYER (CRITICAL)
            # -------------------------------

            if isinstance(result, str):
                normalized = {
                    "handled": True,
                    "tool": tool.name,
                    "type": "text",
                    "data": result
                }

            elif isinstance(result, list):
                normalized = {
                    "handled": True,
                    "tool": tool.name,
                    "type": "list",
                    "data": result
                }

            elif isinstance(result, dict):
                normalized = {
                    "handled": True,
                    "tool": tool.name,
                    "type": result.get("type", "dict"),
                    "data": result.get("data", result)
                }

            else:
                normalized = {
                    "handled": True,
                    "tool": tool.name,
                    "type": "text",
                    "data": str(result)
                }

            return normalized

        except Exception as e:
            logger.error(f"Tool '{tool.name}' failed: {e}")

            return {
                "handled": True,
                "tool": tool.name,
                "type": "error",
                "data": str(e)
            }

    # ----------------------------------------------------
    # Utility Functions
    # ----------------------------------------------------

    def list_tools(self):
        return list(self.tools.keys())

    def has_tool(self, name):
        return name in self.tools

    def unregister(self, name):
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Unregistered tool: {name}")
