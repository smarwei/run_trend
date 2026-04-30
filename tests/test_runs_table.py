"""
Tests for RunsTable sorting (T03).

Runs without heart-rate data must land at the end when the user sorts
by HR ascending — the placeholder "-" cells are not part of the
matching set the user is looking for.
"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from run_trend.ui.runs_table import NumericTableItem, RunsTable


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class TestNumericTableItemSorting(unittest.TestCase):
    """NumericTableItem orders by its sort_value, never by display text."""

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_lt_uses_sort_value(self):
        self.assertTrue(NumericTableItem("50", 50.0) < NumericTableItem("100", 100.0))
        self.assertFalse(NumericTableItem("100", 100.0) < NumericTableItem("50", 50.0))

    def test_inf_sorts_to_end_ascending(self):
        items = [
            NumericTableItem("120", 120.0),
            NumericTableItem("-", float("inf")),
            NumericTableItem("150", 150.0),
            NumericTableItem("-", float("inf")),
            NumericTableItem("130", 130.0),
        ]
        ascending = sorted(items)
        self.assertEqual(
            [it._sort_value for it in ascending],
            [120.0, 130.0, 150.0, float("inf"), float("inf")],
        )


class TestRunsTableHRSort(unittest.TestCase):
    """update_table must store sort-keys that put missing HR at the end."""

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def setUp(self):
        self.widget = RunsTable()

    def _activity(self, strava_id, avg_hr=None, max_hr=None, has_hr=None):
        return {
            "strava_id": strava_id,
            "name": f"Run {strava_id}",
            "start_date": "2024-01-01T08:00:00Z",
            "distance": 10_000,
            "moving_time": 3_600,
            "elevation_gain": 50,
            "has_heartrate": has_hr if has_hr is not None else avg_hr is not None,
            "average_heartrate": avg_hr,
            "max_heartrate": max_hr,
        }

    def _avg_hr_items(self):
        table = self.widget.table
        return [table.item(row, RunsTable.COL_AVG_HR) for row in range(table.rowCount())]

    def _max_hr_items(self):
        table = self.widget.table
        return [table.item(row, RunsTable.COL_MAX_HR) for row in range(table.rowCount())]

    def test_missing_avg_hr_lands_last_when_sorted_ascending(self):
        self.widget.update_table([
            self._activity(1, avg_hr=140.0, max_hr=170.0),
            self._activity(2, avg_hr=None, max_hr=None),
            self._activity(3, avg_hr=120.0, max_hr=160.0),
        ])
        ordered = sorted(self._avg_hr_items())
        self.assertEqual(
            [item._sort_value for item in ordered],
            [120.0, 140.0, float("inf")],
        )
        self.assertEqual(ordered[-1].text(), "-")

    def test_missing_max_hr_lands_last_when_sorted_ascending(self):
        self.widget.update_table([
            self._activity(1, avg_hr=140.0, max_hr=170.0),
            self._activity(2),  # no HR at all
            self._activity(3, avg_hr=120.0, max_hr=160.0),
        ])
        ordered = sorted(self._max_hr_items())
        self.assertEqual(
            [item._sort_value for item in ordered],
            [160.0, 170.0, float("inf")],
        )

    def test_has_heartrate_false_treated_as_missing(self):
        # has_heartrate=False even though numbers are present — Strava's flag wins.
        self.widget.update_table([
            self._activity(1, avg_hr=140.0, max_hr=170.0, has_hr=False),
            self._activity(2, avg_hr=120.0, max_hr=160.0),
        ])
        ordered = sorted(self._avg_hr_items())
        self.assertEqual(
            [item._sort_value for item in ordered],
            [120.0, float("inf")],
        )


if __name__ == "__main__":
    unittest.main()
