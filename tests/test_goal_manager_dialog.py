"""
Tests for GoalManagerDialog (Ticket 18 — UI slice).

Covers list rendering, add/edit/delete via mocked GoalDialog,
and the Toggle-Achieved action.
"""
import os
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog

from run_trend.storage.database import Database
from run_trend.ui.goal_manager_dialog import GoalManagerDialog


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class TestGoalManagerDialog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.tmpfile.close()
        self.db = Database(db_path=self.tmpfile.name)

    def tearDown(self):
        self.db.close()
        os.unlink(self.tmpfile.name)

    def test_format_helpers(self):
        self.assertEqual(GoalManagerDialog._format_distance(None), "—")
        self.assertEqual(GoalManagerDialog._format_distance(21.0975), "21.10")
        self.assertEqual(GoalManagerDialog._format_time(None), "—")
        self.assertEqual(GoalManagerDialog._format_time(0), "—")
        self.assertEqual(GoalManagerDialog._format_time(125), "2:05")
        self.assertEqual(GoalManagerDialog._format_time(6600), "1:50:00")

    def test_loads_existing_goals_into_table(self):
        self.db.add_goal(10.0, 2700, '2026-05-01')
        self.db.add_goal(21.0975, 6600, '2026-09-13')
        dialog = GoalManagerDialog(self.db)
        self.assertEqual(dialog.table.rowCount(), 2)
        # Sorted by target_date ascending.
        self.assertEqual(dialog.table.item(0, 0).text(), '2026-05-01')
        self.assertEqual(dialog.table.item(1, 0).text(), '2026-09-13')

    def test_add_inserts_via_dialog(self):
        dialog = GoalManagerDialog(self.db)

        def fake_get_data(self_dialog):
            return {
                'target_distance_km': 5.0,
                'target_time_seconds': 1300,
                'target_date': '2026-05-15',
            }

        with patch(
            'run_trend.ui.goal_manager_dialog.GoalDialog'
        ) as MockGoalDialog:
            instance = MockGoalDialog.return_value
            instance.exec.return_value = QDialog.Accepted
            instance.get_data.side_effect = lambda: fake_get_data(instance)
            dialog._add()

        goals = self.db.get_goals()
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]['target_distance_km'], 5.0)
        self.assertEqual(goals[0]['target_time_seconds'], 1300)

    def test_toggle_achieved_flips_state(self):
        gid = self.db.add_goal(10.0, 2700, '2026-05-01')
        dialog = GoalManagerDialog(self.db)
        dialog.table.selectRow(0)

        dialog._toggle_selected()
        self.assertEqual(self.db.get_goals()[0]['achieved'], 1)
        # Status column should reflect the new state after reload.
        self.assertEqual(
            dialog.table.item(0, GoalManagerDialog.COL_STATUS).text(),
            dialog.tr("Achieved"),
        )

        dialog._toggle_selected()
        self.assertEqual(self.db.get_goals()[0]['achieved'], 0)
        self.assertEqual(
            dialog.table.item(0, GoalManagerDialog.COL_STATUS).text(),
            dialog.tr("Active"),
        )
        # Sanity: id round-trips
        self.assertEqual(gid, self.db.get_goals()[0]['id'])

    def test_delete_confirmed_removes_row(self):
        self.db.add_goal(10.0, 2700, '2026-05-01')
        self.db.add_goal(21.0975, 6600, '2026-09-13')
        dialog = GoalManagerDialog(self.db)
        dialog.table.selectRow(0)

        from PySide6.QtWidgets import QMessageBox
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes):
            dialog._delete_selected()

        self.assertEqual(len(self.db.get_goals()), 1)

    def test_delete_cancelled_keeps_row(self):
        self.db.add_goal(10.0, 2700, '2026-05-01')
        dialog = GoalManagerDialog(self.db)
        dialog.table.selectRow(0)

        from PySide6.QtWidgets import QMessageBox
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.No):
            dialog._delete_selected()

        self.assertEqual(len(self.db.get_goals()), 1)

    def test_action_buttons_disabled_without_selection(self):
        self.db.add_goal(10.0, 2700, '2026-05-01')
        dialog = GoalManagerDialog(self.db)
        dialog.table.clearSelection()
        dialog.table.setCurrentCell(-1, -1)
        dialog._update_action_state()
        self.assertFalse(dialog.edit_button.isEnabled())
        self.assertFalse(dialog.toggle_button.isEnabled())
        self.assertFalse(dialog.delete_button.isEnabled())


if __name__ == '__main__':
    unittest.main()
