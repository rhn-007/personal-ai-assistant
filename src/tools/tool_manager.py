from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ToolManager:
    """
    Stage 6 Tool Manager (Production-ready)

    Features:
    - tool registry
    - direct name lookup
    - query routing
    - structured execution
    - safe failure handling
    """

    def __init__(self):
        self.tools = {}

    # =========================================================
    # REGISTER TOOL
    # =========================================================

    def register(self, tool):
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    # =========================================================
    # GET TOOL BY NAME (USED BY AGENT LOOP)
    # =========================================================

    def get_tool_by_name(self, name: str):
        return self.tools.get(name)

    # =========================================================
    # ROUTE TOOL BY QUERY (USED BY LEGACY / FALLBACK)
    # =========================================================

    def route(self, query: str):
        for tool in self.tools.values():
            try:
                if hasattr(tool, "can_handle") and tool.can_handle(query):
                    return tool
            except Exception as e:
                logger.error(f"Tool routing error ({tool.name}): {e}")

        return None

    # =========================================================
    # EXECUTE (LEGACY + FALLBACK SUPPORT)
    # =========================================================

    def execute(self, payload):
        """
        Unified execution layer

        Supports:
        - string queries (legacy)
        - structured payloads (new system)
        """

        try:
            # -----------------------------------------
            # CASE 1: legacy string input
            # -----------------------------------------
            if isinstance(payload, str):
                tool = self.route(payload)

                if not tool:
                    return {
                        "handled": False,
                        "tool": None,
                        "result": None
                    }

                result = tool.execute(payload)

                return {
                    "handled": True,
                    "tool": tool.name,
                    "result": result
                }

            # -----------------------------------------
            # CASE 2: structured execution
            # -----------------------------------------
            if isinstance(payload, dict):

                tool_name = payload.get("tool")
                action = payload.get("action")
                input_data = payload.get("input", {})

                tool = self.get_tool_by_name(tool_name)

                if not tool:
                    return {
                        "handled": False,
                        "tool": tool_name,
                        "result": "Tool not found"
                    }

                logger.info(f"Executing {tool_name}:{action}")

                # ACTION-FIRST EXECUTION
                if hasattr(tool, "execute_action"):
                    result = tool.execute_action(action, input_data)
                else:
                    result = tool.execute(input_data)

                return {
                    "handled": True,
                    "tool": tool_name,
                    "result": result
                }

            return {
                "handled": False,
                "tool": None,
                "result": "Invalid payload"
            }

        except Exception as e:
            logger.error(f"Tool execution error: {e}")

            return {
                "handled": True,
                "tool": None,
                "result": f"Tool Error: {str(e)}"
            }

    # =========================================================
    # LIST TOOLS
    # =========================================================

    def list_tools(self):
        return list(self.tools.keys())

    # =========================================================
    # CHECK TOOL
    # =========================================================

    def has_tool(self, name: str):
        return name in self.tools
    
