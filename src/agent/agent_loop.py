from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager


class AgentLoop:

    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager
        self.planner = Planner(tool_manager)
        self.task_manager = TaskManager()

    def run(self, user_input: str):

        # 1. Create task
        task = self.task_manager.create_task(user_input)

        # 2. Create plan
        plan = self.planner.create_plan(user_input)

        if not plan:
            return "No plan generated"

        results = []

        # 3. Execute plan step-by-step
        for step in plan:

            tool_name = step.get("tool")
            query = step.get("input", user_input)

            tool = self.tool_manager.get_tool(query)

            if tool:
                output = tool.execute(query)
                results.append(output)

                self.task_manager.update_task(task["id"], step, output)

        # 4. Finish task
        self.task_manager.complete_task(task["id"], results)

        return "\n".join(results)
