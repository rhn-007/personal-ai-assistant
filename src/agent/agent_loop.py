from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager


class AgentLoop:
    """
    Stage 5 Agent Loop:
    - Plans tasks
    - Executes tools step-by-step
    - Tracks execution state safely
    """

    def __init__(
        self,
        tool_manager: ToolManager,
        planner: Planner = None,
        task_manager: TaskManager = None
    ):

        self.tool_manager = tool_manager

        # use external or fallback
        self.planner = planner if planner else Planner(tool_manager)
        self.task_manager = task_manager if task_manager else TaskManager()

    # =========================================================
    # MAIN LOOP
    # =========================================================

    def run(self, user_input: str):

        # 1. CREATE TASK
        task = self.task_manager.create_task(user_input)

        task_id = task.get("id") if isinstance(task, dict) else getattr(task, "id", None)

        # 2. CREATE PLAN (FIXED)
        plan = self.planner.create_plan(user_input)

        if not plan:
            return "No plan generated"

        results = []

        # 3. EXECUTE PLAN
        for step in plan:

            tool_name = step.get("tool")
            query = step.get("input", user_input)

            # safe tool lookup
            tool = self.tool_manager.get_tool(tool_name) if tool_name else None

            if not tool:
                continue

            try:
                output = tool.execute(query)

                if output is None:
                    continue

                results.append(output)

                # update task safely
                if task_id:
                    try:
                        self.task_manager.update_task(task_id, step, output)
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

        return "\n".join([r for r in results if r])
