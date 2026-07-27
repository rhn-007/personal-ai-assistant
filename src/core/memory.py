"""
Memory Management - Memory 4.0

Provides:

- Conversation history
- User profile memory
- Semantic memory
- Event memory
- Automatic memory retrieval
"""

import sqlite3
import json

from datetime import datetime

from pathlib import Path

from typing import List, Dict, Optional

from src.utils.logger import setup_logger


logger = setup_logger(

    __name__

)


class MemoryManager:

    """
    Advanced persistent memory system.
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

            # -------------------------------------------------
            # CONVERSATIONS
            # -------------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS conversations (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    timestamp TEXT,

                    user_message TEXT,

                    assistant_message TEXT,

                    metadata TEXT

                )

            """)

            # -------------------------------------------------
            # USER PROFILE
            # -------------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS user_profile (

                    key TEXT PRIMARY KEY,

                    value TEXT,

                    updated_at TEXT

                )

            """)

            # -------------------------------------------------
            # SEMANTIC MEMORY
            # -------------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS semantic_memory (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    category TEXT,

                    value TEXT,

                    weight INTEGER DEFAULT 1,

                    last_used TEXT

                )

            """)

            # -------------------------------------------------
            # EVENTS
            # -------------------------------------------------

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

                "Memory database initialized."

            )

    # =========================================================
    # PROFILE MEMORY
    # =========================================================

    def set_profile(

        self,

        key: str,

        value: str

    ):

        with sqlite3.connect(

            self.db_path

        ) as conn:

            conn.execute("""

                INSERT INTO user_profile

                (key, value, updated_at)

                VALUES (?, ?, ?)

                ON CONFLICT(key)

                DO UPDATE SET

                    value = excluded.value,

                    updated_at = excluded.updated_at

            """, (

                key,

                value,

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

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cur = conn.cursor()

            cur.execute(

                """

                SELECT value

                FROM user_profile

                WHERE key = ?

                """,

                (key,)

            )

            row = cur.fetchone()

            return (

                row[0]

                if row

                else None

            )

    # =========================================================
    # GET ALL PROFILE
    # =========================================================

    def get_all_profile(

        self

    ) -> Dict:

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cur = conn.cursor()

            cur.execute(

                """

                SELECT key, value

                FROM user_profile

                """

            )

            return dict(

                cur.fetchall()

            )

    # =========================================================
    # SEMANTIC MEMORY
    # =========================================================

    def add_semantic_memory(

        self,

        category: str,

        value: str

    ):

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cur = conn.cursor()

            cur.execute(

                """

                SELECT weight

                FROM semantic_memory

                WHERE category = ?

                AND value = ?

                """,

                (

                    category,

                    value

                )

            )

            row = cur.fetchone()

            if row:

                cur.execute(

                    """

                    UPDATE semantic_memory

                    SET weight = weight + 1,

                        last_used = ?

                    WHERE category = ?

                    AND value = ?

                    """,

                    (

                        datetime.now().isoformat(),

                        category,

                        value

                    )

                )

            else:

                cur.execute(

                    """

                    INSERT INTO semantic_memory

                    (

                        category,

                        value,

                        weight,

                        last_used

                    )

                    VALUES (?, ?, 1, ?)

                    """,

                    (

                        category,

                        value,

                        datetime.now().isoformat()

                    )

                )

            conn.commit()

    # =========================================================
    # GET SEMANTIC MEMORY
    # =========================================================

    def get_semantic_memory(

        self,

        category: str

    ) -> List[str]:

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cur = conn.cursor()

            cur.execute(

                """

                SELECT value

                FROM semantic_memory

                WHERE category = ?

                ORDER BY weight DESC

                """,

                (

                    category,

                )

            )

            return [

                row[0]

                for row in cur.fetchall()

            ]

    # =========================================================
    # GET ALL SEMANTIC MEMORY
    # =========================================================

    def get_all_semantic(

        self

    ) -> Dict:

        return {

            "likes":

                self.get_semantic_memory(

                    "likes"

                ),

            "dislikes":

                self.get_semantic_memory(

                    "dislikes"

                ),

            "interests":

                self.get_semantic_memory(

                    "interests"

                )

        }

    # =========================================================
    # EVENTS
    # =========================================================

    def add_event(

        self,

        type: str,

        content: str,

        importance: int = 1

    ):

        with sqlite3.connect(

            self.db_path

        ) as conn:

            conn.execute(

                """

                INSERT INTO events

                (

                    type,

                    content,

                    importance,

                    timestamp

                )

                VALUES (?, ?, ?, ?)

                """,

                (

                    type,

                    content,

                    importance,

                    datetime.now().isoformat()

                )

            )

            conn.commit()

    # =========================================================
    # GET EVENTS
    # =========================================================

    def get_events(

        self,

        limit: int = 10

    ) -> List[Dict]:

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cur = conn.cursor()

            cur.execute(

                """

                SELECT

                    type,

                    content,

                    importance,

                    timestamp

                FROM events

                ORDER BY importance DESC, id DESC

                LIMIT ?

                """,

                (

                    limit,

                )

            )

            return [

                {

                    "type": row[0],

                    "content": row[1],

                    "importance": row[2],

                    "timestamp": row[3]

                }

                for row in cur.fetchall()

            ]

    # =========================================================
    # RETRIEVE RELEVANT MEMORY
    # =========================================================

    def retrieve_relevant_memory(

        self,

        text: str

    ) -> Dict:

        return {

            "profile":

                self.get_all_profile(),

            "events":

                self.get_events(),

            "likes":

                self.get_semantic_memory(

                    "likes"

                ),

            "dislikes":

                self.get_semantic_memory(

                    "dislikes"

                ),

            "interests":

                self.get_semantic_memory(

                    "interests"

                )

        }

    # =========================================================
    # AUTO LEARN
    # =========================================================

    def auto_learn(

        self,

        text: str

    ):

        t = text.lower()

        if "my name is" in t:

            self.set_profile(

                "name",

                text.split(

                    "my name is",

                    1

                )[1].strip()

            )

        if "i like" in t:

            self.add_semantic_memory(

                "likes",

                text.split(

                    "i like",

                    1

                )[1].strip()

            )

        if "i hate" in t:

            self.add_semantic_memory(

                "dislikes",

                text.split(

                    "i hate",

                    1

                )[1].strip()

            )

        for word in [

            "ai",

            "coding",

            "anime",

            "music",

            "games",

            "python"

        ]:

            if word in t:

                self.add_semantic_memory(

                    "interests",

                    word

                )

    # =========================================================
    # SAVE CONVERSATION
    # =========================================================

    def save_exchange(

        self,

        exchange: Dict

    ):

        with sqlite3.connect(

            self.db_path

        ) as conn:

            conn.execute(

                """

                INSERT INTO conversations

                (

                    timestamp,

                    user_message,

                    assistant_message,

                    metadata

                )

                VALUES (?, ?, ?, ?)

                """,

                (

                    exchange.get(

                        "timestamp"

                    ),

                    exchange.get(

                        "user"

                    ),

                    exchange.get(

                        "assistant"

                    ),

                    json.dumps(

                        exchange.get(

                            "metadata",

                            {}

                        )

                    )

                )

            )

            conn.commit()

    # =========================================================
    # GET CONVERSATION HISTORY
    # =========================================================

    def get_history(

        self,

        limit: int = 10

    ):

        with sqlite3.connect(

            self.db_path

        ) as conn:

            cur = conn.cursor()

            cur.execute(

                """

                SELECT

                    timestamp,

                    user_message,

                    assistant_message

                FROM conversations

                ORDER BY id DESC

                LIMIT ?

                """,

                (

                    limit,

                )

            )

            rows = cur.fetchall()

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
    # CLEAR HISTORY
    # =========================================================

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
