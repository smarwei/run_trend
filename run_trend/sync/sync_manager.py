"""
Synchronization manager for Strava activities.
"""
from datetime import datetime, timedelta
from typing import Optional, Callable
from ..storage.database import Database
from ..strava.client import StravaClient


class SyncManager:
    """Manages synchronization of activities from Strava to local database."""

    def __init__(self, database: Database, client: StravaClient):
        """
        Initialize sync manager.

        Args:
            database: Database instance
            client: StravaClient instance
        """
        self.db = database
        self.client = client

    def initial_sync(
        self,
        start_date: datetime,
        activity_type: str = 'Run',
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> dict:
        """
        Perform initial synchronization from a start date.

        Args:
            start_date: Date to start importing from
            activity_type: Type of activities to import
            progress_callback: Optional callback(current, total, message)

        Returns:
            Dictionary with sync statistics
        """
        stats = {
            'fetched': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        try:
            # Fetch all activities from Strava
            activities = self.client.get_all_activities_since(start_date, activity_type)
            stats['fetched'] = len(activities)

            if progress_callback:
                progress_callback(0, len(activities), "Importing activities...")

            # Import each activity
            for idx, activity in enumerate(activities):
                try:
                    normalized = self.client.normalize_activity(activity)

                    # Check if already exists
                    exists = self.db.activity_exists(normalized['strava_id'])

                    # Insert or update
                    if self.db.insert_activity(normalized):
                        if exists:
                            stats['updated'] += 1
                        else:
                            stats['imported'] += 1
                    else:
                        stats['errors'] += 1

                    if progress_callback:
                        progress_callback(
                            idx + 1,
                            len(activities),
                            f"Imported {stats['imported']} activities..."
                        )

                except Exception as e:
                    print(f"Error importing activity {activity.get('id')}: {e}")
                    stats['errors'] += 1

            # Save sync timestamp
            self.db.set_setting('last_sync', datetime.utcnow().isoformat())
            self.db.set_setting('training_start_date', start_date.isoformat())

        except Exception as e:
            print(f"Sync error: {e}")
            stats['errors'] += 1

        return stats

    def incremental_sync(
        self,
        activity_type: str = 'Run',
        lookback_days: int = 7,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> dict:
        """
        Perform incremental synchronization of new and recent activities.

        Args:
            activity_type: Type of activities to sync
            lookback_days: Days to look back for updates
            progress_callback: Optional callback(current, total, message)

        Returns:
            Dictionary with sync statistics
        """
        stats = {
            'fetched': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        try:
            # Get latest activity date from database
            latest_date_str = self.db.get_latest_activity_date()

            if latest_date_str:
                # Parse the date and look back a bit to catch edits
                latest_date = datetime.fromisoformat(latest_date_str.replace('Z', '+00:00'))
                sync_from = latest_date - timedelta(days=lookback_days)
            else:
                # No activities yet - use training start date if available
                start_date_str = self.db.get_setting('training_start_date')
                if start_date_str:
                    sync_from = datetime.fromisoformat(start_date_str)
                else:
                    # Default to 30 days ago
                    sync_from = datetime.utcnow() - timedelta(days=30)

            # Fetch activities
            activities = self.client.get_all_activities_since(sync_from, activity_type)
            stats['fetched'] = len(activities)

            if progress_callback:
                progress_callback(0, len(activities), "Syncing activities...")

            # Import each activity
            for idx, activity in enumerate(activities):
                try:
                    normalized = self.client.normalize_activity(activity)

                    # Check if already exists
                    exists = self.db.activity_exists(normalized['strava_id'])

                    # Insert or update
                    if self.db.insert_activity(normalized):
                        if exists:
                            stats['updated'] += 1
                        else:
                            stats['imported'] += 1
                    else:
                        stats['errors'] += 1

                    if progress_callback:
                        progress_callback(
                            idx + 1,
                            len(activities),
                            f"Synced {stats['imported'] + stats['updated']} activities..."
                        )

                except Exception as e:
                    print(f"Error syncing activity {activity.get('id')}: {e}")
                    stats['errors'] += 1

            # Save sync timestamp
            self.db.set_setting('last_sync', datetime.utcnow().isoformat())

        except Exception as e:
            print(f"Sync error: {e}")
            stats['errors'] += 1

        return stats

    def get_sync_status(self) -> dict:
        """
        Get current synchronization status.

        Returns:
            Dictionary with status information
        """
        last_sync = self.db.get_setting('last_sync')
        training_start = self.db.get_setting('training_start_date')
        activity_count = self.db.get_activity_count()

        return {
            'last_sync': last_sync,
            'training_start_date': training_start,
            'activity_count': activity_count,
            'is_synced': last_sync is not None
        }
