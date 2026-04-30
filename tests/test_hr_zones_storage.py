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


if __name__ == '__main__':
    unittest.main()
