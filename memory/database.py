"""
Memory Database Manager for Yui AI Companion
Handles persistent conversation storage using SQLite
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json


class DatabaseManager:
    """Manages SQLite database for conversation history and user profiles"""
    
    def __init__(self, db_path: str = "data/yui_memory.db"):
        """Initialize database connection"""
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        
        # Conversations table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_name TEXT NOT NULL,
                personality TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                emotion TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User profiles table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE NOT NULL,
                preferences TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME
            )
        """)
        
        # Sessions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_name TEXT NOT NULL,
                personality TEXT NOT NULL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                message_count INTEGER DEFAULT 0
            )
        """)
        
        self.conn.commit()
    
    def save_message(self, session_id: str, user_name: str, personality: str,
                    role: str, content: str, emotion: Optional[str] = None):
        """Save a message to the database"""
        timestamp = datetime.now().isoformat()
        
        self.cursor.execute("""
            INSERT INTO conversations 
            (session_id, user_name, personality, role, content, timestamp, emotion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_name, personality, role, content, timestamp, emotion))
        
        # Update session message count
        self.cursor.execute("""
            UPDATE sessions 
            SET message_count = message_count + 1
            WHERE session_id = ?
        """, (session_id,))
        
        self.conn.commit()
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        self.cursor.execute("""
            SELECT role, content, timestamp, emotion
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        
        messages = [dict(row) for row in self.cursor.fetchall()]
        return list(reversed(messages))  # Return in chronological order
    
    def get_user_history(self, user_name: str, limit: int = 100) -> List[Dict]:
        """Get all conversation history for a user"""
        self.cursor.execute("""
            SELECT session_id, personality, role, content, timestamp, emotion
            FROM conversations
            WHERE user_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_name, limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def create_session(self, session_id: str, user_name: str, personality: str):
        """Create a new conversation session"""
        try:
            self.cursor.execute("""
                INSERT INTO sessions (session_id, user_name, personality)
                VALUES (?, ?, ?)
            """, (session_id, user_name, personality))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Session already exists
            pass
    
    def end_session(self, session_id: str):
        """Mark a session as ended"""
        self.cursor.execute("""
            UPDATE sessions
            SET ended_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()
    
    def get_or_create_user_profile(self, user_name: str) -> Dict:
        """Get or create user profile"""
        self.cursor.execute("""
            SELECT * FROM user_profiles WHERE user_name = ?
        """, (user_name,))
        
        profile = self.cursor.fetchone()
        
        if not profile:
            # Create new profile
            self.cursor.execute("""
                INSERT INTO user_profiles (user_name, preferences, last_seen)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_name, json.dumps({})))
            self.conn.commit()
            
            # Fetch the newly created profile
            self.cursor.execute("""
                SELECT * FROM user_profiles WHERE user_name = ?
            """, (user_name,))
            profile = self.cursor.fetchone()
        else:
            # Update last_seen
            self.cursor.execute("""
                UPDATE user_profiles
                SET last_seen = CURRENT_TIMESTAMP
                WHERE user_name = ?
            """, (user_name,))
            self.conn.commit()
        
        return dict(profile)
    
    def update_user_preferences(self, user_name: str, preferences: Dict):
        """Update user preferences"""
        self.cursor.execute("""
            UPDATE user_profiles
            SET preferences = ?
            WHERE user_name = ?
        """, (json.dumps(preferences), user_name))
        self.conn.commit()
    
    def search_conversations(self, user_name: str, keyword: str, limit: int = 20) -> List[Dict]:
        """Search conversations by keyword"""
        self.cursor.execute("""
            SELECT session_id, personality, role, content, timestamp
            FROM conversations
            WHERE user_name = ? AND content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_name, f'%{keyword}%', limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_stats(self, user_name: str) -> Dict:
        """Get user statistics"""
        # Total messages
        self.cursor.execute("""
            SELECT COUNT(*) as total_messages
            FROM conversations
            WHERE user_name = ?
        """, (user_name,))
        total_messages = self.cursor.fetchone()['total_messages']
        
        # Total sessions
        self.cursor.execute("""
            SELECT COUNT(*) as total_sessions
            FROM sessions
            WHERE user_name = ?
        """, (user_name,))
        total_sessions = self.cursor.fetchone()['total_sessions']
        
        # Favorite personality
        self.cursor.execute("""
            SELECT personality, COUNT(*) as count
            FROM sessions
            WHERE user_name = ?
            GROUP BY personality
            ORDER BY count DESC
            LIMIT 1
        """, (user_name,))
        fav_result = self.cursor.fetchone()
        favorite_personality = fav_result['personality'] if fav_result else 'None'
        
        return {
            'total_messages': total_messages,
            'total_sessions': total_sessions,
            'favorite_personality': favorite_personality
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
