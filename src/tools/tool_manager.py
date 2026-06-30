"""
Tool Manager
Handles registration and execution of all assistant tools.
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
        """
        Register a new tool.

        Example:
            tool_manager.register(EmailTool())
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    # ----------------------------------------------------
    # Find Matching Tool
    # ----------------------------------------------------

    def get_tool(self, query):
        """
        Returns the first tool capable of handling the query.
        """

        for tool in self.tools.values():
            try:
                if tool.can_handle(query):
                    return tool
            except Exception as e:
                logger.error(f"Error checking tool '{tool.name}': {e}")

        return None

    # ----------------------------------------------------
    # Execute Tool
    # ----------------------------------------------------

    def execute(self, query):
        """
        Execute the appropriate tool.

        Returns:
            dict:
            {
                "handled": True/False,
                "tool": "email",
                "result": ...
            }
        """

        tool = self.get_tool(query)

        if tool is None:
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
            logger.error(f"Tool '{tool.name}' failed: {e}")

            return {
                "handled": True,
                "tool": tool.name,
                "result": f"Tool Error: {e}"
            }

    # ----------------------------------------------------
    # Utility Functions
    # ----------------------------------------------------

    def list_tools(self):
        """Return a list of registered tool names."""
        return list(self.tools.keys())

    def has_tool(self, name):
        """Check if a tool is registered."""
        return name in self.tools

    def unregister(self, name):
        """Remove a registered tool."""
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Unregistered tool: {name}")
