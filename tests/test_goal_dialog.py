"""
Tests for GoalDialog (Ticket 18 — UI slice).
"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from run_trend.ui.goal_dialog import GoalDialog


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class TestGoalDialogHelpers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_seconds_to_qtime_roundtrip(self):
        for s in [0, 1, 59, 60, 3600, 3661, 13522]:
            t = GoalDialog._seconds_to_qtime(s)
            self.assertEqual(GoalDialog._qtime_to_seconds(t), s)

    def test_seconds_clamped_to_24h(self):
        t = GoalDialog._seconds_to_qtime(86400)
        self.assertEqual(
            GoalDialog._qtime_to_seconds(t),
            23 * 3600 + 59 * 60 + 59,
        )


class TestGoalDialogDefaults(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_default_distance_is_half_marathon(self):
        dialog = GoalDialog()
        data = dialog.get_data()
        # Spinbox quantises to 3 decimals → 21.098 rather than 21.0975.
        self.assertAlmostEqual(data["target_distance_km"], 21.098, places=3)

    def test_default_target_date_is_three_months_out(self):
        dialog = GoalDialog()
        # The exact date isn't tested (system clock dependent) — just shape.
        self.assertRegex(dialog.get_data()["target_date"], r"^\d{4}-\d{2}-\d{2}$")


class TestGoalDialogPrefill(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_prefill_marathon_preset(self):
        dialog = GoalDialog(goal={
            "target_distance_km": 42.195,
            "target_time_seconds": 14400,  # 4:00:00
            "target_date": "2026-09-13",
        })
        data = dialog.get_data()
        self.assertAlmostEqual(data["target_distance_km"], 42.195, places=2)
        self.assertEqual(data["target_time_seconds"], 14400)
        self.assertEqual(data["target_date"], "2026-09-13")

    def test_prefill_custom_distance_falls_into_custom_slot(self):
        dialog = GoalDialog(goal={
            "target_distance_km": 12.345,
            "target_time_seconds": 3600,
            "target_date": "2026-06-01",
        })
        data = dialog.get_data()
        self.assertAlmostEqual(data["target_distance_km"], 12.345, places=3)
        # Combo should have switched to "Custom" (last index).
        self.assertEqual(
            dialog.distance_combo.currentIndex(),
            dialog.distance_combo.count() - 1,
        )
        self.assertTrue(dialog.distance_spin.isEnabled())

    def test_preset_match_disables_distance_spin(self):
        dialog = GoalDialog(goal={
            "target_distance_km": 10.0,
            "target_time_seconds": 2700,
            "target_date": "2026-06-01",
        })
        # 10K preset selected → spin box read-only / disabled.
        self.assertFalse(dialog.distance_spin.isEnabled())


class TestGoalDialogValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_get_data_returns_full_dict(self):
        dialog = GoalDialog()
        data = dialog.get_data()
        self.assertIn("target_distance_km", data)
        self.assertIn("target_time_seconds", data)
        self.assertIn("target_date", data)
        self.assertGreater(data["target_distance_km"], 0)


if __name__ == "__main__":
    unittest.main()
