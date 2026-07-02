from src.utils.logger import setup_logger
from datetime import datetime, timedelta

logger = setup_logger(__name__)


class CalendarTool:
    """
    Simple in-memory Calendar Tool (Stage 1)
    """

    def __init__(self):
        self.name = "calendar"  
        self.events = []
        logger.info("CalendarTool initialized (local mode)")

    def create(self, query: str):
        event = {
            "title": query,
            "time": str(datetime.now() + timedelta(hours=1)),
            "raw": query
        }

        self.events.append(event)

        return {
            "status": "success",
            "message": "Event created",
            "event": event
        }

    def view(self, query: str = None):
        if not self.events:
            return {"message": "No events found"}

        return {"events": self.events}

    def delete(self, query: str = None):
        if not self.events:
            return {"message": "No events to delete"}

        removed = self.events.pop()

        return {
            "status": "deleted",
            "event": removed
        }

    def execute_action(self, action: str, query: str):
        if action == "create":
            return self.create(query)
        elif action == "view":
            return self.view(query)
        elif action == "delete":
            return self.delete(query)

        return {"error": f"Unknown action: {action}"}
