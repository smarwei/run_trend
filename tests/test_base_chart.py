"""
Tests for the Rate-of-Change helpers extracted into BaseChart (Ticket 33).

The same RoC code lived in DistanceChart, PaceChart and HeartRateChart;
T33 deduplicates it into ``_make_roc_checkbox``, ``_build_roc_series``,
and ``_create_roc_axis``. These tests exercise the helpers in isolation
through DistanceChart (any concrete BaseChart subclass would do).
"""
import math
import os
import unittest
from datetime import datetime, timedelta

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QCheckBox
from PySide6.QtCharts import QLineSeries, QValueAxis

from run_trend.charts.distance_chart import DistanceChart


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _aggregates(distances):
    """Build a list of weekly aggregates with the given distance series."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(weeks=len(distances))
    return [
        {
            'period_date': start + timedelta(weeks=i),
            'period': (start + timedelta(weeks=i)).strftime('%Y-%W'),
            'total_distance_km': d,
            'total_moving_time_h': 4.0,
            'num_runs': 4,
            'weighted_avg_pace_min_per_km': 5.0,
            'avg_speed_kmh': 12.0,
            'avg_heartrate': 150,
            'min_avg_heartrate': 140,
            'max_heartrate': 170,
            'efficiency_factor': 0.025,
            'num_hr_activities': 4,
            'is_complete': True,
        }
        for i, d in enumerate(distances)
    ]


class TestRocCheckboxFactory(unittest.TestCase):

    def setUp(self):
        _ensure_qapplication()
        self.chart = DistanceChart()

    def test_returns_checkbox_unchecked(self):
        cb = self.chart._make_roc_checkbox()
        self.assertIsInstance(cb, QCheckBox)
        self.assertFalse(cb.isChecked())

    def test_label_override_wins(self):
        cb = self.chart._make_roc_checkbox(label_override="Custom")
        self.assertEqual(cb.text(), "Custom")


class TestBuildRocSeries(unittest.TestCase):

    def setUp(self):
        _ensure_qapplication()
        self.chart = DistanceChart()

    def test_too_few_points_returns_none(self):
        # Window size is 8 — anything shorter gives all-NaN, helper returns None.
        aggs = _aggregates([10.0, 20.0, 30.0])
        period_dates = [a['period_date'] for a in aggs]
        result = self.chart._build_roc_series(
            aggs, 'total_distance_km', period_dates, label="x",
        )
        self.assertIsNone(result)

    def test_returns_series_and_valid_values(self):
        aggs = _aggregates([float(i) for i in range(12)])  # linear ramp
        period_dates = [a['period_date'] for a in aggs]
        result = self.chart._build_roc_series(
            aggs, 'total_distance_km', period_dates, label="ramp",
        )
        self.assertIsNotNone(result)
        series, valid = result
        self.assertIsInstance(series, QLineSeries)
        self.assertEqual(series.name(), "ramp")
        # Linear data, window=8 → slope is 1.0 once the window is full.
        self.assertEqual(len(valid), 12 - 7)
        for v in valid:
            self.assertAlmostEqual(v, 1.0, places=4)
            self.assertFalse(math.isnan(v))
        self.assertEqual(series.count(), len(valid))


class TestCreateRocAxis(unittest.TestCase):

    def setUp(self):
        _ensure_qapplication()
        self.chart = DistanceChart()

    def test_axis_range_includes_margin(self):
        axis = self.chart._create_roc_axis([1.0, 2.0, 3.0], "RoC", fmt="%.2f")
        self.assertIsInstance(axis, QValueAxis)
        # range = 2.0; margin = 0.4. Axis: 0.6 .. 3.4.
        self.assertAlmostEqual(axis.min(), 0.6, places=4)
        self.assertAlmostEqual(axis.max(), 3.4, places=4)
        self.assertEqual(axis.labelFormat(), "%.2f")

    def test_collapsed_range_uses_margin_floor(self):
        axis = self.chart._create_roc_axis(
            [5.0, 5.0, 5.0], "RoC", margin_floor=0.5,
        )
        self.assertAlmostEqual(axis.min(), 4.5, places=4)
        self.assertAlmostEqual(axis.max(), 5.5, places=4)


if __name__ == "__main__":
    unittest.main()
