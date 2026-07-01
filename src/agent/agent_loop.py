from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager


class AgentLoop:
    """
    Stage 5 Agent Loop (FULLY FIXED)
    - Works with structured tool outputs
    - Safe execution
    - No type mismatches
    """

    def __init__(self, tool_manager: ToolManager, planner=None, task_manager=None):
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

        if not plan or not isinstance(plan, list):
            return None

        results = []

        for step in plan:

            if not isinstance(step, dict):
                continue

            tool_name = step.get("tool")
            query = step.get("input", user_input)

            tool = self.tool_manager.get_tool(tool_name)

            if not tool:
                continue

            try:
                output = tool.execute(query)

                # =================================================
                # SAFE UNWRAP (CRITICAL FIX)
                # =================================================

                if isinstance(output, dict):
                    data = output.get("data")
                    tool_type = output.get("type")

                    # convert list/dict into safe text
                    if tool_type == "list" and isinstance(data, list):
                        cleaned = "\n".join(
                            str(item.get("subject", item)) if isinstance(item, dict) else str(item)
                            for item in data
                        )
                        results.append(cleaned)
                    else:
                        results.append(str(data))

                else:
                    results.append(str(output))

                # update task safely
                if task_id:
                    try:
                        self.task_manager.update_task(task_id, step, str(output))
                    except:
                        pass

            except Exception as e:
                if task_id:
                    try:
                        self.task_manager.update_task(task_id, step, f"ERROR: {e}")
                    except:
                        pass

        if task_id:
            try:
                self.task_manager.complete_task(task_id, results)
            except:
                pass

        return "\n".join(results) if results else None
