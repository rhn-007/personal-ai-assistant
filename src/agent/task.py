"""
Task Object - Stage 5 Agent Core
"""

import uuid
from datetime import datetime


class Task:

    def __init__(self, goal: str):
        self.id = str(uuid.uuid4())
        self.goal = goal
        self.steps = []
        self.result = None
        self.status = "pending"
        self.created_at = datetime.now().isoformat()

    def add_step(self, tool: str, input_data: str):
        self.steps.append({
            "tool": tool,
            "input": input_data,
            "status": "pending",
            "output": None
        })

    def mark_done(self, result):
        self.result = result
        self.status = "completed"

    def to_dict(self):
        return {
            "id": self.id,
            "goal": self.goal,
            "steps": self.steps,
            "result": self.result,
            "status": self.status
        }
