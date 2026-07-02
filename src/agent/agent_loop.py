from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager


class AgentLoop:
    """
    Stage 6 Agent Loop (App-Integration Ready)

    Features:
    - structured plan execution
    - action-based tool calls
    - safe normalization
    - multi-app ready architecture
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

        task = self.task_manager.create_task(user_input)
        task_id = task.get("id") if isinstance(task, dict) else getattr(task, "id", None)

        plan = self.planner.create_plan(user_input)

        if not plan:
            return None

        results = []

        for step in plan:

            if not isinstance(step, dict):
                continue

            tool_name = step.get("tool")
            action = step.get("action", "default")
            payload = step.get("input", {})

            if not tool_name:
                continue

            tool = self.tool_manager.get_tool_by_name(tool_name)

            if not tool:
                continue

            try:
                # =================================================
                # ACTION-FIRST EXECUTION (PRIMARY)
                # =================================================
                output = None

                if hasattr(tool, "execute_action"):
                    output = tool.execute_action(action, payload)

                elif hasattr(tool, "execute"):
                    output = tool.execute({
                        "action": action,
                        "input": payload
                    })

                if output is None:
                    continue

                normalized = self._normalize(output)
                results.append(normalized)

                # =================================================
                # TASK TRACKING
                # =================================================
                if task_id:
                    try:
                        self.task_manager.update_task(task_id, step, normalized)
                    except Exception:
                        pass

            except Exception as e:

                error_msg = f"{tool_name} failed: {str(e)}"
                results.append(error_msg)

                if task_id:
                    try:
                        self.task_manager.update_task(task_id, step, error_msg)
                    except Exception:
                        pass

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
        Converts all tool outputs into safe strings
        """

        if output is None:
            return ""

        if isinstance(output, str):
            return output

        if isinstance(output, dict):

            # common structured tool responses
            if "result" in output:
                return str(output["result"])

            if "message" in output:
                return str(output["message"])

            if "data" in output:
                return str(output["data"])

            return str(output)

        if isinstance(output, list):
            return "\n".join(str(i) for i in output)

        return str(output)
