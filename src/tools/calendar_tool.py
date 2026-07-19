from src.integrations.calendar import CalendarIntegration
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class CalendarTool:

    def __init__(self):

        self.name = "calendar"

        self.calendar = CalendarIntegration()

        logger.info(
            "CalendarTool initialized"
        )

    # =====================================================
    # CREATE EVENT
    # =====================================================

    def create_event(
        self,
        query
    ):

        return (
            "Calendar event creation is ready, "
            "but natural-language date parsing "
            "will be added next."
        )

    # =====================================================
    # SHOW EVENTS
    # =====================================================

    def show_events(self):

        events = (
            self.calendar.get_all_events()
        )

        if not events:

            return (
                "You have no calendar events."
            )

        output = [
            "📅 Your Calendar:"
        ]

        for event in events:

            event_id = event[0]

            title = event[1]

            event_date = event[3]

            event_time = event[4]

            output.append(
                f"{event_id}. "
                f"{title} — "
                f"{event_date} "
                f"{event_time or ''}"
            )

        return "\n".join(output)

    # =====================================================
    # EXECUTE ACTION
    # =====================================================

    def execute_action(
        self,
        action,
        query=None
    ):

        if action == "create":

            return self.create_event(
                query
            )

        if action in [
            "list",
            "show"
        ]:

            return self.show_events()

        return (
            f"Unknown calendar action: "
            f"{action}"
        )

    # =====================================================
    # TOOL MANAGER COMPATIBILITY
    # =====================================================

    def execute(self, query):

        return self.create_event(
            query
        )
