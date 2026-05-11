"""
Tests for the HR-zone DB cache (Ticket 19 — storage slice).
"""
import os
import tempfile
import unittest

from run_trend.storage.database import Database


class TestActivityHrZonesCache(unittest.TestCase):

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.tmpfile.close()
        self.db = Database(db_path=self.tmpfile.name)

    def tearDown(self):
        self.db.close()
        os.unlink(self.tmpfile.name)

    def test_upsert_inserts_then_replaces(self):
        self.db.upsert_activity_hr_zones(123, [60, 600, 300, 100, 0], hr_max_used=190)
        row = self.db.get_activity_hr_zones(123)
        self.assertIsNotNone(row)
        self.assertEqual(row['z1_seconds'], 60)
        self.assertEqual(row['z2_seconds'], 600)
        self.assertEqual(row['hr_max_used'], 190)
        self.assertEqual(row['scheme'], 'classic')
        self.assertIsNone(row['hr_rest_used'])

        # Replace with different values.
        self.db.upsert_activity_hr_zones(123, [10, 20, 30, 40, 50], hr_max_used=190)
        row = self.db.get_activity_hr_zones(123)
        self.assertEqual(row['z1_seconds'], 10)
        self.assertEqual(row['z5_seconds'], 50)

    def test_upsert_persists_karvonen_config(self):
        self.db.upsert_activity_hr_zones(
            456, [0, 100, 200, 300, 400],
            hr_max_used=200, hr_rest_used=55, scheme='karvonen',
        )
        row = self.db.get_activity_hr_zones(456)
        self.assertEqual(row['hr_rest_used'], 55)
        self.assertEqual(row['scheme'], 'karvonen')

    def test_upsert_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            self.db.upsert_activity_hr_zones(1, [10, 20, 30], hr_max_used=190)

    def test_get_unknown_returns_none(self):
        self.assertIsNone(self.db.get_activity_hr_zones(99999))

    def test_invalidate_drops_stale_hr_max(self):
        self.db.upsert_activity_hr_zones(1, [0, 0, 0, 0, 0], hr_max_used=190)
        self.db.upsert_activity_hr_zones(2, [0, 0, 0, 0, 0], hr_max_used=185)

        deleted = self.db.invalidate_activity_hr_zones(hr_max=190)
        self.assertEqual(deleted, 1)
        self.assertIsNotNone(self.db.get_activity_hr_zones(1))
        self.assertIsNone(self.db.get_activity_hr_zones(2))

    def test_invalidate_drops_on_scheme_change(self):
        self.db.upsert_activity_hr_zones(
            1, [0, 0, 0, 0, 0], hr_max_used=190,
            hr_rest_used=50, scheme='karvonen',
        )
        deleted = self.db.invalidate_activity_hr_zones(scheme='classic')
        self.assertEqual(deleted, 1)
        self.assertIsNone(self.db.get_activity_hr_zones(1))

    def test_invalidate_no_args_is_noop(self):
        self.db.upsert_activity_hr_zones(1, [0, 0, 0, 0, 0], hr_max_used=190)
        self.assertEqual(self.db.invalidate_activity_hr_zones(), 0)
        self.assertIsNotNone(self.db.get_activity_hr_zones(1))

    def test_idempotent_schema(self):
        # Re-opening the DB should not raise (CREATE TABLE IF NOT EXISTS).
        self.db.close()
        self.db = Database(db_path=self.tmpfile.name)
        # Surface should still be intact.
        self.db.upsert_activity_hr_zones(1, [0, 0, 0, 0, 0], hr_max_used=190)
        self.assertIsNotNone(self.db.get_activity_hr_zones(1))


class TestActivityHrZonesBulk(unittest.TestCase):
    """Ticket 32 — bulk lookup eliminates N+1 SELECT pattern from the
    HR-zone render path."""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.tmpfile.close()
        self.db = Database(db_path=self.tmpfile.name)

    def tearDown(self):
        self.db.close()
        os.unlink(self.tmpfile.name)

    def test_empty_list_returns_empty_dict(self):
        self.assertEqual(self.db.get_activity_hr_zones_bulk([]), {})

    def test_partial_match_returns_only_present_ids(self):
        self.db.upsert_activity_hr_zones(1, [10, 20, 30, 40, 50], hr_max_used=190)
        self.db.upsert_activity_hr_zones(3, [11, 22, 33, 44, 55], hr_max_used=190)

        result = self.db.get_activity_hr_zones_bulk([1, 2, 3, 4])
        self.assertEqual(set(result), {1, 3})
        self.assertEqual(result[1]['z1_seconds'], 10)
        self.assertEqual(result[3]['z5_seconds'], 55)

    def test_returns_full_row_payload(self):
        self.db.upsert_activity_hr_zones(
            42, [60, 600, 300, 100, 0],
            hr_max_used=200, hr_rest_used=50, scheme='karvonen',
        )
        result = self.db.get_activity_hr_zones_bulk([42])
        row = result[42]
        # Must look identical to single-row API for callers who already
        # rely on those keys.
        self.assertEqual(row['hr_max_used'], 200)
        self.assertEqual(row['hr_rest_used'], 50)
        self.assertEqual(row['scheme'], 'karvonen')

    def test_chunking_handles_more_than_900_ids(self):
        """Stay under SQLite's variable-binding limit when the caller
        passes a long ID list."""
        # Insert 50 rows; query for 1500 IDs (mix of hits and misses).
        for sid in range(1, 51):
            self.db.upsert_activity_hr_zones(sid, [0, 0, 0, 0, 0], hr_max_used=190)

        query_ids = list(range(1, 1501))  # 1500 IDs, of which 50 hit
        result = self.db.get_activity_hr_zones_bulk(query_ids)

        self.assertEqual(len(result), 50)
        self.assertEqual(set(result), set(range(1, 51)))


if __name__ == '__main__':
    unittest.main()
