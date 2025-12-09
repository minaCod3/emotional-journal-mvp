"""
Data Manager for Emotional Journal MVP
Handles SQLite database operations for journal entries
"""

import sqlite3
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """Manages SQLite database operations for journal entries"""

    def __init__(self, db_path: str = "data/journal_entries.db"):
        """
        Initialize database connection and create tables if needed

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._create_tables()
        logger.info(f"Database initialized at {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Create database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                entry_text TEXT NOT NULL,
                user_selected_mood TEXT,
                ai_sentiment_label TEXT,
                ai_sentiment_score REAL,
                ai_confidence REAL,
                word_count INTEGER,
                detected_emotions TEXT,
                keywords TEXT
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON journal_entries(timestamp)
        ''')

        conn.commit()
        conn.close()

    def save_entry(
        self,
        entry_text: str,
        user_selected_mood: Optional[str] = None,
        ai_sentiment_label: Optional[str] = None,
        ai_sentiment_score: Optional[float] = None,
        ai_confidence: Optional[float] = None,
        detected_emotions: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> int:
        """
        Save a new journal entry to database

        Args:
            entry_text: The journal entry text
            user_selected_mood: User's manually selected mood (emoji)
            ai_sentiment_label: AI-detected sentiment (POSITIVE/NEGATIVE/NEUTRAL)
            ai_sentiment_score: Sentiment score (-1 to 1)
            ai_confidence: Confidence of sentiment prediction (0 to 1)
            detected_emotions: List of detected emotions
            keywords: List of extracted keywords

        Returns:
            Entry ID of the newly created entry
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        word_count = len(entry_text.split())
        emotions_json = json.dumps(detected_emotions) if detected_emotions else None
        keywords_json = json.dumps(keywords) if keywords else None

        cursor.execute('''
            INSERT INTO journal_entries (
                entry_text, user_selected_mood, ai_sentiment_label,
                ai_sentiment_score, ai_confidence, word_count,
                detected_emotions, keywords
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry_text, user_selected_mood, ai_sentiment_label,
            ai_sentiment_score, ai_confidence, word_count,
            emotions_json, keywords_json
        ))

        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Entry {entry_id} saved successfully")
        return entry_id

    def get_all_entries(self) -> pd.DataFrame:
        """
        Get all journal entries as a pandas DataFrame

        Returns:
            DataFrame with all entries
        """
        conn = self._get_connection()
        df = pd.read_sql_query("SELECT * FROM journal_entries ORDER BY timestamp DESC", conn)
        conn.close()

        # Parse JSON fields
        if not df.empty:
            df['detected_emotions'] = df['detected_emotions'].apply(
                lambda x: json.loads(x) if x else []
            )
            df['keywords'] = df['keywords'].apply(
                lambda x: json.loads(x) if x else []
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')

        return df

    def get_recent_entries(self, limit: int = 10) -> pd.DataFrame:
        """
        Get N most recent entries

        Args:
            limit: Number of entries to retrieve

        Returns:
            DataFrame with recent entries
        """
        conn = self._get_connection()
        query = f"SELECT * FROM journal_entries ORDER BY timestamp DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Parse JSON fields
        if not df.empty:
            df['detected_emotions'] = df['detected_emotions'].apply(
                lambda x: json.loads(x) if x else []
            )
            df['keywords'] = df['keywords'].apply(
                lambda x: json.loads(x) if x else []
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')

        return df

    def get_entries_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Get entries within a date range

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            DataFrame with filtered entries
        """
        conn = self._get_connection()
        query = """
            SELECT * FROM journal_entries
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()

        # Parse JSON fields
        if not df.empty:
            df['detected_emotions'] = df['detected_emotions'].apply(
                lambda x: json.loads(x) if x else []
            )
            df['keywords'] = df['keywords'].apply(
                lambda x: json.loads(x) if x else []
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')

        return df

    def search_entries(self, keyword: str) -> pd.DataFrame:
        """
        Search entries by keyword (case-insensitive)

        Args:
            keyword: Keyword to search for

        Returns:
            DataFrame with matching entries
        """
        conn = self._get_connection()
        query = """
            SELECT * FROM journal_entries
            WHERE LOWER(entry_text) LIKE LOWER(?)
            ORDER BY timestamp DESC
        """
        df = pd.read_sql_query(query, conn, params=(f'%{keyword}%',))
        conn.close()

        # Parse JSON fields
        if not df.empty:
            df['detected_emotions'] = df['detected_emotions'].apply(
                lambda x: json.loads(x) if x else []
            )
            df['keywords'] = df['keywords'].apply(
                lambda x: json.loads(x) if x else []
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')

        return df

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete an entry by ID

        Args:
            entry_id: ID of entry to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
            conn.commit()
            conn.close()
            logger.info(f"Entry {entry_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting entry {entry_id}: {e}")
            return False

    def export_to_csv(self, filepath: str = "journal_export.csv") -> str:
        """
        Export all entries to CSV file

        Args:
            filepath: Path for exported CSV file

        Returns:
            Path to exported file
        """
        df = self.get_all_entries()

        # Convert lists to strings for CSV export
        df['detected_emotions'] = df['detected_emotions'].apply(str)
        df['keywords'] = df['keywords'].apply(str)

        df.to_csv(filepath, index=False)
        logger.info(f"Data exported to {filepath}")
        return filepath

    def get_stats(self) -> Dict:
        """
        Calculate aggregate statistics

        Returns:
            Dictionary with statistics
        """
        df = self.get_all_entries()

        if df.empty:
            return {
                'total_entries': 0,
                'current_streak': 0,
                'longest_streak': 0,
                'avg_mood_7d': 0,
                'avg_mood_30d': 0,
                'most_common_emotion': None,
                'consistency_30d': 0
            }

        # Total entries
        total_entries = len(df)

        # Current and longest streak
        current_streak, longest_streak = self._calculate_streaks(df)

        # Average mood (last 7 and 30 days)
        now = datetime.now()
        df_7d = df[df['timestamp'] >= now - timedelta(days=7)]
        df_30d = df[df['timestamp'] >= now - timedelta(days=30)]

        avg_mood_7d = df_7d['ai_sentiment_score'].mean() if not df_7d.empty else 0
        avg_mood_30d = df_30d['ai_sentiment_score'].mean() if not df_30d.empty else 0

        # Most common emotion
        all_emotions = []
        for emotions in df['detected_emotions']:
            if emotions:
                all_emotions.extend(emotions)

        most_common_emotion = max(set(all_emotions), key=all_emotions.count) if all_emotions else None

        # Consistency (% of days with entry in last 30 days)
        unique_days = df_30d['timestamp'].dt.date.nunique()
        consistency_30d = (unique_days / 30) * 100

        return {
            'total_entries': total_entries,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'avg_mood_7d': avg_mood_7d,
            'avg_mood_30d': avg_mood_30d,
            'most_common_emotion': most_common_emotion,
            'consistency_30d': consistency_30d
        }

    def _calculate_streaks(self, df: pd.DataFrame) -> Tuple[int, int]:
        """
        Calculate current and longest journaling streaks

        Args:
            df: DataFrame with entries

        Returns:
            Tuple of (current_streak, longest_streak)
        """
        if df.empty:
            return 0, 0

        # Get unique dates with entries
        dates = sorted(df['timestamp'].dt.date.unique(), reverse=True)

        if not dates:
            return 0, 0

        # Calculate current streak
        current_streak = 1
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        if dates[0] == today or dates[0] == yesterday:
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i + 1]).days == 1:
                    current_streak += 1
                else:
                    break
        else:
            current_streak = 0

        # Calculate longest streak
        longest_streak = 1
        temp_streak = 1

        for i in range(len(dates) - 1):
            if (dates[i] - dates[i + 1]).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1

        return current_streak, longest_streak

    def get_entry_by_id(self, entry_id: int) -> Optional[Dict]:
        """
        Get a single entry by ID

        Args:
            entry_id: ID of entry to retrieve

        Returns:
            Entry as dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        columns = [
            'id', 'timestamp', 'entry_text', 'user_selected_mood',
            'ai_sentiment_label', 'ai_sentiment_score', 'ai_confidence',
            'word_count', 'detected_emotions', 'keywords'
        ]

        entry = dict(zip(columns, row))
        entry['detected_emotions'] = json.loads(entry['detected_emotions']) if entry['detected_emotions'] else []
        entry['keywords'] = json.loads(entry['keywords']) if entry['keywords'] else []

        return entry
