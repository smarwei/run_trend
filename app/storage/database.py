"""
SQLite database management for Running Progress Tracker.
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class Database:
    """Manages SQLite database operations."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use XDG_DATA_HOME for Flatpak compatibility
            data_home = os.environ.get('XDG_DATA_HOME', str(Path.home() / ".local" / "share"))
            db_path = str(Path(data_home) / "run_trend" / "activities.db")

        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self):
        """Create database schema if it doesn't exist."""
        cursor = self.conn.cursor()

        # Create activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                strava_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                timezone TEXT,
                distance REAL NOT NULL,
                moving_time INTEGER NOT NULL,
                elapsed_time INTEGER NOT NULL,
                average_speed REAL,
                max_speed REAL,
                elevation_gain REAL,
                average_heartrate REAL,
                last_synced TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Create indices for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activities_start_date
            ON activities(start_date)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activities_type
            ON activities(type)
        ''')

        self.conn.commit()

    def insert_activity(self, activity_data: Dict[str, Any]) -> bool:
        """
        Insert or update an activity.

        Args:
            activity_data: Dictionary containing activity data

        Returns:
            True if inserted/updated successfully
        """
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO activities (
                    strava_id, name, type, start_date, timezone,
                    distance, moving_time, elapsed_time, average_speed,
                    max_speed, elevation_gain, average_heartrate,
                    last_synced, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                         COALESCE((SELECT created_at FROM activities WHERE strava_id = ?), ?),
                         ?)
            ''', (
                activity_data['strava_id'],
                activity_data.get('name', 'Untitled'),
                activity_data.get('type', 'Run'),
                activity_data['start_date'],
                activity_data.get('timezone'),
                activity_data['distance'],
                activity_data['moving_time'],
                activity_data['elapsed_time'],
                activity_data.get('average_speed'),
                activity_data.get('max_speed'),
                activity_data.get('elevation_gain'),
                activity_data.get('average_heartrate'),
                now,
                activity_data['strava_id'],
                now,
                now
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting activity: {e}")
            self.conn.rollback()
            return False

    def get_all_activities(self, activity_type: str = 'Run') -> List[Dict[str, Any]]:
        """
        Get all activities of a specific type.

        Args:
            activity_type: Type of activity (default: 'Run')

        Returns:
            List of activity dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM activities
            WHERE type = ?
            ORDER BY start_date ASC
        ''', (activity_type,))

        return [dict(row) for row in cursor.fetchall()]

    def get_activities_since(self, start_date: str, activity_type: str = 'Run') -> List[Dict[str, Any]]:
        """
        Get activities since a specific date.

        Args:
            start_date: ISO format date string
            activity_type: Type of activity (default: 'Run')

        Returns:
            List of activity dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM activities
            WHERE type = ? AND start_date >= ?
            ORDER BY start_date ASC
        ''', (activity_type, start_date))

        return [dict(row) for row in cursor.fetchall()]

    def get_latest_activity_date(self) -> Optional[str]:
        """
        Get the start date of the most recent activity.

        Returns:
            ISO format date string or None if no activities
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT MAX(start_date) as latest_date FROM activities
        ''')
        result = cursor.fetchone()
        return result['latest_date'] if result else None

    def activity_exists(self, strava_id: int) -> bool:
        """
        Check if an activity with given Strava ID exists.

        Args:
            strava_id: Strava activity ID

        Returns:
            True if exists
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count FROM activities WHERE strava_id = ?
        ''', (strava_id,))
        result = cursor.fetchone()
        return result['count'] > 0

    def get_activity_count(self) -> int:
        """
        Get total number of activities in database.

        Returns:
            Activity count
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM activities')
        result = cursor.fetchone()
        return result['count']

    def set_setting(self, key: str, value: Any):
        """
        Store a setting.

        Args:
            key: Setting key
            value: Setting value (will be JSON serialized)
        """
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        value_str = json.dumps(value)

        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value_str, now))
        self.conn.commit()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a setting.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()

        if result:
            return json.loads(result['value'])
        return default

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
