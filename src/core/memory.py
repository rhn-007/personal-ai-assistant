"""
Memory 3.0 - Event-Based + Contextual Long-Term Memory
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MemoryManager:
    """Memory 3.0: stores facts + events + learning patterns"""

    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    # ---------------- INIT ----------------

    def _ensure_db_exists(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Conversations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_message TEXT,
                    assistant_message TEXT,
                    metadata TEXT
                )
            """)

            # USER FACTS (name, preferences)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """)

            # 🧠 MEMORY 3.0: EVENTS TABLE (NEW CORE)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    content TEXT,
                    importance INTEGER DEFAULT 1,
                    timestamp TEXT
                )
            """)

            conn.commit()

    # ---------------- PROFILE MEMORY ----------------

    def set_profile(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO user_profile (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at=excluded.updated_at
            """, (key, value, datetime.now().isoformat()))

    def get_profile(self, key: str):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM user_profile WHERE key=?",
                (key,)
            ).fetchone()
            return row[0] if row else None

    def get_all_profile(self):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT key, value FROM user_profile").fetchall()
            return dict(rows)

    # ---------------- 🧠 MEMORY 3.0 CORE ----------------

    def add_event(self, event_type: str, content: str, importance: int = 1):
        """
        Store real-world context event
        Example:
        - "goal": "build AI assistant"
        - "problem": "low disk space on C drive"
        - "preference": "likes short answers"
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memory_events (event_type, content, importance, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                event_type,
                content,
                importance,
                datetime.now().isoformat()
            ))

    def get_events(self, limit: int = 20):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT event_type, content, importance, timestamp
                FROM memory_events
                ORDER BY importance DESC, id DESC
                LIMIT ?
            """, (limit,)).fetchall()

            return [
                {
                    "type": r[0],
                    "content": r[1],
                    "importance": r[2],
                    "timestamp": r[3]
                }
                for r in rows
            ]

    def search_events(self, keyword: str):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT event_type, content, importance, timestamp
                FROM memory_events
                WHERE content LIKE ?
                ORDER BY importance DESC
            """, (f"%{keyword}%",)).fetchall()

            return [
                {
                    "type": r[0],
                    "content": r[1],
                    "importance": r[2],
                    "timestamp": r[3]
                }
                for r in rows
            ]

    # ---------------- CONVERSATIONS ----------------

    def save_exchange(self, exchange: Dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations (timestamp, user_message, assistant_message, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                exchange.get("timestamp"),
                exchange.get("user"),
                exchange.get("assistant"),
                json.dumps(exchange.get("metadata", {}))
            ))

    def get_history(self, limit: int = 10):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT timestamp, user_message, assistant_message, metadata
                FROM conversations
                ORDER BY id DESC
                LIMIT ?
            """, (limit,)).fetchall()

            return list(reversed([
                {
                    "timestamp": r[0],
                    "user": r[1],
                    "assistant": r[2],
                    "metadata": json.loads(r[3]) if r[3] else {}
                }
                for r in rows
            ]))
