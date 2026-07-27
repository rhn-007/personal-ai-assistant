"""
Memory Management - Memory 5.0
Persistent Profile, Semantic, Event, and Conversation Memory
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
    Persistent memory system for the AI assistant.

    Stores:

    - User profile information
    - Likes
    - Dislikes
    - Interests
    - Important events
    - Conversation history
    """

    def __init__(

        self,

        db_path: str = "data/history.db"

    ):

        self.db_path = db_path

        self._ensure_db_exists()

    # =========================================================
    # DATABASE INITIALIZATION
    # =========================================================

    def _ensure_db_exists(self):

        Path(
            self.db_path
        ).parent.mkdir(

            parents=True,

            exist_ok=True

        )

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cursor = conn.cursor()

            # ---------------------------------------------
            # CONVERSATIONS
            # ---------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS conversations (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    timestamp TEXT,

                    user_message TEXT,

                    assistant_message TEXT,

                    metadata TEXT

                )

            """)

            # ---------------------------------------------
            # USER PROFILE
            # ---------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS user_profile (

                    key TEXT PRIMARY KEY,

                    value TEXT,

                    updated_at TEXT

                )

            """)

            # ---------------------------------------------
            # SEMANTIC MEMORY
            # ---------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS semantic_memory (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    category TEXT,

                    value TEXT,

                    weight INTEGER DEFAULT 1,

                    last_used TEXT

                )

            """)

            # ---------------------------------------------
            # EVENTS
            # ---------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS events (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    type TEXT,

                    content TEXT,

                    importance INTEGER DEFAULT 1,

                    timestamp TEXT

                )

            """)

            conn.commit()

        logger.info(

            "Memory system initialized successfully."

        )

    # =========================================================
    # PROFILE MEMORY
    # =========================================================

    def set_profile(

        self,

        key: str,

        value: str

    ):

        if not key or value is None:

            return

        with sqlite3.connect(

            self.db_path

        ) as conn:

            conn.execute("""

                INSERT INTO user_profile (

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

                key.strip().lower(),

                str(value).strip(),

                datetime.now().isoformat()

            ))

            conn.commit()

        logger.info(

            f"Profile memory updated: {key}"

        )

    def get_profile(

        self,

        key: str

    ) -> Optional[str]:

        if not key:

            return None

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cursor = conn.cursor()

            cursor.execute("""

                SELECT value

                FROM user_profile

                WHERE key = ?

            """, (

                key.strip().lower(),

            ))

            row = cursor.fetchone()

            return row[0] if row else None

    def get_all_profile(

        self

    ) -> Dict:

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cursor = conn.cursor()

            cursor.execute("""

                SELECT key, value

                FROM user_profile

                ORDER BY updated_at DESC

            """)

            return dict(

                cursor.fetchall()

            )

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

        category = category.strip().lower()

        value = value.strip()

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cursor = conn.cursor()

            cursor.execute("""

                SELECT id, weight

                FROM semantic_memory

                WHERE category = ?

                AND LOWER(value) = LOWER(?)

            """, (

                category,

                value

            ))

            row = cursor.fetchone()

            if row:

                cursor.execute("""

                    UPDATE semantic_memory

                    SET weight = weight + 1,

                        last_used = ?

                    WHERE id = ?

                """, (

                    datetime.now().isoformat(),

                    row[0]

                ))

            else:

                cursor.execute("""

                    INSERT INTO semantic_memory (

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

        logger.info(

            f"Semantic memory updated: "

            f"{category} -> {value}"

        )

    def get_semantic_memory(

        self,

        category: str

    ) -> List[str]:

        if not category:

            return []

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cursor = conn.cursor()

            cursor.execute("""

                SELECT value

                FROM semantic_memory

                WHERE category = ?

                ORDER BY weight DESC, last_used DESC

            """, (

                category.strip().lower(),

            ))

            return [

                row[0]

                for row in cursor.fetchall()

            ]

    def get_all_semantic(

        self

    ) -> Dict:

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cursor = conn.cursor()

            cursor.execute("""

                SELECT category, value

                FROM semantic_memory

                ORDER BY weight DESC

            """)

            rows = cursor.fetchall()

        result = {}

        for category, value in rows:

            if category not in result:

                result[category] = []

            result[category].append(value)

        return result

    def get_all_semantic_flat(

        self

    ) -> Dict:

        return self.get_all_semantic()

    # =========================================================
    # EVENT MEMORY
    # =========================================================

    def add_event(

        self,

        type: str,

        content: str,

        importance: int = 1

    ):

        if not type or not content:

            return

        with sqlite3.connect(

            self.db_path

        ) as conn:

            conn.execute("""

                INSERT INTO events (

                    type,

                    content,

                    importance,

                    timestamp

                )

                VALUES (?, ?, ?, ?)

            """, (

                type,

                content,

                importance,

                datetime.now().isoformat()

            ))

            conn.commit()

    def get_events(

        self,

        limit: int = 10

    ) -> List[Dict]:

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cursor = conn.cursor()

            cursor.execute("""

                SELECT type,

                       content,

                       importance,

                       timestamp

                FROM events

                ORDER BY importance DESC, id DESC

                LIMIT ?

            """, (

                limit,

            ))

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
    # RELEVANT MEMORY
    # =========================================================

    def retrieve_relevant_memory(

        self,

        text: str

    ) -> Dict:

        return {

            "profile": self.get_all_profile(),

            "semantic": self.get_all_semantic(),

            "events": self.get_events(),

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

        original = text.strip()

        lowered = original.lower()

        # ---------------------------------------------
        # NAME
        # ---------------------------------------------

        if "my name is" in lowered:

            value = original[

                lowered.index("my name is")

                + len("my name is"):

            ].strip()

            if value:

                self.set_profile(

                    "name",

                    value

                )

        # ---------------------------------------------
        # PREFERRED NAME
        # ---------------------------------------------

        if "call me" in lowered:

            value = original[

                lowered.index("call me")

                + len("call me"):

            ].strip()

            if value:

                self.set_profile(

                    "name",

                    value

                )

        # ---------------------------------------------
        # LIKES
        # ---------------------------------------------

        like_phrases = [

            "i like",

            "i love",

            "i enjoy",

            "i am interested in",

            "i'm interested in"

        ]

        for phrase in like_phrases:

            if phrase in lowered:

                start = (

                    lowered.index(phrase)

                    + len(phrase)

                )

                value = original[start:].strip()

                if value:

                    self.add_semantic_memory(

                        "likes",

                        value

                    )

                break

        # ---------------------------------------------
        # DISLIKES
        # ---------------------------------------------

        dislike_phrases = [

            "i hate",

            "i dislike",

            "i don't like",

            "i do not like"

        ]

        for phrase in dislike_phrases:

            if phrase in lowered:

                start = (

                    lowered.index(phrase)

                    + len(phrase)

                )

                value = original[start:].strip()

                if value:

                    self.add_semantic_memory(

                        "dislikes",

                        value

                    )

                break

        # ---------------------------------------------
        # INTERESTS
        # ---------------------------------------------

        known_interests = [

            "ai",

            "artificial intelligence",

            "coding",

            "programming",

            "anime",

            "music",

            "games",

            "gaming",

            "python",

            "robot",

            "robotics",

            "technology",

            "technology"

        ]

        for interest in known_interests:

            if interest in lowered:

                self.add_semantic_memory(

                    "interests",

                    interest

                )

    # =========================================================
    # CONVERSATION HISTORY
    # =========================================================

    def save_exchange(

        self,

        exchange: Dict

    ):

        if not exchange:

            return

        with sqlite3.connect(

            self.db_path

        ) as conn:

            conn.execute("""

                INSERT INTO conversations (

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

    def get_history(

        self,

        limit: int = 10

    ):

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cursor = conn.cursor()

            cursor.execute("""

                SELECT timestamp,

                       user_message,

                       assistant_message

                FROM conversations

                ORDER BY id DESC

                LIMIT ?

            """, (

                limit,

            ))

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

    def clear_history(

        self

    ):

        with sqlite3.connect(

            self.db_path

        ) as conn:

            conn.execute(

                "DELETE FROM conversations"

            )

            conn.commit()

        logger.info(

            "Conversation history cleared."

        )
