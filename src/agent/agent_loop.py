"""
NEXUS Agent Loop

Runs tools safely without blocking UI.
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError

from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager

from src.utils.logger import setup_logger

from src.ui.status import set_status, clear_status


logger = setup_logger(__name__)


executor = ThreadPoolExecutor(
    max_workers=4
)


class AgentLoop:


    def __init__(
        self,
        tool_manager: ToolManager,
        planner=None,
        task_manager=None
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


    # ==========================================
    # RUN
    # ==========================================

    def run(self, user_input):

        if not user_input:
            return None


        try:

            set_status(
                "Planning task"
            )


            task = self.task_manager.create_task(
                user_input
            )


            task_id = getattr(
                task,
                "id",
                None
            )


            plan = self.planner.create_plan(
                user_input
            )


            if not plan:

                clear_status()

                return None



            if isinstance(plan, dict):

                plan=[plan]


            results=[]


            for step in plan:


                tool_name = step.get(
                    "tool"
                )


                action = step.get(
                    "action",
                    "default"
                )


                query = step.get(
                    "query",
                    user_input
                )


                if not tool_name:
                    continue


                set_status(
                    f"Running {tool_name}"
                )


                future = executor.submit(
                    self._execute_tool,
                    tool_name,
                    action,
                    query
                )


                try:

                    result = future.result(
                        timeout=60
                    )


                except TimeoutError:

                    result = (
                        f"{tool_name} timed out."
                    )


                except Exception as e:

                    result = (
                        f"Tool error: {e}"
                    )


                if result:

                    results.append(
                        str(result)
                    )


            clear_status()


            if not results:

                return None


            return "\n".join(results)



        except Exception as e:

            logger.error(
                f"Agent failed: {e}"
            )

            clear_status()

            return None



    # ==========================================
    # TOOL EXECUTION
    # ==========================================

    def _execute_tool(
        self,
        tool_name,
        action,
        query
    ):


        tool = (
            self.tool_manager
            .get_tool_by_name(
                tool_name
            )
        )


        if not tool:

            return (
                f"Tool {tool_name} not found."
            )


        if hasattr(
            tool,
            "execute_action"
        ):

            return tool.execute_action(
                action,
                query
            )


        if hasattr(
            tool,
            "execute"
        ):

            return tool.execute(
                query
            )


        return (
            "Tool cannot execute."
        )
