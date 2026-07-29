"""
NEXUS Agent Loop

Handles:
- Complex task execution
- Planner-based workflows
- Multi-step tool execution
- Task tracking
- Result normalization

Simple commands should be handled by ToolManager first.
AgentLoop is used as a secondary execution layer.
"""


from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager

from src.utils.logger import setup_logger

from src.ui.status import set_status, clear_status


logger = setup_logger(__name__)


class AgentLoop:


    def __init__(
        self,
        tool_manager: ToolManager,
        planner: Planner = None,
        task_manager: TaskManager = None
    ):


        self.tool_manager = tool_manager


        self.planner = (

            planner

            if planner

            else Planner(tool_manager)

        )


        self.task_manager = (

            task_manager

            if task_manager

            else TaskManager()

        )



    # =====================================================
    # RUN AGENT
    # =====================================================

    def run(
        self,
        user_input: str
    ):


        if not user_input:

            return None


        if not isinstance(
            user_input,
            str
        ):

            return None



        try:


            set_status(
                "Planning task"
            )


            # =================================================
            # CREATE TASK
            # =================================================

            task = (

                self.task_manager.create_task(
                    user_input
                )

            )


            task_id = None


            if isinstance(
                task,
                dict
            ):

                task_id = task.get(
                    "id"
                )

            else:

                task_id = getattr(
                    task,
                    "id",
                    None
                )



            # =================================================
            # CREATE PLAN
            # =================================================

            plan = (

                self.planner.create_plan(
                    user_input
                )

            )


            logger.info(
                f"Agent plan: {plan}"
            )



            if not plan:

                clear_status()

                return None



            # =================================================
            # NORMALIZE PLAN
            # =================================================

            if isinstance(
                plan,
                dict
            ):

                plan = [
                    plan
                ]


            if not isinstance(
                plan,
                list
            ):

                clear_status()

                return None



            results = []



            # =================================================
            # EXECUTE STEPS
            # =================================================

            for step in plan:


                if not isinstance(
                    step,
                    dict
                ):

                    continue



                tool_name = step.get(
                    "tool"
                )


                action = step.get(
                    "action",
                    "default"
                )



                if not tool_name:

                    continue



                query = self._extract_query(
                    step,
                    user_input
                )



                set_status(
                    "Running tools"
                )



                try:


                    tool = (

                        self.tool_manager
                        .get_tool_by_name(
                            tool_name
                        )

                    )



                    if not tool:


                        result = (

                            f"Tool '{tool_name}' "
                            "not found."

                        )



                    elif hasattr(
                        tool,
                        "execute_action"
                    ):


                        result = (

                            tool.execute_action(
                                action,
                                query
                            )

                        )



                    elif hasattr(
                        tool,
                        "execute"
                    ):


                        result = (

                            tool.execute(
                                query
                            )

                        )



                    else:


                        result = (

                            f"Tool '{tool_name}' "
                            "cannot execute."

                        )



                    normalized = (

                        self._normalize(
                            result
                        )

                    )



                    if normalized:


                        results.append(
                            normalized
                        )



                    # Update task

                    if task_id:


                        try:


                            self.task_manager.update_task(

                                task_id,

                                step,

                                normalized

                            )


                        except Exception as e:


                            logger.warning(

                                f"Task update failed: {e}"

                            )



                except Exception as e:


                    logger.error(

                        f"Tool execution error "
                        f"({tool_name}): {e}"

                    )


                    results.append(

                        f"Tool Error: {e}"

                    )



            # =================================================
            # COMPLETE TASK
            # =================================================


            if task_id:


                try:


                    self.task_manager.complete_task(

                        task_id,

                        results

                    )


                except Exception as e:


                    logger.warning(

                        f"Task completion failed: {e}"

                    )



            clear_status()



            if not results:

                return None



            return "\n".join(
                results
            )



        except Exception as e:


            clear_status()


            logger.error(

                f"Agent loop failed: {e}"

            )


            return None



    # =====================================================
    # QUERY EXTRACTION
    # =====================================================

    def _extract_query(
        self,
        step,
        fallback
    ):


        tool_input = step.get(
            "input"
        )


        if isinstance(
            tool_input,
            dict
        ):


            return (

                tool_input.get(
                    "query"
                )

                or

                tool_input.get(
                    "raw"
                )

                or

                fallback

            )



        if isinstance(
            tool_input,
            str
        ):

            return tool_input



        return step.get(
            "query",
            fallback
        )



    # =====================================================
    # NORMALIZE OUTPUT
    # =====================================================

    def _normalize(
        self,
        output
    ):


        if output is None:

            return ""



        if isinstance(
            output,
            str
        ):

            return output



        if isinstance(
            output,
            dict
        ):


            if "result" in output:

                return str(
                    output["result"]
                )


            if "message" in output:

                return str(
                    output["message"]
                )


            return str(output)



        if isinstance(
            output,
            list
        ):


            return "\n".join(

                str(item)

                for item in output

            )


        return str(output)
