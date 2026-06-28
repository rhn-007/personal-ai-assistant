"""
Memory Management - Stores and retrieves conversation history
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class MemoryManager:
    """Manages persistent storage of conversation history"""
    
    def __init__(self, db_path: str = "data/history.db"):
        """
        Initialize memory manager with database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Create database and tables if they don't exist"""
        # Create data directory if needed
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_start TEXT NOT NULL,
                    session_end TEXT,
                    message_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def save_exchange(self, exchange: Dict) -> None:
        """
        Save a conversation exchange to database
        
        Args:
            exchange: Dictionary with 'user', 'assistant', and 'timestamp' keys
        """
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
                logger.debug("Exchange saved to memory")
        
        except Exception as e:
            logger.error(f"Error saving exchange to memory: {e}")
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve conversation history
        
        Args:
            limit: Maximum number of exchanges to retrieve
            
        Returns:
            List of conversation exchanges
        """
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
                
                return list(reversed(history))  # Return in chronological order
        
        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return []
    
    def clear_history(self) -> None:
        """Clear all conversation history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM conversations')
                conn.commit()
                logger.info("Conversation history cleared")
        
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
    
    def search_history(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search conversation history
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching exchanges
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                search_pattern = f"%{query}%"
                cursor.execute('''
                    SELECT timestamp, user_message, assistant_message, metadata
                    FROM conversations
                    WHERE user_message LIKE ? OR assistant_message LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (search_pattern, search_pattern, limit))
                
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'timestamp': row[0],
                        'user': row[1],
                        'assistant': row[2],
                        'metadata': json.loads(row[3]) if row[3] else {}
                    })
                
                return list(reversed(results))
        
        except Exception as e:
            logger.error(f"Error searching history: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get conversation statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM conversations')
                total_messages = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT DATE(timestamp), COUNT(*)
                    FROM conversations
                    GROUP BY DATE(timestamp)
                    ORDER BY DATE(timestamp) DESC
                    LIMIT 7
                ''')
                
                daily_counts = cursor.fetchall()
                
                return {
                    'total_exchanges': total_messages,
                    'daily_activity': {day: count for day, count in daily_counts}
                }
        
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
