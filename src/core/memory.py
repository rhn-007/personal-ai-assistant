"""
Memory Management - Stores conversations + persistent user profile
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
    """Manages persistent memory for assistant"""

    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    # ---------------- INIT ----------------

    def _ensure_db_exists(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Conversations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    metadata TEXT
                )
            ''')

            # Sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_start TEXT NOT NULL,
                    session_end TEXT,
                    message_count INTEGER DEFAULT 0
                )
            ''')

            # PROFILE MEMORY (important)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            ''')

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    # ---------------- PROFILE MEMORY (2.0 CORE FEATURE) ----------------

    def set_profile(self, key: str, value: str):
        """Store permanent user memory (name, preferences, etc.)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO user_profile (key, value, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        value=excluded.value,
                        updated_at=excluded.updated_at
                ''', (key, value, datetime.now().isoformat()))

                conn.commit()

        except Exception as e:
            logger.error(f"Profile save error: {e}")

    def get_profile(self, key: str) -> Optional[str]:
        """Get a stored user fact"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    'SELECT value FROM user_profile WHERE key=?',
                    (key,)
                )

                row = cursor.fetchone()
                return row[0] if row else None

        except Exception as e:
            logger.error(f"Profile fetch error: {e}")
            return None

    def get_all_profile(self) -> Dict:
        """Return full user memory profile"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT key, value FROM user_profile')
                return dict(cursor.fetchall())

        except Exception as e:
            logger.error(f"Profile fetch error: {e}")
            return {}

    # ---------------- CONVERSATIONS ----------------

    def save_exchange(self, exchange: Dict) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO conversations (timestamp, user_message, assistant_message, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (
                    exchange.get('timestamp'),
                    exchange.get('user'),
                    exchange.get('assistant'),
                    json.dumps(exchange.get('metadata', {}))
                ))

                conn.commit()

        except Exception as e:
            logger.error(f"Error saving exchange: {e}")

    def get_history(self, limit: int = 10) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT timestamp, user_message, assistant_message, metadata
                    FROM conversations
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))

                rows = cursor.fetchall()

                return list(reversed([
                    {
                        'timestamp': r[0],
                        'user': r[1],
                        'assistant': r[2],
                        'metadata': json.loads(r[3]) if r[3] else {}
                    }
                    for r in rows
                ]))

        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return []

    def clear_history(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM conversations')
                conn.commit()
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
