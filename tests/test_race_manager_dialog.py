"""
Tests for RaceManagerDialog (Ticket 15 — UI slice).

Focus: dialog populates from DB, deselected state disables actions, and
helpers format distance/time correctly. Edit/Delete flows are exercised
through the public DB methods rather than via simulated user clicks.
"""
import os
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from run_trend.storage.database import Database
from run_trend.ui.race_manager_dialog import RaceManagerDialog


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class TestRaceManagerDialog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = Database(db_path=self.tmp.name)
        self.db.add_race_marker(
            date="2026-04-12", name="Hannover Marathon",
            distance_km=42.195, result_time=13522,
        )
        self.db.add_race_marker(date="2026-05-01", name="Local 5K")

    def tearDown(self):
        self.db.close()
        os.unlink(self.tmp.name)

    def test_table_shows_all_markers(self):
        dialog = RaceManagerDialog(self.db)
        self.assertEqual(dialog.table.rowCount(), 2)
        # Ordered by date ascending (db.get_race_markers contract).
        self.assertEqual(
            dialog.table.item(0, RaceManagerDialog.COL_NAME).text(),
            "Hannover Marathon",
        )
        self.assertEqual(
            dialog.table.item(1, RaceManagerDialog.COL_NAME).text(),
            "Local 5K",
        )

    def test_optional_fields_render_as_dash(self):
        dialog = RaceManagerDialog(self.db)
        # Local 5K row has no distance or time.
        self.assertEqual(
            dialog.table.item(1, RaceManagerDialog.COL_DISTANCE).text(),
            "—",
        )
        self.assertEqual(
            dialog.table.item(1, RaceManagerDialog.COL_TIME).text(),
            "—",
        )

    def test_action_buttons_disabled_when_no_selection(self):
        dialog = RaceManagerDialog(self.db)
        dialog.table.clearSelection()
        dialog.table.setCurrentCell(-1, -1)
        self.assertFalse(dialog.edit_button.isEnabled())
        self.assertFalse(dialog.delete_button.isEnabled())

    def test_action_buttons_enabled_when_row_selected(self):
        dialog = RaceManagerDialog(self.db)
        dialog.table.selectRow(0)
        self.assertTrue(dialog.edit_button.isEnabled())
        self.assertTrue(dialog.delete_button.isEnabled())

    def test_format_time_handles_seconds_minutes_hours(self):
        f = RaceManagerDialog._format_time
        self.assertEqual(f(None), "—")
        self.assertEqual(f(0), "—")
        self.assertEqual(f(45), "0:45")
        self.assertEqual(f(330), "5:30")
        self.assertEqual(f(3661), "1:01:01")
        self.assertEqual(f(13522), "3:45:22")

    def test_format_distance_handles_none(self):
        f = RaceManagerDialog._format_distance
        self.assertEqual(f(None), "—")
        self.assertEqual(f(42.195), "42.20")
        self.assertEqual(f(5), "5.00")

    def test_selected_marker_returns_full_record(self):
        dialog = RaceManagerDialog(self.db)
        dialog.table.selectRow(0)
        m = dialog._selected_marker()
        self.assertIsNotNone(m)
        self.assertEqual(m["name"], "Hannover Marathon")
        self.assertEqual(m["result_time"], 13522)

    def test_reload_picks_up_new_rows(self):
        dialog = RaceManagerDialog(self.db)
        self.assertEqual(dialog.table.rowCount(), 2)
        self.db.add_race_marker(date="2026-06-01", name="June")
        dialog._reload()
        self.assertEqual(dialog.table.rowCount(), 3)


if __name__ == "__main__":
    unittest.main()
