from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class ToolManager:
    """
    Unified Tool Manager

    - Register tools
    - Get tools by name
    - Route queries to tools
    - Execute tools safely
    - Support action-based execution
    """

    def __init__(self):

        self.tools = {}

    # =====================================================
    # REGISTER TOOL
    # =====================================================

    def register(self, tool):

        self.tools[tool.name] = tool

        logger.info(
            f"Registered tool: {tool.name}"
        )

    # =====================================================
    # GET TOOL
    # =====================================================

    def get_tool_by_name(self, name):

        return self.get_tool(
            name
        )

    def get_tool(self, name: str):

        return self.tools.get(
            name
        )

    # =====================================================
    # ROUTE QUERY TO TOOL
    # =====================================================

    def route(self, query: str):

        for tool in self.tools.values():

            try:

                if (
                    hasattr(
                        tool,
                        "can_handle"
                    )
                    and tool.can_handle(query)
                ):

                    return tool

            except Exception as e:

                logger.error(
                    f"Tool check error "
                    f"({tool.name}): {e}"
                )

        return None

    # =====================================================
    # NORMAL EXECUTION
    # =====================================================

    def execute(self, query: str):

        tool = self.route(
            query
        )

        if not tool:

            return {

                "handled": False,

                "tool": None,

                "result": None

            }

        try:

            logger.info(
                f"Executing tool: "
                f"{tool.name}"
            )

            result = tool.execute(
                query
            )

            return {

                "handled": True,

                "tool": tool.name,

                "result": result

            }

        except Exception as e:

            logger.error(
                f"Tool execution failed: {e}"
            )

            return {

                "handled": True,

                "tool": tool.name,

                "result":
                    f"Tool Error: {e}"

            }

    # =====================================================
    # ACTION-BASED EXECUTION
    # =====================================================

    def execute_by_name(
        self,
        name,
        action,
        query
    ):

        tool = self.get_tool_by_name(
            name
        )

        if not tool:

            logger.warning(
                f"Tool not found: {name}"
            )

            return {

                "handled": False,

                "tool": name,

                "result": None

            }

        try:

            logger.info(
                f"Executing tool: "
                f"{name} | "
                f"Action: {action}"
            )

            # -----------------------------------------
            # ACTION-AWARE TOOL
            # -----------------------------------------

            if hasattr(
                tool,
                "execute_action"
            ):

                result = tool.execute_action(

                    action,

                    query

                )

            # -----------------------------------------
            # STANDARD TOOL
            # -----------------------------------------

            else:

                result = tool.execute(
                    query
                )

            return {

                "handled": True,

                "tool": name,

                "result": result

            }

        except Exception as e:

            logger.error(

                f"Tool execution failed "
                f"({name}): {e}"

            )

            return {

                "handled": True,

                "tool": name,

                "result":
                    f"Tool Error: {e}"

            }

    # =====================================================
    # LIST TOOLS
    # =====================================================

    def list_tools(self):

        return list(
            self.tools.keys()
        )
