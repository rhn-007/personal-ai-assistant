from src.planner.planner import Planner
from src.tools.tool_manager import ToolManager
from src.agent.task_manager import TaskManager

class AgentLoop:
"""
Stage 6 Agent Loop

```
- Uses structured planner output
- Supports action-based tool execution
- Supports legacy execute() tools
- Handles task tracking
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

def run(self, user_input: str):

    if not user_input or not isinstance(user_input, str):
        return None

    # =====================================================
    # 1. CREATE TASK
    # =====================================================

    task = self.task_manager.create_task(user_input)

    task_id = (
        task.get("id")
        if isinstance(task, dict)
        else getattr(task, "id", None)
    )

    # =====================================================
    # 2. CREATE PLAN
    # =====================================================

    plan = self.planner.create_plan(user_input)

    print(f"DEBUG PLAN: {plan}")

    if not plan or not isinstance(plan, list):
        return None

    results = []

    # =====================================================
    # 3. EXECUTE PLAN
    # =====================================================

    for step in plan:

        if not isinstance(step, dict):
            continue

        tool_name = step.get("tool")
        action = step.get("action", "default")
        tool_input = step.get("input", user_input)

        if not tool_name:
            continue

        # Normalize input
        if isinstance(tool_input, dict):

            query = (
                tool_input.get("raw")
                or tool_input.get("query")
                or user_input
            )

        else:
            query = tool_input

        try:

            # =================================================
            # TOOL LOOKUP
            # =================================================

            tool = self.tool_manager.get_tool_by_name(tool_name)

            if not tool:

                result = f"Tool '{tool_name}' not found."

            # =================================================
            # ACTION-AWARE TOOL
            # =================================================

            elif hasattr(tool, "execute_action"):

                result = tool.execute_action(
                    action,
                    query
                )

            # =================================================
            # STANDARD TOOL
            # =================================================

            elif hasattr(tool, "execute"):

                result = tool.execute(query)

            else:

                result = (
                    f"Tool '{tool_name}' does not have "
                    f"an execute() or execute_action() method."
                )

            # =================================================
            # NORMALIZE RESULT
            # =================================================

            normalized_result = self._normalize(result)

            if normalized_result:

                results.append(normalized_result)

            # =================================================
            # UPDATE TASK
            # =================================================

            if task_id:

                try:

                    self.task_manager.update_task(
                        task_id,
                        step,
                        normalized_result
                    )

                except Exception:
                    pass

        except Exception as e:

            error_message = f"Tool Error: {str(e)}"

            if task_id:

                try:

                    self.task_manager.update_task(
                        task_id,
                        step,
                        error_message
                    )

                except Exception:
                    pass

    # =====================================================
    # 4. COMPLETE TASK
    # =====================================================

    if task_id:

        try:

            self.task_manager.complete_task(
                task_id,
                results
            )

        except Exception:
            pass

    # =====================================================
    # 5. RETURN RESULT
    # =====================================================

    return "\n".join(results) if results else None

# =========================================================
# NORMALIZATION
# =========================================================

def _normalize(self, output):

    if output is None:
        return ""

    if isinstance(output, str):
        return output

    if isinstance(output, dict):

        if "result" in output:
            return str(output["result"])

        if "message" in output:
            return str(output["message"])

        return str(output)

    if isinstance(output, list):

        return "\n".join(
            str(item)
            for item in output
        )

    return str(output)
```
