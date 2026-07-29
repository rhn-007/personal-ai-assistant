from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class ToolManager:
    """
    NEXUS Tool Manager

    Responsibilities:
    - Register tools
    - Use Planner for routing
    - Execute tools safely
    - Support action-based tools
    """


    def __init__(self):

        self.tools = {}

        self.planner = None



    # =====================================================
    # REGISTER TOOL
    # =====================================================

    def register(self, tool):

        if not tool:
            return


        if not hasattr(tool, "name"):

            logger.warning(
                "Invalid tool registration attempt."
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
            "Planner attached."
        )



    # =====================================================
    # GET TOOL
    # =====================================================

    def get_tool(self, name):

        if not name:
            return None


        return self.tools.get(name)



    def get_tool_by_name(self, name):

        return self.get_tool(name)



    # =====================================================
    # GET PLAN
    # =====================================================

    def _get_plan(self, query):

        if not self.planner:
            return None


        try:

            plan = self.planner.create_plan(
                query
            )


            if not plan:
                return None


            if isinstance(plan, dict):

                return plan


            if isinstance(plan, list):

                if len(plan) > 0:

                    return plan[0]


            return None


        except Exception as e:

            logger.error(
                f"Planner error: {e}"
            )

            return None



    # =====================================================
    # MAIN EXECUTION
    # =====================================================

    def execute(self, query):

        if not query:

            return {
                "handled": False,
                "tool": None,
                "result": None
            }



        plan = self._get_plan(
            query
        )


        if not plan:

            return {
                "handled": False,
                "tool": None,
                "result": None
            }



        tool_name = plan.get(
            "tool"
        )


        action = plan.get(
            "action",
            "default"
        )


        if not tool_name:

            return {
                "handled": False,
                "tool": None,
                "result": None
            }



        tool = self.get_tool(
            tool_name
        )


        if not tool:

            logger.warning(
                f"Tool not found: {tool_name}"
            )


            return {
                "handled": True,
                "tool": tool_name,
                "result": (
                    f"Tool '{tool_name}' "
                    "not found."
                )
            }



        # Extract query

        tool_query = query


        if plan.get("query"):

            tool_query = plan.get(
                "query"
            )


        elif isinstance(
            plan.get("input"),
            dict
        ):

            tool_query = (

                plan["input"].get(
                    "query"
                )

                or query

            )



        return self.execute_by_name(

            tool_name,

            action,

            tool_query

        )



    # =====================================================
    # ACTION EXECUTION
    # =====================================================

    def execute_by_name(
        self,
        name,
        action,
        query=None
    ):


        tool = self.get_tool(
            name
        )


        if not tool:

            return {

                "handled": True,

                "tool": name,

                "result": (
                    f"Tool '{name}' "
                    "not found."
                )

            }



        try:

            logger.info(
                f"Executing tool: {name} | Action: {action}"
            )


            if hasattr(
                tool,
                "execute_action"
            ):

                result = tool.execute_action(

                    action,

                    query

                )


            elif hasattr(
                tool,
                "execute"
            ):

                result = tool.execute(
                    query
                )


            else:

                result = (
                    f"Tool '{name}' "
                    "cannot execute."
                )



            logger.info(
                f"Tool result: {result}"
            )



            return {

                "handled": True,

                "tool": name,

                "result": result

            }



        except Exception as e:


            logger.error(
                f"Tool execution failed ({name}): {e}"
            )


            return {

                "handled": True,

                "tool": name,

                "result": (
                    f"Tool Error: {e}"
                )

            }



    # =====================================================
    # OPTIONAL FALLBACK ROUTING
    # =====================================================

    def route(self, query):

        if not query:
            return None


        for tool in self.tools.values():

            try:

                if hasattr(
                    tool,
                    "can_handle"
                ):

                    if tool.can_handle(query):

                        return tool


            except Exception as e:

                logger.error(
                    f"Tool detection error: {e}"
                )


        return None



    # =====================================================
    # EXECUTE MULTIPLE STEPS
    # =====================================================

    def execute_plan(self, plan):

        if not plan:

            return []



        if isinstance(
            plan,
            dict
        ):

            plan = [plan]



        results = []


        for step in plan:


            if not isinstance(
                step,
                dict
            ):

                continue



            result = self.execute_by_name(

                step.get("tool"),

                step.get(
                    "action",
                    "default"
                ),

                step.get(
                    "query"
                )

            )


            results.append(
                result
            )



        return results



    # =====================================================
    # LIST TOOLS
    # =====================================================

    def list_tools(self):

        return list(
            self.tools.keys()
        )
