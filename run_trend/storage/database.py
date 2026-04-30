"""
SQLite database management for Running Progress Tracker.
"""
import sqlite3
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


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
                max_heartrate REAL,
                has_heartrate INTEGER DEFAULT 0,
                trainer INTEGER DEFAULT 0,
                manual INTEGER DEFAULT 0,
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

        # Race markers (annotations on the time axis: races, time trials,
        # other notable events). distance_km / result_time are optional so
        # the user can record a race without filling in performance data.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS race_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                distance_km REAL,
                result_time INTEGER,
                notes TEXT,
                created_at TEXT NOT NULL,
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

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_race_markers_date
            ON race_markers(date)
        ''')

        # Migrate older databases that predate the trainer/manual columns
        self._migrate_add_column('activities', 'trainer', 'INTEGER DEFAULT 0')
        self._migrate_add_column('activities', 'manual', 'INTEGER DEFAULT 0')

        self.conn.commit()

    def _migrate_add_column(self, table: str, column: str, decl: str):
        """Idempotently add a column to a table when missing."""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        existing = {row['name'] for row in cursor.fetchall()}
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")
            logger.info("Migrated %s: added column %s", table, column)

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
                    max_heartrate, has_heartrate, trainer, manual,
                    last_synced, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                         ?,
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
                activity_data.get('max_heartrate'),
                1 if activity_data.get('has_heartrate') else 0,
                1 if activity_data.get('trainer') else 0,
                1 if activity_data.get('manual') else 0,
                now,
                activity_data['strava_id'],
                now,
                now
            ))
            self.conn.commit()
            return True
        except Exception:
            logger.exception("Error inserting activity")
            self.conn.rollback()
            return False

    @staticmethod
    def _filter_clause(include_treadmill: bool, include_manual: bool) -> str:
        """Build the optional ``AND ...`` clause used by activity queries."""
        clauses = []
        if not include_treadmill:
            clauses.append("COALESCE(trainer, 0) = 0")
        if not include_manual:
            clauses.append("COALESCE(manual, 0) = 0")
        return (" AND " + " AND ".join(clauses)) if clauses else ""

    def get_all_activities(
        self,
        activity_type: str = 'Run',
        include_treadmill: bool = True,
        include_manual: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get all activities of a specific type.

        Args:
            activity_type: Type of activity (default: 'Run')
            include_treadmill: Include trainer/treadmill activities (default True)
            include_manual: Include manually entered activities (default True)

        Returns:
            List of activity dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM activities WHERE type = ?'
            + self._filter_clause(include_treadmill, include_manual)
            + ' ORDER BY start_date ASC',
            (activity_type,),
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_activities_since(
        self,
        start_date: str,
        activity_type: str = 'Run',
        include_treadmill: bool = True,
        include_manual: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get activities since a specific date.

        Args:
            start_date: ISO format date string
            activity_type: Type of activity (default: 'Run')
            include_treadmill: Include trainer/treadmill activities (default True)
            include_manual: Include manually entered activities (default True)

        Returns:
            List of activity dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM activities WHERE type = ? AND start_date >= ?'
            + self._filter_clause(include_treadmill, include_manual)
            + ' ORDER BY start_date ASC',
            (activity_type, start_date),
        )

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

    def delete_all_activities(self) -> int:
        """Delete all activities from the database.

        Returns:
            int: Number of activities deleted
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM activities')
        count = cursor.fetchone()['count']

        cursor.execute('DELETE FROM activities')
        self.conn.commit()

        return count

    def clear_sync_settings(self):
        """Clear sync-related settings (last sync timestamp, etc.)."""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM settings
            WHERE key IN ('last_sync', 'training_start_date')
        ''')
        self.conn.commit()

    def get_database_path(self) -> str:
        """Get the full path to the database file."""
        return self.db_path

    # ------------------------------------------------------------------ #
    # Race markers                                                         #
    # ------------------------------------------------------------------ #

    def add_race_marker(
        self,
        date: str,
        name: str,
        distance_km: Optional[float] = None,
        result_time: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> int:
        """Insert a race marker and return its new row id.

        Args:
            date: ISO date string of the race.
            name: Display name (e.g. "Hannover Marathon").
            distance_km: Race distance in kilometres, optional.
            result_time: Net time in seconds, optional.
            notes: Free-form notes, optional.
        """
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute('''
            INSERT INTO race_markers (
                date, name, distance_km, result_time, notes,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, name, distance_km, result_time, notes, now, now))
        self.conn.commit()
        return cursor.lastrowid

    def get_race_markers(self) -> List[Dict[str, Any]]:
        """Return all race markers ordered by date ascending."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM race_markers ORDER BY date ASC')
        return [dict(row) for row in cursor.fetchall()]

    def update_race_marker(
        self,
        marker_id: int,
        date: Optional[str] = None,
        name: Optional[str] = None,
        distance_km: Optional[float] = None,
        result_time: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """Update fields on a race marker. Only non-None args are written.

        Returns True if a row was updated, False if no marker with that id exists.
        """
        fields = {
            'date': date,
            'name': name,
            'distance_km': distance_km,
            'result_time': result_time,
            'notes': notes,
        }
        updates = {k: v for k, v in fields.items() if v is not None}
        if not updates:
            return False

        updates['updated_at'] = datetime.utcnow().isoformat()
        set_clause = ', '.join(f'{k} = ?' for k in updates)
        values = list(updates.values()) + [marker_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f'UPDATE race_markers SET {set_clause} WHERE id = ?',
            values,
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_race_marker(self, marker_id: int) -> bool:
        """Delete a race marker by id. Returns True if a row was removed."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM race_markers WHERE id = ?', (marker_id,))
        self.conn.commit()
        return cursor.rowcount > 0

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
