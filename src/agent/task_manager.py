"""
Task Manager - Stage 5 Agent Memory
"""

class TaskManager:

    def __init__(self):
        self.tasks = []

    def create_task(self, goal: str):
        from src.agent.task import Task

        task = Task(goal)
        self.tasks.append(task)
        return task

    def get_active_tasks(self):
        return [t for t in self.tasks if t.status != "completed"]

    def get_all_tasks(self):
        return [t.to_dict() for t in self.tasks]
