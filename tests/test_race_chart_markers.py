"""
Tests for race-marker rendering on time-axis charts (T15).

The BaseChart helper ``_add_race_markers`` adds one vertical QLineSeries per
race date. We exercise it through DistanceChart, which inherits BaseChart, to
verify markers appear on the chart only after ``set_race_markers`` is called.
"""
import os
import unittest
from datetime import datetime, timedelta

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCharts import QLineSeries
from PySide6.QtWidgets import QApplication

from run_trend.charts.distance_chart import DistanceChart


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _make_aggregates(start: datetime, n: int):
    return [
        {
            'period_date': start + timedelta(days=7 * i),
            'is_complete': True,
            'total_distance_km': 30 + i,
            'longest_run_km': 12 + i,
            'avg_distance_km': 6 + i,
            'avg_long_run_km': 10 + i,
            'total_moving_time_h': 3.5 + i * 0.1,
            'num_runs': 4 + (i % 2),
        }
        for i in range(n)
    ]


def _line_count_at_x(chart, x_ts_ms: int) -> int:
    """Count QLineSeries that are vertical lines at the given x timestamp."""
    hits = 0
    for s in chart.series():
        if not isinstance(s, QLineSeries):
            continue
        if s.count() != 2:
            continue
        p0, p1 = s.at(0), s.at(1)
        if int(p0.x()) == x_ts_ms and int(p1.x()) == x_ts_ms:
            hits += 1
    return hits


class TestRaceMarkersOnDistanceChart(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_no_markers_when_none_set(self):
        chart = DistanceChart()
        chart.update_chart(_make_aggregates(datetime(2025, 1, 6), 6))
        # No marker series should be present.
        baseline_count = len(chart.chart.series())
        self.assertGreater(baseline_count, 0)

        # Set empty list explicitly — still no markers added on next refresh.
        chart.set_race_markers([])
        chart.update_chart(_make_aggregates(datetime(2025, 1, 6), 6))
        self.assertEqual(len(chart.chart.series()), baseline_count)

    def test_marker_added_for_each_race(self):
        chart = DistanceChart()
        baseline = DistanceChart()
        baseline.update_chart(_make_aggregates(datetime(2025, 1, 6), 6))
        baseline_count = len(baseline.chart.series())

        race_date = datetime(2025, 2, 10)
        chart.set_race_markers([
            {'date': race_date.isoformat(), 'name': 'Spring 10K'},
            {'date': '2025-02-24T00:00:00', 'name': 'City Half'},
        ])
        chart.update_chart(_make_aggregates(datetime(2025, 1, 6), 6))

        self.assertEqual(len(chart.chart.series()), baseline_count + 2)
        self.assertEqual(
            _line_count_at_x(chart.chart, int(race_date.timestamp() * 1000)),
            1,
        )

    def test_markers_persist_across_refresh(self):
        chart = DistanceChart()
        chart.set_race_markers([
            {'date': '2025-02-10T00:00:00', 'name': 'Race A'},
        ])
        chart.update_chart(_make_aggregates(datetime(2025, 1, 6), 6))
        first = len(chart.chart.series())

        # Refresh with the same markers — same total, no double-up, no loss.
        chart.update_chart(_make_aggregates(datetime(2025, 1, 6), 6))
        self.assertEqual(len(chart.chart.series()), first)

    def test_invalid_date_is_skipped(self):
        chart = DistanceChart()
        baseline = DistanceChart()
        baseline.update_chart(_make_aggregates(datetime(2025, 1, 6), 6))
        baseline_count = len(baseline.chart.series())

        chart.set_race_markers([
            {'date': 'not-a-date', 'name': 'Bogus'},
            {'date': None, 'name': 'Also bogus'},
            {'date': '2025-02-10T00:00:00', 'name': 'Real one'},
        ])
        chart.update_chart(_make_aggregates(datetime(2025, 1, 6), 6))
        self.assertEqual(len(chart.chart.series()), baseline_count + 1)


if __name__ == "__main__":
    unittest.main()
