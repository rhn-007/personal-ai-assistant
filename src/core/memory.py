"""
Memory Management - Memory 5.0

Provides:

- Conversation history
- User profile memory
- Semantic memory
- Event memory
- Fast relevant memory retrieval
- SQLite connection optimization
- In-memory caching for frequently accessed memory
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
    Fast persistent memory system.

    Uses:

    - SQLite for permanent storage
    - In-memory cache for frequently accessed data
    - Single-query retrieval where possible
    - WAL mode for better SQLite performance
    """

    def __init__(

        self,

        db_path: str = "data/history.db"

    ):

        self.db_path = db_path

        # =====================================================
        # MEMORY CACHE
        # =====================================================

        self.profile_cache = {}

        self.semantic_cache = {

            "likes": [],

            "dislikes": [],

            "interests": []

        }

        self.events_cache = []

        self.cache_loaded = False

        # =====================================================
        # DATABASE
        # =====================================================

        self._ensure_db_exists()

        self._load_cache()

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    def _connect(self):

        """

        Creates an optimized SQLite connection.
        """

        conn = sqlite3.connect(

            self.db_path,

            timeout=10

        )

        conn.execute(

            "PRAGMA journal_mode=WAL"

        )

        conn.execute(

            "PRAGMA synchronous=NORMAL"

        )

        conn.execute(

            "PRAGMA cache_size=-10000"

        )

        return conn

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

        with self._connect() as conn:

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

            # -------------------------------------------------
            # INDEXES
            # -------------------------------------------------

            cursor.execute("""

                CREATE INDEX IF NOT EXISTS idx_semantic_category

                ON semantic_memory(category)

            """)

            cursor.execute("""

                CREATE INDEX IF NOT EXISTS idx_semantic_value

                ON semantic_memory(value)

            """)

            cursor.execute("""

                CREATE INDEX IF NOT EXISTS idx_events_importance

                ON events(importance DESC, id DESC)

            """)

            cursor.execute("""

                CREATE INDEX IF NOT EXISTS idx_conversations_id

                ON conversations(id DESC)

            """)

            conn.commit()

        logger.info(

            "Memory database initialized."

        )

    # =========================================================
    # LOAD CACHE
    # =========================================================

    def _load_cache(self):

        """

        Loads frequently accessed memory into RAM.

        This means normal profile and semantic memory retrieval
        does not need to access SQLite every time.
        """

        try:

            with self._connect() as conn:

                cur = conn.cursor()

                # -------------------------------------------------
                # PROFILE
                # -------------------------------------------------

                cur.execute("""

                    SELECT key, value

                    FROM user_profile

                """)

                self.profile_cache = dict(

                    cur.fetchall()

                )

                # -------------------------------------------------
                # SEMANTIC MEMORY
                # -------------------------------------------------

                cur.execute("""

                    SELECT category, value

                    FROM semantic_memory

                    ORDER BY weight DESC

                """)

                self.semantic_cache = {

                    "likes": [],

                    "dislikes": [],

                    "interests": []

                }

                for category, value in cur.fetchall():

                    if category in self.semantic_cache:

                        self.semantic_cache[

                            category

                        ].append(

                            value

                        )

                # -------------------------------------------------
                # EVENTS
                # -------------------------------------------------

                cur.execute("""

                    SELECT

                        type,

                        content,

                        importance,

                        timestamp

                    FROM events

                    ORDER BY importance DESC, id DESC

                    LIMIT 20

                """)

                self.events_cache = [

                    {

                        "type": row[0],

                        "content": row[1],

                        "importance": row[2],

                        "timestamp": row[3]

                    }

                    for row in cur.fetchall()

                ]

            self.cache_loaded = True

            logger.info(

                "Memory cache loaded."

            )

        except Exception as e:

            logger.error(

                f"Memory cache loading failed: {e}"

            )

    # =========================================================
    # REFRESH CACHE
    # =========================================================

    def _refresh_cache(self):

        """

        Refreshes cached memory after a database update.
        """

        self._load_cache()

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

        key = key.strip()

        value = str(value).strip()

        if not key or not value:

            return

        now = datetime.now().isoformat()

        with self._connect() as conn:

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

                key,

                value,

                now

            ))

            conn.commit()

        # Update RAM cache immediately

        self.profile_cache[key] = value

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

        if not key:

            return None

        return self.profile_cache.get(

            key

        )

    # =========================================================
    # GET ALL PROFILE
    # =========================================================

    def get_all_profile(

        self

    ) -> Dict:

        return dict(

            self.profile_cache

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

        value = str(value).strip()

        if not value:

            return

        now = datetime.now().isoformat()

        with self._connect() as conn:

            cur = conn.cursor()

            cur.execute("""

                SELECT id

                FROM semantic_memory

                WHERE category = ?

                AND value = ?

            """, (

                category,

                value

            ))

            row = cur.fetchone()

            if row:

                cur.execute("""

                    UPDATE semantic_memory

                    SET

                        weight = weight + 1,

                        last_used = ?

                    WHERE id = ?

                """, (

                    now,

                    row[0]

                ))

            else:

                cur.execute("""

                    INSERT INTO semantic_memory

                    (

                        category,

                        value,

                        weight,

                        last_used

                    )

                    VALUES (?, ?, 1, ?)

                """, (

                    category,

                    value,

                    now

                ))

            conn.commit()

        # Update cache directly

        if category not in self.semantic_cache:

            self.semantic_cache[category] = []

        if value not in self.semantic_cache[category]:

            self.semantic_cache[category].insert(

                0,

                value

            )

        logger.info(

            f"Semantic memory updated: "

            f"{category} -> {value}"

        )

    # =========================================================
    # GET SEMANTIC MEMORY
    # =========================================================

    def get_semantic_memory(

        self,

        category: str

    ) -> List[str]:

        return list(

            self.semantic_cache.get(

                category,

                []

            )

        )[:50]

    # =========================================================
    # GET ALL SEMANTIC MEMORY
    # =========================================================

    def get_all_semantic(

        self

    ) -> Dict:

        return {

            "likes": self.get_semantic_memory(

                "likes"

            ),

            "dislikes": self.get_semantic_memory(

                "dislikes"

            ),

            "interests": self.get_semantic_memory(

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

        if not content:

            return

        now = datetime.now().isoformat()

        with self._connect() as conn:

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

                type,

                content,

                importance,

                now

            ))

            conn.commit()

        # Add to cache

        self.events_cache.insert(

            0,

            {

                "type": type,

                "content": content,

                "importance": importance,

                "timestamp": now

            }

        )

        self.events_cache = sorted(

            self.events_cache,

            key=lambda event: (

                event["importance"],

                event["timestamp"]

            ),

            reverse=True

        )[:20]

    # =========================================================
    # GET EVENTS
    # =========================================================

    def get_events(

        self,

        limit: int = 10

    ) -> List[Dict]:

        return self.events_cache[:limit]

    # =========================================================
    # FAST RELEVANT MEMORY RETRIEVAL
    # =========================================================

    def retrieve_relevant_memory(

        self,

        text: str

    ) -> Dict:

        """

        Extremely fast memory retrieval.

        Profile, semantic memory and events are already
        cached in RAM.

        No SQLite query is performed here.

        This is the main performance improvement.
        """

        if not text:

            return {

                "profile": {},

                "events": [],

                "likes": [],

                "dislikes": [],

                "interests": []

            }

        text = text.lower()

        # -----------------------------------------------------
        # TOKENIZE QUERY
        # -----------------------------------------------------

        words = {

            word.strip(

                ".,!?;:()[]{}\"'"

            )

            for word in text.split()

            if len(

                word.strip(

                    ".,!?;:()[]{}\"'"

                )

            ) > 2

        }

        # -----------------------------------------------------
        # FAST MEMORY MATCHING
        # -----------------------------------------------------

        relevant = {

            "likes": [],

            "dislikes": [],

            "interests": []

        }

        for category, values in self.semantic_cache.items():

            for value in values:

                value_lower = value.lower()

                if (

                    value_lower in text

                    or any(

                        word in value_lower

                        for word in words

                    )

                ):

                    relevant[category].append(

                        value

                    )

        # -----------------------------------------------------
        # IF NO SPECIFIC MATCHES
        # -----------------------------------------------------

        # Give the assistant a small amount of
        # general memory context.

        for category in relevant:

            if not relevant[category]:

                relevant[category] = (

                    self.semantic_cache.get(

                        category,

                        []

                    )[:5]

                )

        return {

            "profile": dict(

                self.profile_cache

            ),

            "events": self.events_cache[:5],

            "likes": relevant["likes"][:5],

            "dislikes": relevant["dislikes"][:5],

            "interests": relevant["interests"][:5]

        }

    # =========================================================
    # AUTO LEARN
    # =========================================================

    def auto_learn(

        self,

        text: str

    ):

        if not text:

            return

        t = text.lower()

        # -----------------------------------------------------
        # NAME
        # -----------------------------------------------------

        if "my name is" in t:

            name = text.split(

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

        if "i like" in t:

            value = text.split(

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

        if "i hate" in t:

            value = text.split(

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

        for word in [

            "ai",

            "coding",

            "anime",

            "music",

            "games",

            "python",

            "robot",

            "robotics"

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

        with self._connect() as conn:

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

            ))

            conn.commit()

    # =========================================================
    # GET CONVERSATION HISTORY
    # =========================================================

    def get_history(

        self,

        limit: int = 10

    ):

        with self._connect() as conn:

            cur = conn.cursor()

            cur.execute("""

                SELECT

                    timestamp,

                    user_message,

                    assistant_message

                FROM conversations

                ORDER BY id DESC

                LIMIT ?

            """, (

                limit,

            ))

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

        with self._connect() as conn:

            conn.execute(

                "DELETE FROM conversations"

            )

            conn.commit()

        logger.info(

            "Conversation history cleared."

        )
