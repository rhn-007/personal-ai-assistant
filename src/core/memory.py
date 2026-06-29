"""
Memory Management - Stores and retrieves conversation history
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
    """Manages persistent storage of conversation history and user memory"""

    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    # ---------------- DB INIT ----------------

    def _ensure_db_exists(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    metadata TEXT
                )
            ''')

            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_start TEXT NOT NULL,
                    session_end TEXT,
                    message_count INTEGER DEFAULT 0
                )
            ''')

            # ✅ NEW: User profile memory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

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

                history = []
                for row in rows:
                    history.append({
                        'timestamp': row[0],
                        'user': row[1],
                        'assistant': row[2],
                        'metadata': json.loads(row[3]) if row[3] else {}
                    })

                return list(reversed(history))

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

    def search_history(self, query: str, limit: int = 20) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                search = f"%{query}%"
                cursor.execute('''
                    SELECT timestamp, user_message, assistant_message, metadata
                    FROM conversations
                    WHERE user_message LIKE ? OR assistant_message LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (search, search, limit))

                rows = cursor.fetchall()

                return [
                    {
                        'timestamp': r[0],
                        'user': r[1],
                        'assistant': r[2],
                        'metadata': json.loads(r[3]) if r[3] else {}
                    }
                    for r in rows
                ][::-1]

        except Exception as e:
            logger.error(f"Error searching history: {e}")
            return []

    def get_stats(self) -> Dict:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT COUNT(*) FROM conversations')
                total = cursor.fetchone()[0]

                return {
                    "total_exchanges": total
                }

        except Exception as e:
            logger.error(f"Error stats: {e}")
            return {}

    # ---------------- 🧠 NEW: USER PROFILE MEMORY ----------------

    def set_profile(self, key: str, value: str):
        """Store a persistent fact (like name, preference, etc.)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO user_profile (key, value)
                    VALUES (?, ?)
                ''', (key, value))

                conn.commit()

        except Exception as e:
            logger.error(f"Error setting profile: {e}")

    def get_profile(self, key: str):
        """Get a stored fact"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT value FROM user_profile WHERE key=?', (key,))
                row = cursor.fetchone()

                return row[0] if row else None

        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None

    def get_all_profile(self) -> Dict:
        """Get all stored memory facts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT key, value FROM user_profile')
                return dict(cursor.fetchall())

        except Exception as e:
            logger.error(f"Error getting all profile: {e}")
            return {}
