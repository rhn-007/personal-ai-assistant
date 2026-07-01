from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager


class AgentLoop:
    """
    Fixed Stage 5 Agent Loop

    Responsibilities:
    - Execute structured plans
    - Use ToolManager correctly
    - Normalize tool outputs
    - Keep execution safe
    """

    def __init__(
        self,
        tool_manager: ToolManager,
        planner: Planner = None,
        task_manager: TaskManager = None
    ):

        self.tool_manager = tool_manager
        self.planner = planner if planner else Planner(tool_manager)
        self.task_manager = task_manager if task_manager else TaskManager()

    # =========================================================
    # MAIN EXECUTION LOOP
    # =========================================================

    def run(self, user_input: str):

        # 1. CREATE TASK
        task = self.task_manager.create_task(user_input)
        task_id = task.get("id") if isinstance(task, dict) else getattr(task, "id", None)

        # 2. CREATE PLAN
        plan = self.planner.create_plan(user_input)

        if not plan or not isinstance(plan, list):
            return None

        results = []

        # 3. EXECUTE PLAN
        for step in plan:

            if not isinstance(step, dict):
                continue

            tool_name = step.get("tool")
            query = step.get("input", user_input)

            if not tool_name:
                continue

            # ✔ FIX: correct ToolManager API
            tool = self.tool_manager.get_tool_by_name(tool_name)

            if not tool:
                continue

            try:
                output = tool.execute(query)

                if output is None:
                    continue

                normalized_output = self._normalize(output)
                results.append(normalized_output)

                # update task safely
                if task_id:
                    try:
                        self.task_manager.update_task(task_id, step, normalized_output)
                    except Exception:
                        pass

            except Exception as e:
                if task_id:
                    try:
                        self.task_manager.update_task(
                            task_id,
                            step,
                            f"ERROR: {str(e)}"
                        )
                    except Exception:
                        pass

        # 4. COMPLETE TASK
        if task_id:
            try:
                self.task_manager.complete_task(task_id, results)
            except Exception:
                pass

        return "\n".join(results) if results else None

    # =========================================================
    # OUTPUT NORMALIZATION (IMPORTANT FIX)
    # =========================================================

    def _normalize(self, output):
        """
        Ensures all tool outputs become safe strings
        """

        if output is None:
            return ""

        if isinstance(output, str):
            return output

        if isinstance(output, dict):
            # try common fields first
            if "result" in output:
                return str(output["result"])
            return str(output)

        if isinstance(output, list):
            return "\n".join(str(i) for i in output)

        return str(output)
