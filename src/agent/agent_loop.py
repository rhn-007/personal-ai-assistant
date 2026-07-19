from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager


class AgentLoop:
    """
    Stage 6 Agent Loop (Fully App-Integration Ready)

    - Uses structured planner output
    - Supports tool + action execution
    - Uses execute_by_name() safely
    - Fully automation-ready (Jarvis-style)
    """

    def __init__(self, tool_manager: ToolManager, planner: Planner = None, task_manager: TaskManager = None):

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
        print(f"DEBUG PLAN: {plan}")

        if not plan or not isinstance(plan, list):
            return None

        results = []

        # 3. EXECUTE PLAN
        for step in plan:

            if not isinstance(step, dict):
                continue

            tool_name = step.get("tool")
            action = step.get("action", "default")
            query = step.get("input", user_input)

            if not tool_name:
                continue

            # =================================================
            # TOOL EXECUTION (FIXED)
            # =================================================

            try:
                output = self.tool_manager.execute_by_name(
                    tool_name,
                    action,
                    query
                )

                if not output:
                    continue

                result = output.get("result")

                if result:
                    results.append(str(result))

                # =================================================
                # TASK UPDATE
                # =================================================
                if task_id:
                    try:
                        self.task_manager.update_task(task_id, step, result)
                    except Exception:
                        pass

            except Exception as e:
                if task_id:
                    try:
                        self.task_manager.update_task(task_id, step, f"ERROR: {str(e)}")
                    except Exception:
                        pass

        # 4. COMPLETE TASK
        if task_id:
            try:
                self.task_manager.complete_task(task_id, results)
            except Exception:
                pass

        return "\n".join(results) if results else None
