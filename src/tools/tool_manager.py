from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class ToolManager:
    """
    Unified Tool Manager

    Responsibilities:
    - Register tools
    - Route queries using the Planner
    - Execute tools safely
    - Support action-based execution
    """

    def __init__(self):

        self.tools = {}

        # Planner is attached later
        self.planner = None

    # =====================================================
    # REGISTER TOOL
    # =====================================================

    def register(self, tool):

        if not tool:
            return

        if not hasattr(tool, "name"):

            logger.warning(
                "Attempted to register invalid tool."
            )

            return

        self.tools[tool.name] = tool

        logger.info(
            f"Registered tool: {tool.name}"
        )

    # =====================================================
    # SET PLANNER
    # =====================================================

    def set_planner(self, planner):

        self.planner = planner

        logger.info(
            "Planner attached to ToolManager."
        )

    # =====================================================
    # GET TOOL
    # =====================================================

    def get_tool_by_name(self, name):

        return self.get_tool(name)

    def get_tool(self, name: str):

        if not name:
            return None

        return self.tools.get(name)

    # =====================================================
    # GET PLAN
    # =====================================================

    def _get_plan(self, query):

        if not self.planner:
            return None

        try:

            plan = self.planner.create_plan(query)

            if not plan:
                return None

            # ---------------------------------------------
            # SUPPORT SINGLE DICTIONARY PLAN
            # ---------------------------------------------

            if isinstance(plan, dict):

                return plan

            # ---------------------------------------------
            # SUPPORT LIST PLAN
            # ---------------------------------------------

            if isinstance(plan, list):

                if len(plan) == 0:
                    return None

                return plan[0]

            return None

        except Exception as e:

            logger.error(
                f"Planner error: {e}"
            )

            return None

    # =====================================================
    # ROUTE QUERY TO TOOL
    # =====================================================

    def route(self, query: str):

        if not query:
            return None

        # -------------------------------------------------
        # PLANNER FIRST
        # -------------------------------------------------

        plan = self._get_plan(query)

        if plan:

            tool_name = plan.get("tool")

            tool = self.get_tool(tool_name)

            if tool:
                return tool

        # -------------------------------------------------
        # FALLBACK TO can_handle()
        # -------------------------------------------------

        for tool in self.tools.values():

            try:

                if (

                    hasattr(tool, "can_handle")

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
    # MAIN EXECUTION
    # =====================================================

    def execute(self, query: str):

        if not query:

            return {
                "handled": False,
                "tool": None,
                "result": None
            }

        # -------------------------------------------------
        # GET PLAN
        # -------------------------------------------------

        plan = self._get_plan(query)

        if plan:

            tool_name = plan.get("tool")

            action = plan.get("action")

            # ---------------------------------------------
            # GET INPUT
            # ---------------------------------------------

            tool_input = plan.get(
                "input",
                {}
            )

            # ---------------------------------------------
            # QUERY EXTRACTION
            # ---------------------------------------------

            tool_query = query

            if isinstance(tool_input, dict):

                tool_query = tool_input.get(
                    "query",
                    query
                )

            # ---------------------------------------------
            # DIRECT QUERY FROM PLAN
            # ---------------------------------------------

            if plan.get("query"):

                tool_query = plan.get(
                    "query"
                )

            tool = self.get_tool(
                tool_name
            )

            if tool:

                logger.info(
                    f"Planner selected: "
                    f"{tool_name} | "
                    f"Action: {action}"
                )

                return self.execute_by_name(

                    name=tool_name,

                    action=action,

                    query=tool_query

                )

        # -------------------------------------------------
        # FALLBACK ROUTING
        # -------------------------------------------------

        tool = self.route(query)

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

            result = tool.execute(query)

            return {

                "handled": True,

                "tool": tool.name,

                "result": result

            }

        except Exception as e:

            logger.error(

                f"Tool execution failed "
                f"({tool.name}): {e}"

            )

            return {

                "handled": True,

                "tool": tool.name,

                "result": f"Tool Error: {e}"

            }

    # =====================================================
    # ACTION-BASED EXECUTION
    # =====================================================

    def execute_by_name(

        self,

        name,

        action,

        query=None

    ):

        tool = self.get_tool_by_name(name)

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

            # ---------------------------------------------
            # ACTION-AWARE TOOL
            # ---------------------------------------------

            if hasattr(

                tool,

                "execute_action"

            ):

                result = tool.execute_action(

                    action,

                    query

                )

            # ---------------------------------------------
            # STANDARD TOOL
            # ---------------------------------------------

            else:

                result = tool.execute(query)

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

                "result": f"Tool Error: {e}"

            }

    # =====================================================
    # EXECUTE PLAN
    # =====================================================

    def execute_plan(self, plan):

        if not plan:

            return {

                "handled": False,

                "tool": None,

                "result": None

            }

        # ---------------------------------------------
        # SINGLE PLAN DICTIONARY
        # ---------------------------------------------

        if isinstance(plan, dict):

            plan = [plan]

        results = []

        for step in plan:

            tool_name = step.get("tool")

            action = step.get("action")

            tool_input = step.get(
                "input",
                {}
            )

            query = None

            if isinstance(tool_input, dict):

                query = tool_input.get(
                    "query"
                )

            if not query:

                query = step.get(
                    "query"
                )

            result = self.execute_by_name(

                name=tool_name,

                action=action,

                query=query

            )

            results.append(result)

        return results

    # =====================================================
    # LIST TOOLS
    # =====================================================

    def list_tools(self):

        return list(
            self.tools.keys()
        )
