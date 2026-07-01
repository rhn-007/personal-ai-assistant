"""
Memory Management - Memory 4.0 (FIXED + COMPLETE COMPATIBILITY)
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import setup_logger

logger = setup_logger(__name__)


class MemoryManager:
    """Advanced persistent memory system (Memory 4.0 FIXED)"""

    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    # ---------------- INIT ----------------

    def _ensure_db_exists(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

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

            conn.commit()
            logger.info("Memory 4.0 DB initialized (FIXED)")

    # =========================================================
    # 🧠 PROFILE MEMORY
    # =========================================================

    def set_profile(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO user_profile (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at=excluded.updated_at
            """, (key, value, datetime.now().isoformat()))
            conn.commit()

    def get_profile(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM user_profile WHERE key=?", (key,))
            row = cur.fetchone()
            return row[0] if row else None

    def get_all_profile(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM user_profile")
            return dict(cur.fetchall())

    # =========================================================
    # 🔥 SEMANTIC MEMORY
    # =========================================================

    def add_semantic_memory(self, category: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT weight FROM semantic_memory
                WHERE category=? AND value=?
            """, (category, value))

            row = cur.fetchone()

            if row:
                cur.execute("""
                    UPDATE semantic_memory
                    SET weight = weight + 1,
                        last_used = ?
                    WHERE category=? AND value=?
                """, (datetime.now().isoformat(), category, value))
            else:
                cur.execute("""
                    INSERT INTO semantic_memory
                    (category, value, weight, last_used)
                    VALUES (?, ?, 1, ?)
                """, (category, value, datetime.now().isoformat()))

            conn.commit()

    def get_semantic_memory(self, category: str) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT value FROM semantic_memory
                WHERE category=?
                ORDER BY weight DESC
            """, (category,))
            return [r[0] for r in cur.fetchall()]

    # =========================================================
    # 🆕 COMPATIBILITY LAYER (IMPORTANT FIX)
    # =========================================================

    def get_all_semantic(self) -> Dict:
        """
        FIX: used by Assistant + Planner + AgentLoop
        """
        return {
            "likes": self.get_semantic_memory("likes"),
            "dislikes": self.get_semantic_memory("dislikes"),
            "interests": self.get_semantic_memory("interests"),
        }

    def get_all_semantic_flat(self) -> Dict:
        """
        Alternative flat structure (future planning use)
        """
        return self.get_all_semantic()

    # =========================================================
    # 🆕 EVENT SYSTEM
    # =========================================================

    def add_event(self, type: str, content: str, importance: int = 1):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO events (type, content, importance, timestamp)
                VALUES (?, ?, ?, ?)
            """, (type, content, importance, datetime.now().isoformat()))
            conn.commit()

    def get_events(self, limit: int = 10) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT type, content, importance, timestamp
                FROM events
                ORDER BY importance DESC, id DESC
                LIMIT ?
            """, (limit,))

            return [
                {
                    "type": r[0],
                    "content": r[1],
                    "importance": r[2],
                    "timestamp": r[3]
                }
                for r in cur.fetchall()
            ]

    # =========================================================
    # 🧠 SMART MEMORY RETRIEVAL
    # =========================================================

    def retrieve_relevant_memory(self, text: str) -> Dict:
        return {
            "profile": self.get_all_profile(),
            "events": self.get_events(),
            "likes": self.get_semantic_memory("likes"),
            "dislikes": self.get_semantic_memory("dislikes"),
            "interests": self.get_semantic_memory("interests"),
        }

    # =========================================================
    # 🧠 AUTO LEARN
    # =========================================================

    def auto_learn(self, text: str):
        t = text.lower()

        if "my name is" in t:
            self.set_profile("name", text.split("my name is")[-1].strip())

        if "i like" in t:
            self.add_semantic_memory("likes", text.split("i like")[-1].strip())

        if "i hate" in t:
            self.add_semantic_memory("dislikes", text.split("i hate")[-1].strip())

        for w in ["ai", "coding", "anime", "music", "games", "python"]:
            if w in t:
                self.add_semantic_memory("interests", w)

    # =========================================================
    # 🧾 HISTORY
    # =========================================================

    def save_exchange(self, exchange: Dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations
                (timestamp, user_message, assistant_message, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                exchange.get("timestamp"),
                exchange.get("user"),
                exchange.get("assistant"),
                json.dumps(exchange.get("metadata", {}))
            ))
            conn.commit()

    def get_history(self, limit: int = 10):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT timestamp, user_message, assistant_message
                FROM conversations
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))

            rows = cur.fetchall()

            return list(reversed([
                {
                    "timestamp": r[0],
                    "user": r[1],
                    "assistant": r[2]
                }
                for r in rows
            ]))

    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM conversations")
            conn.commit()
