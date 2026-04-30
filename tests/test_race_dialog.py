"""
Tests for RaceDialog (Ticket 15 — UI slice).

Covers data round-tripping (prefill from activity, prefill from existing
marker, optional fields → None) and the QTime <-> seconds helpers.
"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QTime
from PySide6.QtWidgets import QApplication

from run_trend.ui.race_dialog import RaceDialog


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class TestRaceDialogHelpers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_seconds_to_qtime_roundtrip(self):
        cases = [0, 1, 59, 60, 3600, 3661, 13522]
        for s in cases:
            t = RaceDialog._seconds_to_qtime(s)
            self.assertEqual(RaceDialog._qtime_to_seconds(t), s)

    def test_seconds_clamped_to_24h(self):
        t = RaceDialog._seconds_to_qtime(86400)  # 24h exactly
        self.assertEqual(
            RaceDialog._qtime_to_seconds(t),
            23 * 3600 + 59 * 60 + 59,
        )

    def test_negative_seconds_floored_to_zero(self):
        t = RaceDialog._seconds_to_qtime(-100)
        self.assertEqual(RaceDialog._qtime_to_seconds(t), 0)


class TestRaceDialogActivityPrefill(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_prefills_from_activity(self):
        activity = {
            "name": "Hannover Marathon",
            "start_date": "2026-04-12T08:00:00Z",
            "distance": 42_195,        # metres
            "moving_time": 13_522,     # seconds
        }
        dialog = RaceDialog(activity=activity)
        data = dialog.get_data()
        self.assertEqual(data["name"], "Hannover Marathon")
        self.assertEqual(data["date"], "2026-04-12")
        self.assertAlmostEqual(data["distance_km"], 42.195, places=3)
        self.assertEqual(data["result_time"], 13_522)
        self.assertIsNone(data["notes"])

    def test_zero_distance_and_time_become_none(self):
        dialog = RaceDialog(activity={
            "name": "Comeback",
            "start_date": "2026-05-01T07:00:00Z",
        })
        data = dialog.get_data()
        self.assertEqual(data["name"], "Comeback")
        self.assertIsNone(data["distance_km"])
        self.assertIsNone(data["result_time"])

    def test_invalid_iso_date_falls_back_to_today(self):
        # Should not raise even if start_date is unparseable.
        dialog = RaceDialog(activity={"name": "X", "start_date": "??"})
        # Date must still be a valid yyyy-MM-dd string.
        self.assertRegex(dialog.get_data()["date"], r"^\d{4}-\d{2}-\d{2}$")


class TestRaceDialogMarkerPrefill(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_full_marker_roundtrip(self):
        marker = {
            "id": 1,
            "date": "2025-09-29",
            "name": "Berlin Marathon",
            "distance_km": 42.195,
            "result_time": 12_900,
            "notes": "PB",
        }
        dialog = RaceDialog(marker=marker)
        data = dialog.get_data()
        self.assertEqual(data["date"], "2025-09-29")
        self.assertEqual(data["name"], "Berlin Marathon")
        self.assertAlmostEqual(data["distance_km"], 42.195, places=3)
        self.assertEqual(data["result_time"], 12_900)
        self.assertEqual(data["notes"], "PB")

    def test_marker_with_optional_fields_null(self):
        marker = {
            "id": 1,
            "date": "2025-09-29",
            "name": "Time Trial",
            "distance_km": None,
            "result_time": None,
            "notes": None,
        }
        dialog = RaceDialog(marker=marker)
        data = dialog.get_data()
        self.assertEqual(data["name"], "Time Trial")
        self.assertIsNone(data["distance_km"])
        self.assertIsNone(data["result_time"])
        self.assertIsNone(data["notes"])


if __name__ == "__main__":
    unittest.main()
