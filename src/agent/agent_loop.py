from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager


class AgentLoop:
    """
    Stage 6 Agent Loop (App-Integration Ready)

    Supports:
    - tool routing
    - action-based execution
    - structured planner output
    - safe execution
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
    # MAIN LOOP
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

        # 3. EXECUTE PLAN STEPS
        for step in plan:

            if not isinstance(step, dict):
                continue

            tool_name = step.get("tool")
            action = step.get("action", "default")
            query = step.get("input", user_input)

            if not tool_name:
                continue

            # =================================================
            # TOOL LOOKUP (UPDATED API)
            # =================================================
            tool = self.tool_manager.get_tool_by_name(tool_name)

            if not tool:
                continue

            try:
                # =================================================
                # TOOL EXECUTION (ACTION-AWARE)
                # =================================================
                if hasattr(tool, "execute_action"):
                    output = tool.execute_action(action, query)
                else:
                    output = tool.execute(query)

                if output is None:
                    continue

                normalized_output = self._normalize(output)
                results.append(normalized_output)

                # =================================================
                # TASK UPDATE
                # =================================================
                if task_id:
                    try:
                        self.task_manager.update_task(
                            task_id,
                            step,
                            normalized_output
                        )
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
    # NORMALIZATION LAYER
    # =========================================================

    def _normalize(self, output):
        """
        Convert all tool outputs into safe strings
        """

        if output is None:
            return ""

        if isinstance(output, str):
            return output

        if isinstance(output, dict):
            # common patterns
            if "result" in output:
                return str(output["result"])
            if "message" in output:
                return str(output["message"])
            return str(output)

        if isinstance(output, list):
            return "\n".join(str(i) for i in output)

        return str(output)
