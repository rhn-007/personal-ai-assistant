"""
Memory Management - Memory 5.0

Responsibilities:

- Store user profile memory
- Store semantic memory
- Store important events
- Store conversation history
- Retrieve recent conversation history quickly
- Retrieve searchable memory
- Provide structured memory data to Ollama
"""

import sqlite3
import json

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class MemoryManager:

    """
    Persistent memory system backed by SQLite.
    """

    def __init__(self, db_path: str = "data/history.db"):

        self.db_path = db_path

        self._ensure_db_exists()

    # =========================================================
    # DATABASE INITIALIZATION
    # =========================================================

    def _ensure_db_exists(self):

        Path(self.db_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    timestamp TEXT,

                    user_message TEXT,

                    assistant_message TEXT,

                    metadata TEXT

                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (

                    key TEXT PRIMARY KEY,

                    value TEXT,

                    updated_at TEXT

                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_memory (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    category TEXT,

                    value TEXT,

                    weight INTEGER DEFAULT 1,

                    last_used TEXT

                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    type TEXT,

                    content TEXT,

                    importance INTEGER DEFAULT 1,

                    timestamp TEXT

                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_semantic_category

                ON semantic_memory(category)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_importance

                ON events(importance DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_id

                ON conversations(id DESC)
            """)

            conn.commit()

        logger.info("Memory database initialized.")

    # =========================================================
    # PROFILE MEMORY
    # =========================================================

    def set_profile(
        self,
        key: str,
        value: str
    ):

        if not key or not value:

            return

        with sqlite3.connect(self.db_path) as conn:

            conn.execute("""
                INSERT INTO user_profile
                (
                    key,
                    value,
                    updated_at
                )
                VALUES (?, ?, ?)

                ON CONFLICT(key)

                DO UPDATE SET

                    value = excluded.value,

                    updated_at = excluded.updated_at
            """, (
                key.strip(),
                value.strip(),
                datetime.now().isoformat()
            ))

            conn.commit()

        logger.info(
            f"Profile memory updated: {key}"
        )

    # =========================================================
    # GET PROFILE
    # =========================================================

    def get_profile(
        self,
        key: str
    ) -> Optional[str]:

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT value

                FROM user_profile

                WHERE key = ?
            """, (key,))

            row = cursor.fetchone()

            if row:

                return row[0]

            return None

    # =========================================================
    # GET ALL PROFILE
    # =========================================================

    def get_all_profile(self) -> Dict:

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT key, value

                FROM user_profile

                ORDER BY updated_at DESC
            """)

            return dict(cursor.fetchall())

    # =========================================================
    # SEMANTIC MEMORY
    # =========================================================

    def add_semantic_memory(
        self,
        category: str,
        value: str
    ):

        if not category or not value:

            return

        category = category.strip()
        value = value.strip()

        if not category or not value:

            return

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, weight

                FROM semantic_memory

                WHERE category = ?

                AND value = ?
            """, (
                category,
                value
            ))

            row = cursor.fetchone()

            if row:

                cursor.execute("""
                    UPDATE semantic_memory

                    SET

                        weight = weight + 1,

                        last_used = ?

                    WHERE id = ?
                """, (
                    datetime.now().isoformat(),
                    row[0]
                ))

            else:

                cursor.execute("""
                    INSERT INTO semantic_memory
                    (
                        category,
                        value,
                        weight,
                        last_used
                    )

                    VALUES (?, ?, ?, ?)
                """, (
                    category,
                    value,
                    1,
                    datetime.now().isoformat()
                ))

            conn.commit()

    # =========================================================
    # GET SEMANTIC MEMORY
    # =========================================================

    def get_semantic_memory(
        self,
        category: str,
        limit: int = 50
    ) -> List[str]:

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT value

                FROM semantic_memory

                WHERE category = ?

                ORDER BY weight DESC, last_used DESC

                LIMIT ?
            """, (
                category,
                limit
            ))

            return [
                row[0]
                for row in cursor.fetchall()
            ]

    # =========================================================
    # GET ALL SEMANTIC MEMORY
    # =========================================================

    def get_all_semantic(self) -> Dict:

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT category, value, weight

                FROM semantic_memory

                ORDER BY weight DESC, last_used DESC
            """)

            rows = cursor.fetchall()

        result = {}

        for category, value, weight in rows:

            if category not in result:

                result[category] = []

            result[category].append({
                "value": value,
                "weight": weight
            })

        return result

    # =========================================================
    # EVENTS
    # =========================================================

    def add_event(
        self,
        event_type: str,
        content: str,
        importance: int = 1
    ):

        if not content:

            return

        with sqlite3.connect(self.db_path) as conn:

            conn.execute("""
                INSERT INTO events
                (
                    type,
                    content,
                    importance,
                    timestamp
                )

                VALUES (?, ?, ?, ?)
            """, (
                event_type,
                content,
                importance,
                datetime.now().isoformat()
            ))

            conn.commit()

    # =========================================================
    # GET EVENTS
    # =========================================================

    def get_events(
        self,
        limit: int = 10
    ) -> List[Dict]:

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT

                    type,

                    content,

                    importance,

                    timestamp

                FROM events

                ORDER BY importance DESC, id DESC

                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()

        return [

            {
                "type": row[0],
                "content": row[1],
                "importance": row[2],
                "timestamp": row[3]
            }

            for row in rows

        ]

    # =========================================================
    # SAVE CONVERSATION
    # =========================================================

    def save_exchange(
        self,
        exchange: Dict
    ):

        with sqlite3.connect(self.db_path) as conn:

            conn.execute("""
                INSERT INTO conversations
                (
                    timestamp,

                    user_message,

                    assistant_message,

                    metadata
                )

                VALUES (?, ?, ?, ?)
            """, (

                exchange.get(
                    "timestamp",
                    datetime.now().isoformat()
                ),

                exchange.get(
                    "user",
                    ""
                ),

                exchange.get(
                    "assistant",
                    ""
                ),

                json.dumps(
                    exchange.get(
                        "metadata",
                        {}
                    )
                )

            ))

            conn.commit()

    # =========================================================
    # GET RECENT HISTORY
    # =========================================================

    def get_history(
        self,
        limit: int = 10
    ) -> List[Dict]:

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT

                    timestamp,

                    user_message,

                    assistant_message

                FROM conversations

                ORDER BY id DESC

                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()

        return list(
            reversed(
                [
                    {
                        "timestamp": row[0],
                        "user": row[1],
                        "assistant": row[2]
                    }

                    for row in rows
                ]
            )
        )

    # =========================================================
    # GET ALL CONVERSATIONS
    # =========================================================

    def get_all_conversations(
        self,
        limit: int = 100
    ) -> List[Dict]:

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT

                    timestamp,

                    user_message,

                    assistant_message

                FROM conversations

                ORDER BY id DESC

                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()

        return [

            {
                "timestamp": row[0],
                "user": row[1],
                "assistant": row[2]
            }

            for row in rows

        ]

    # =========================================================
    # SEARCH CONVERSATIONS
    # =========================================================

    def search_conversations(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:

        if not query:

            return []

        words = [

            word.strip(
                ".,!?;:()[]{}\"'"
            ).lower()

            for word in query.split()

            if len(
                word.strip(
                    ".,!?;:()[]{}\"'"
                )
            ) > 2

        ]

        if not words:

            return []

        conditions = []

        parameters = []

        for word in words:

            conditions.append("""
                (
                    LOWER(user_message) LIKE ?

                    OR

                    LOWER(assistant_message) LIKE ?
                )
            """)

            parameters.extend([
                f"%{word}%",
                f"%{word}%"
            ])

        where_clause = " OR ".join(
            conditions
        )

        parameters.append(limit)

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            cursor.execute(
                f"""
                SELECT

                    timestamp,

                    user_message,

                    assistant_message

                FROM conversations

                WHERE {where_clause}

                ORDER BY id DESC

                LIMIT ?
                """,
                parameters
            )

            rows = cursor.fetchall()

        return [

            {
                "timestamp": row[0],
                "user": row[1],
                "assistant": row[2]
            }

            for row in rows

        ]

    # =========================================================
    # RAW MEMORY SNAPSHOT
    # =========================================================

    def get_memory_snapshot(
        self,
        conversation_limit: int = 50
    ) -> Dict:

        """
        Returns the complete structured memory snapshot.

        Ollama can decide which parts are relevant.
        """

        return {

            "profile": self.get_all_profile(),

            "semantic_memory": self.get_all_semantic(),

            "events": self.get_events(20),

            "conversations": self.get_all_conversations(
                conversation_limit
            )

        }

    # =========================================================
    # AUTO LEARNING
    # =========================================================

    def auto_learn(
        self,
        text: str
    ):

        if not text:

            return

        original_text = text.strip()

        lower_text = original_text.lower()

        # -----------------------------------------------------
        # NAME
        # -----------------------------------------------------

        if "my name is" in lower_text:

            name = original_text.split(
                "my name is",
                1
            )[1].strip()

            if name:

                self.set_profile(
                    "name",
                    name
                )

        # -----------------------------------------------------
        # LIKES
        # -----------------------------------------------------

        if "i like" in lower_text:

            value = original_text.split(
                "i like",
                1
            )[1].strip()

            if value:

                self.add_semantic_memory(
                    "likes",
                    value
                )

        # -----------------------------------------------------
        # DISLIKES
        # -----------------------------------------------------

        if "i hate" in lower_text:

            value = original_text.split(
                "i hate",
                1
            )[1].strip()

            if value:

                self.add_semantic_memory(
                    "dislikes",
                    value
                )

        # -----------------------------------------------------
        # INTERESTS
        # -----------------------------------------------------

        interests = [

            "ai",

            "python",

            "coding",

            "anime",

            "music",

            "games",

            "robot",

            "robotics",

            "spotify",

            "programming"

        ]

        for interest in interests:

            if interest in lower_text:

                self.add_semantic_memory(
                    "interests",
                    interest
                )

    # =========================================================
    # CLEAR CONVERSATION HISTORY
    # =========================================================

    def clear_history(self):

        with sqlite3.connect(self.db_path) as conn:

            conn.execute(
                "DELETE FROM conversations"
            )

            conn.commit()

        logger.info(
            "Conversation history cleared."
        )
