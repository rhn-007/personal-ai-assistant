from src.utils.logger import setup_logger
from datetime import datetime, timedelta

logger = setup_logger(__name__)


class CalendarTool:
    """
    Simple Calendar Tool (Stage 1 - Local / Mock Mode)

    Later upgrade: Google Calendar API integration
    """

    def __init__(self):
        self.events = []  # in-memory storage (for now)
        logger.info("CalendarTool initialized (local mode)")

    # =========================================================
    # CREATE EVENT
    # =========================================================
    def create_event(self, query: str):
        """
        Very simple parser (Stage 1)
        Example:
        "meeting tomorrow at 5pm"
        """

        event = {
            "title": query,
            "time": str(datetime.now() + timedelta(hours=1)),
            "raw": query
        }

        self.events.append(event)

        return {
            "status": "success",
            "message": "Event added to calendar",
            "event": event
        }

    # =========================================================
    # VIEW EVENTS
    # =========================================================
    def view_events(self, query: str=None):
        if not self.events:
            return {"message": "No events found"}

        return {
            "events": self.events
        }

    # =========================================================
    # DELETE LAST EVENT (simple control)
    # =========================================================
    def delete_last(self, query: str=None):
        if not self.events:
            return {"message": "No events to delete"}

        removed = self.events.pop()

        return {
            "status": "deleted",
            "event": removed
        }

    # =========================================================
    # ROUTER (IMPORTANT for Agent Loop compatibility)
    # =========================================================
    def execute_action(self, action: str, query: str):
        if action in ["create", "create_event", "add"]:
            return self.create_event(query)

        elif action in ["view", "list", "get"]:
            return self.view_events(query)

        elif action in ["delete", "remove"]:
            return self.delete_last(query)

        return {"error": f"Unknown action: {action}"}
