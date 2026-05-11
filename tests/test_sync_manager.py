"""
Tests for SyncManager (Ticket 34 — close coverage gap).

The sync manager glues the Strava client to the local DB. Tests use
in-memory mocks for both so we don't touch the network or the filesystem.
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from run_trend.sync.sync_manager import SyncManager


def _activity(strava_id: int, distance_m: float = 5000.0, hr: int = 0) -> dict:
    """Build a Strava-shaped activity payload."""
    base = {
        'id': strava_id,
        'name': f'Run {strava_id}',
        'type': 'Run',
        'distance': distance_m,
        'moving_time': 1800,
        'start_date': '2026-04-01T10:00:00Z',
        'average_speed': 2.78,
    }
    if hr:
        base['average_heartrate'] = hr
    return base


class TestInitialSync(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.db.activity_exists.return_value = False
        self.db.insert_activity.return_value = True
        self.client = MagicMock()
        # Returned activities pass through normalize_activity unchanged
        # except that we add a 'strava_id' field (mirroring the real client).
        self.client.normalize_activity.side_effect = lambda a: {
            **a, 'strava_id': a['id'],
        }
        self.sync = SyncManager(self.db, self.client)

    def test_initial_sync_imports_all_new_activities(self):
        self.client.get_all_activities_since.return_value = [
            _activity(1), _activity(2), _activity(3),
        ]
        stats = self.sync.initial_sync(datetime(2026, 1, 1))

        self.assertEqual(stats['fetched'], 3)
        self.assertEqual(stats['imported'], 3)
        self.assertEqual(stats['updated'], 0)
        self.assertEqual(stats['errors'], 0)
        # Both timestamps persisted.
        keys = {call.args[0] for call in self.db.set_setting.call_args_list}
        self.assertIn('last_sync', keys)
        self.assertIn('training_start_date', keys)

    def test_initial_sync_counts_updates_for_existing(self):
        self.db.activity_exists.return_value = True
        self.client.get_all_activities_since.return_value = [
            _activity(1), _activity(2),
        ]
        stats = self.sync.initial_sync(datetime(2026, 1, 1))

        self.assertEqual(stats['imported'], 0)
        self.assertEqual(stats['updated'], 2)

    def test_initial_sync_counts_errors_on_insert_failure(self):
        self.db.insert_activity.side_effect = [True, False, True]
        self.client.get_all_activities_since.return_value = [
            _activity(1), _activity(2), _activity(3),
        ]
        stats = self.sync.initial_sync(datetime(2026, 1, 1))

        self.assertEqual(stats['imported'], 2)
        self.assertEqual(stats['errors'], 1)

    def test_initial_sync_counts_errors_on_normalize_exception(self):
        self.client.get_all_activities_since.return_value = [_activity(1)]
        self.client.normalize_activity.side_effect = ValueError("malformed")

        stats = self.sync.initial_sync(datetime(2026, 1, 1))

        self.assertEqual(stats['errors'], 1)
        self.assertEqual(stats['imported'], 0)

    def test_initial_sync_client_failure_skips_persistence(self):
        self.client.get_all_activities_since.side_effect = RuntimeError("API down")

        stats = self.sync.initial_sync(datetime(2026, 1, 1))

        self.assertEqual(stats['errors'], 1)
        # No timestamps written — set_setting must not have been called for
        # 'last_sync' / 'training_start_date'.
        keys = [call.args[0] for call in self.db.set_setting.call_args_list]
        self.assertNotIn('last_sync', keys)
        self.assertNotIn('training_start_date', keys)

    def test_initial_sync_progress_callback_invocations(self):
        self.client.get_all_activities_since.return_value = [
            _activity(1), _activity(2),
        ]
        cb = MagicMock()
        self.sync.initial_sync(datetime(2026, 1, 1), progress_callback=cb)

        # 1 init + N per-activity = 3 total
        self.assertEqual(cb.call_count, 3)
        first_call = cb.call_args_list[0]
        self.assertEqual(first_call.args[0], 0)
        self.assertEqual(first_call.args[1], 2)


class TestIncrementalSync(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.db.activity_exists.return_value = False
        self.db.insert_activity.return_value = True
        self.client = MagicMock()
        self.client.normalize_activity.side_effect = lambda a: {
            **a, 'strava_id': a['id'],
        }
        self.sync = SyncManager(self.db, self.client)

    def test_uses_latest_activity_date_with_lookback(self):
        self.db.get_latest_activity_date.return_value = '2026-04-15T00:00:00Z'
        self.client.get_all_activities_since.return_value = []

        self.sync.incremental_sync(lookback_days=7)

        called_from = self.client.get_all_activities_since.call_args.args[0]
        # latest 2026-04-15 minus 7 days = 2026-04-08.
        self.assertEqual(called_from.date(), datetime(2026, 4, 8).date())

    def test_falls_back_to_training_start_when_no_activities(self):
        self.db.get_latest_activity_date.return_value = None
        self.db.get_setting.return_value = '2026-01-01T00:00:00'
        self.client.get_all_activities_since.return_value = []

        self.sync.incremental_sync()

        called_from = self.client.get_all_activities_since.call_args.args[0]
        self.assertEqual(called_from.year, 2026)
        self.assertEqual(called_from.month, 1)
        self.assertEqual(called_from.day, 1)

    def test_falls_back_to_30_days_when_nothing_configured(self):
        self.db.get_latest_activity_date.return_value = None
        self.db.get_setting.return_value = None
        self.client.get_all_activities_since.return_value = []

        with patch('run_trend.sync.sync_manager.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 5, 1, 12, 0, 0)
            # Keep fromisoformat etc. working.
            mock_dt.fromisoformat.side_effect = datetime.fromisoformat
            self.sync.incremental_sync()

        called_from = self.client.get_all_activities_since.call_args.args[0]
        expected = datetime(2026, 5, 1, 12, 0, 0) - timedelta(days=30)
        self.assertEqual(called_from, expected)


class TestSyncStatus(unittest.TestCase):

    def test_get_sync_status_reports_synced_when_last_sync_present(self):
        db = MagicMock()
        db.get_setting.side_effect = lambda key: {
            'last_sync': '2026-05-11T20:00:00',
            'training_start_date': '2026-01-01T00:00:00',
        }.get(key)
        db.get_activity_count.return_value = 42

        sync = SyncManager(db, MagicMock())
        status = sync.get_sync_status()

        self.assertTrue(status['is_synced'])
        self.assertEqual(status['activity_count'], 42)
        self.assertEqual(status['last_sync'], '2026-05-11T20:00:00')

    def test_get_sync_status_reports_unsynced_when_no_last_sync(self):
        db = MagicMock()
        db.get_setting.return_value = None
        db.get_activity_count.return_value = 0

        sync = SyncManager(db, MagicMock())
        status = sync.get_sync_status()

        self.assertFalse(status['is_synced'])
        self.assertEqual(status['activity_count'], 0)


if __name__ == "__main__":
    unittest.main()
