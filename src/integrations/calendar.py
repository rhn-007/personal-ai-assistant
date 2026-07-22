import sqlite3
from datetime import datetime

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class CalendarIntegration:

    def __init__(self, db_path="calendar.db"):

        self.db_path = db_path

        self._initialize_database()

        logger.info(
            "Local Calendar database initialized"
        )

    # =====================================================
    # DATABASE CONNECTION
    # =====================================================

    def _connect(self):

        return sqlite3.connect(
            self.db_path
        )

    # =====================================================
    # INITIALIZE DATABASE
    # =====================================================

    def _initialize_database(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title TEXT NOT NULL,

                description TEXT,

                event_date TEXT NOT NULL,

                event_time TEXT,

                created_at TEXT NOT NULL

            )
            """
        )

        connection.commit()

        connection.close()

    # =====================================================
    # CREATE EVENT
    # =====================================================

    def create_event(
        self,
        title,
        event_date,
        event_time=None,
        description=""
    ):

        connection = self._connect()

        cursor = connection.cursor()

        created_at = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO events
            (
                title,
                description,
                event_date,
                event_time,
                created_at
            )

            VALUES (?, ?, ?, ?, ?)
            """,

            (
                title,
                description,
                event_date,
                event_time,
                created_at
            )
        )

        connection.commit()

        event_id = cursor.lastrowid

        connection.close()

        return {
            "id": event_id,
            "title": title,
            "date": event_date,
            "time": event_time
        }

    # =====================================================
    # GET ALL EVENTS
    # =====================================================

    def get_all_events(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                event_date,
                event_time

            FROM events

            ORDER BY event_date, event_time
            """
        )

        rows = cursor.fetchall()

        connection.close()

        return rows

    # =====================================================
    # GET EVENTS FOR DATE
    # =====================================================

    def get_events_for_date(
        self,
        event_date
    ):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                event_date,
                event_time

            FROM events

            WHERE event_date = ?

            ORDER BY event_time
            """,

            (event_date,)
        )

        rows = cursor.fetchall()

        connection.close()

        return rows

    # =====================================================
    # DELETE EVENT BY TITLE
    # =====================================================

    def delete_event_by_title(self, title):

        if not title:

            return None

        connection = self._connect()

        cursor = connection.cursor()

        # Find the most recently created matching event
        cursor.execute(
            """
            SELECT
                id,
                title

            FROM events

            WHERE LOWER(title) LIKE LOWER(?)

            ORDER BY id DESC

            LIMIT 1
            """,

            (f"%{title}%",)
        )

        event = cursor.fetchone()

        if not event:

            connection.close()

            return None

        event_id = event[0]

        event_title = event[1]

        cursor.execute(
            """
            DELETE FROM events

            WHERE id = ?
            """,

            (event_id,)
        )

        connection.commit()

        connection.close()

        return {
            "id": event_id,
            "title": event_title
        }

    # =====================================================
    # DELETE LATEST EVENT
    # =====================================================

    def delete_latest_event(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title

            FROM events

            ORDER BY id DESC

            LIMIT 1
            """
        )

        event = cursor.fetchone()

        if not event:

            connection.close()

            return None

        event_id = event[0]

        title = event[1]

        cursor.execute(
            """
            DELETE FROM events

            WHERE id = ?
            """,

            (event_id,)
        )

        connection.commit()

        connection.close()

        return {
            "id": event_id,
            "title": title
        }
