"""
Unit tests for Database — focused on race_markers (Ticket 15 DB layer).
"""
import os
import tempfile
import unittest

from run_trend.storage.database import Database


class TestRaceMarkers(unittest.TestCase):

    def setUp(self):
        # Use a fresh temp file per test so we exercise the schema-creation
        # path each time rather than reusing a shared state.
        self.tmpfile = tempfile.NamedTemporaryFile(
            suffix='.db', delete=False
        )
        self.tmpfile.close()
        self.db = Database(db_path=self.tmpfile.name)

    def tearDown(self):
        self.db.close()
        os.unlink(self.tmpfile.name)

    def test_table_created_on_init(self):
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='race_markers'"
        )
        self.assertIsNotNone(cursor.fetchone())

    def test_init_is_idempotent(self):
        # Re-opening the same DB must not raise.
        self.db.close()
        db2 = Database(db_path=self.tmpfile.name)
        try:
            self.assertEqual(db2.get_race_markers(), [])
        finally:
            db2.close()
            self.db = Database(db_path=self.tmpfile.name)  # re-open for tearDown

    def test_add_and_get_returns_inserted_marker(self):
        new_id = self.db.add_race_marker(
            date='2026-04-12',
            name='Hannover Marathon',
            distance_km=42.195,
            result_time=13522,
            notes='Strong second half',
        )
        self.assertIsInstance(new_id, int)
        self.assertGreater(new_id, 0)

        markers = self.db.get_race_markers()
        self.assertEqual(len(markers), 1)
        m = markers[0]
        self.assertEqual(m['id'], new_id)
        self.assertEqual(m['date'], '2026-04-12')
        self.assertEqual(m['name'], 'Hannover Marathon')
        self.assertAlmostEqual(m['distance_km'], 42.195, places=3)
        self.assertEqual(m['result_time'], 13522)
        self.assertEqual(m['notes'], 'Strong second half')
        self.assertIsNotNone(m['created_at'])
        self.assertIsNotNone(m['updated_at'])

    def test_optional_fields_default_to_null(self):
        new_id = self.db.add_race_marker(date='2026-05-01', name='Local 5K')
        markers = self.db.get_race_markers()
        self.assertEqual(len(markers), 1)
        m = markers[0]
        self.assertEqual(m['id'], new_id)
        self.assertIsNone(m['distance_km'])
        self.assertIsNone(m['result_time'])
        self.assertIsNone(m['notes'])

    def test_get_returns_markers_ordered_by_date(self):
        self.db.add_race_marker(date='2026-06-01', name='June')
        self.db.add_race_marker(date='2026-01-01', name='January')
        self.db.add_race_marker(date='2026-03-15', name='March')
        markers = self.db.get_race_markers()
        self.assertEqual([m['name'] for m in markers],
                         ['January', 'March', 'June'])

    def test_update_changes_only_provided_fields(self):
        new_id = self.db.add_race_marker(
            date='2026-04-12',
            name='Original Name',
            distance_km=21.0975,
            result_time=6000,
            notes='before',
        )
        ok = self.db.update_race_marker(new_id, name='Updated Name', notes='after')
        self.assertTrue(ok)

        m = self.db.get_race_markers()[0]
        self.assertEqual(m['name'], 'Updated Name')
        self.assertEqual(m['notes'], 'after')
        # Untouched fields preserved.
        self.assertEqual(m['date'], '2026-04-12')
        self.assertAlmostEqual(m['distance_km'], 21.0975, places=4)
        self.assertEqual(m['result_time'], 6000)

    def test_update_unknown_id_returns_false(self):
        self.assertFalse(self.db.update_race_marker(99999, name='ghost'))

    def test_update_with_no_fields_returns_false(self):
        new_id = self.db.add_race_marker(date='2026-04-12', name='Race')
        self.assertFalse(self.db.update_race_marker(new_id))

    def test_delete_removes_marker(self):
        new_id = self.db.add_race_marker(date='2026-04-12', name='Race')
        ok = self.db.delete_race_marker(new_id)
        self.assertTrue(ok)
        self.assertEqual(self.db.get_race_markers(), [])

    def test_delete_unknown_id_returns_false(self):
        self.assertFalse(self.db.delete_race_marker(99999))

    def test_replace_overwrites_all_fields_including_nulls(self):
        new_id = self.db.add_race_marker(
            date='2026-04-12',
            name='Original',
            distance_km=42.195,
            result_time=13522,
            notes='before',
        )
        ok = self.db.replace_race_marker(
            new_id,
            date='2026-05-01',
            name='Updated',
            distance_km=None,
            result_time=None,
            notes=None,
        )
        self.assertTrue(ok)
        m = self.db.get_race_markers()[0]
        self.assertEqual(m['date'], '2026-05-01')
        self.assertEqual(m['name'], 'Updated')
        self.assertIsNone(m['distance_km'])
        self.assertIsNone(m['result_time'])
        self.assertIsNone(m['notes'])

    def test_replace_unknown_id_returns_false(self):
        self.assertFalse(
            self.db.replace_race_marker(99999, date='2026-04-12', name='X')
        )


if __name__ == '__main__':
    unittest.main()
