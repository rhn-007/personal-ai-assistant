import re
from datetime import datetime, timedelta

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
    # PARSE NATURAL LANGUAGE EVENT
    # =====================================================

    def parse_event(self, query):

        text = query.lower().strip()

        # -----------------------------
        # EXTRACT TIME
        # -----------------------------

        time_match = re.search(
            r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b",
            text
        )

        event_time = None

        if time_match:

            hour = int(
                time_match.group(1)
            )

            minute = (
                int(time_match.group(2))
                if time_match.group(2)
                else 0
            )

            period = time_match.group(3)

            if period == "pm" and hour != 12:

                hour += 12

            elif period == "am" and hour == 12:

                hour = 0

            event_time = (
                f"{hour:02d}:{minute:02d}"
            )

        # -----------------------------
        # EXTRACT DATE
        # -----------------------------

        today = datetime.now().date()

        if (
            "tomorrow" in text
            or "tmrw" in text
        ):

            event_date = (
                today + timedelta(days=1)
            ).isoformat()

        elif "today" in text:

            event_date = (
                today.isoformat()
            )

        else:

            event_date = (
                today.isoformat()
            )

        # -----------------------------
        # CLEAN TITLE
        # -----------------------------

        title = text

        phrases_to_remove = [

            "set a reminder for",

            "set a reminder to",

            "remind me to",

            "remind me about",

            "schedule",

            "create an event for",

            "create a reminder for",

            "at ",

            "today",

            "tomorrow",

            "tmrw",

            "for"
        ]

        for phrase in phrases_to_remove:

            title = title.replace(
                phrase,
                ""
            )

        # -----------------------------
        # REMOVE TIME
        # -----------------------------

        if time_match:

            title = title.replace(
                time_match.group(0),
                ""
            )

        # -----------------------------
        # CLEAN EXTRA SPACES
        # -----------------------------

        title = re.sub(
            r"\s+",
            " ",
            title
        ).strip()

        if not title:

            title = "Reminder"

        return {

            "title": title.title(),

            "date": event_date,

            "time": event_time

        }

    # =====================================================
    # CREATE EVENT
    # =====================================================

    def create_event(self, query):

        if not query:

            return (
                "I need to know what you want "
                "to schedule."
            )

        event = self.parse_event(
            query
        )

        created = self.calendar.create_event(

            title=event["title"],

            event_date=event["date"],

            event_time=event["time"]

        )

        return (

            f"📅 Reminder created!\n"

            f"Event: {created['title']}\n"

            f"Date: {created['date']}\n"

            f"Time: "
            f"{created['time'] or 'Any time'}"

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

        return "\n".join(
            output
        )

    # =====================================================
    # EXTRACT DELETE TITLE
    # =====================================================

    def extract_delete_title(self, query):

        text = query.lower().strip()

        phrases_to_remove = [

            "delete reminder for",

            "delete event for",
    
            "delete appointment for",
    
            "remove reminder for",
    
            "remove event for",
    
            "remove appointment for",
    
            "cancel reminder for",
    
            "cancel event for",
    
            "cancel appointment for",
    
            "delete",
    
            "remove",
    
            "cancel",
    
            "reminder",
    
            "event",
    
            "appointment",
    
            "the",
    
            "my",
    
            "this",
    
            "for"
        ]

        title = text

        for phrase in phrases_to_remove:

            title = title.replace(
                phrase,
                ""
            )

        title = re.sub(
            r"\s+",
            " ",
            title
        ).strip()

        return title

    # =====================================================
    # DELETE EVENT
    # =====================================================

    def delete_event(self, query=None):

        delete_title = None

        if query:

            delete_title = (
                self.extract_delete_title(
                    query
                )
            )

        # ---------------------------------
        # DELETE SPECIFIC EVENT
        # ---------------------------------

        if delete_title:

            event = (
                self.calendar.delete_event_by_title(
                    delete_title
                )
            )

            if not event:

                return (
                    f"❌ Could not find an event "
                    f"matching '{delete_title}'."
                )

            return (

                f"🗑️ Deleted event: "
                f"{event['title']}"

            )

        # ---------------------------------
        # DELETE LATEST EVENT
        # ---------------------------------

        event = (
            self.calendar.delete_latest_event()
        )

        if not event:

            return (
                "There are no events to delete."
            )

        return (

            f"🗑️ Deleted event: "
            f"{event['title']}"

        )

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

        if action == "delete":

            return self.delete_event(
                query
            )

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
