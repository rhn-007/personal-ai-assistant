"""
Task Manager - Stage 5 Agent Memory

Handles:
- Creating tasks
- Tracking active tasks
- Updating execution state
- Completing tasks
- Task history
"""


from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class TaskManager:


    def __init__(self):

        self.tasks = []

        self.counter = 1



    # =====================================================
    # CREATE TASK
    # =====================================================

    def create_task(
        self,
        goal: str
    ):


        from src.agent.task import Task


        try:


            task = Task(
                goal
            )


            # Assign ID if missing

            if not hasattr(
                task,
                "id"
            ):

                task.id = self.counter


            self.counter += 1


            if hasattr(
                task,
                "status"
            ):

                task.status = "running"



            self.tasks.append(
                task
            )


            logger.info(
                f"Task created: {task.id}"
            )


            return task



        except Exception as e:


            logger.error(
                f"Task creation failed: {e}"
            )


            return None



    # =====================================================
    # GET TASK
    # =====================================================

    def get_task(
        self,
        task_id
    ):


        for task in self.tasks:


            if getattr(
                task,
                "id",
                None
            ) == task_id:

                return task


        return None



    # =====================================================
    # UPDATE TASK
    # =====================================================

    def update_task(
        self,
        task_id,
        step,
        result
    ):


        task = self.get_task(
            task_id
        )


        if not task:

            return False



        if hasattr(
            task,
            "add_step"
        ):


            task.add_step(
                step,
                result
            )


        else:


            if not hasattr(
                task,
                "steps"
            ):

                task.steps = []


            task.steps.append(
                {
                    "step": step,
                    "result": result
                }
            )


        return True



    # =====================================================
    # COMPLETE TASK
    # =====================================================

    def complete_task(
        self,
        task_id,
        results=None
    ):


        task = self.get_task(
            task_id
        )


        if not task:

            return False



        if hasattr(
            task,
            "status"
        ):

            task.status = "completed"



        if results is not None:

            task.results = results



        logger.info(
            f"Task completed: {task_id}"
        )


        return True



    # =====================================================
    # FAIL TASK
    # =====================================================

    def fail_task(
        self,
        task_id,
        error
    ):


        task = self.get_task(
            task_id
        )


        if not task:

            return False



        task.status = "failed"

        task.error = error


        return True



    # =====================================================
    # ACTIVE TASKS
    # =====================================================

    def get_active_tasks(self):


        return [

            task

            for task in self.tasks

            if getattr(
                task,
                "status",
                ""
            ) != "completed"

        ]



    # =====================================================
    # ALL TASKS
    # =====================================================

    def get_all_tasks(self):


        output = []


        for task in self.tasks:


            if hasattr(
                task,
                "to_dict"
            ):

                output.append(
                    task.to_dict()
                )

            else:

                output.append(
                    task.__dict__
                )


        return output
