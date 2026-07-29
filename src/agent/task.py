"""
Task Object - Stage 5 Agent Core

Represents an agent task.

Handles:
- Task identity
- Goal tracking
- Execution steps
- Results
- Status management
"""


import uuid

from datetime import datetime


class Task:


    def __init__(
        self,
        goal: str
    ):


        self.id = str(
            uuid.uuid4()
        )


        self.goal = goal


        self.steps = []


        self.result = None


        self.error = None


        self.status = "pending"


        self.created_at = (
            datetime.now()
            .isoformat()
        )


        self.completed_at = None



    # =====================================================
    # ADD EXECUTION STEP
    # =====================================================

    def add_step(
        self,
        tool: str,
        input_data: str
    ):


        step = {


            "tool": tool,


            "input": input_data,


            "status": "pending",


            "output": None,


            "created_at": (
                datetime.now()
                .isoformat()
            )

        }


        self.steps.append(
            step
        )


        return step



    # =====================================================
    # UPDATE LAST STEP
    # =====================================================

    def update_last_step(
        self,
        output,
        status="completed"
    ):


        if not self.steps:

            return False


        self.steps[-1][
            "output"
        ] = output


        self.steps[-1][
            "status"
        ] = status


        return True



    # =====================================================
    # COMPLETE TASK
    # =====================================================

    def mark_done(
        self,
        result
    ):


        self.result = result


        self.status = "completed"


        self.completed_at = (
            datetime.now()
            .isoformat()
        )


    # =====================================================
    # FAIL TASK
    # =====================================================

    def mark_failed(
        self,
        error
    ):


        self.error = error


        self.status = "failed"


        self.completed_at = (
            datetime.now()
            .isoformat()
        )



    # =====================================================
    # CHECK STATUS
    # =====================================================

    def is_completed(self):

        return (
            self.status == "completed"
        )



    def is_failed(self):

        return (
            self.status == "failed"
        )



    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(self):


        return {


            "id": self.id,


            "goal": self.goal,


            "steps": self.steps,


            "result": self.result,


            "error": self.error,


            "status": self.status,


            "created_at": self.created_at,


            "completed_at": self.completed_at

        }
