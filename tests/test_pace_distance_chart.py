"""
Tests for PaceDistanceChart axis-range handling (T09).

Regression guard: when every run has the (near-)same pace, the y-axis
must still span at least 1.0 min/km (≥ 0.5 margin floor on each side)
so the chart does not collapse onto a single horizontal line.
"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCharts import QCategoryAxis
from PySide6.QtWidgets import QApplication

from run_trend.charts.pace_distance_chart import PaceDistanceChart


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _pace_axis(chart):
    return next(
        (a for a in chart.axes() if isinstance(a, QCategoryAxis)),
        None,
    )


class TestPaceDistanceChartMargin(unittest.TestCase):
    """Pace-axis must stay visible even when paces barely differ."""

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def test_identical_paces_produce_visible_axis(self):
        chart = PaceDistanceChart()
        chart.update_chart([
            {"distance": 5_000, "moving_time": 1_500},
            {"distance": 10_000, "moving_time": 3_000},
            {"distance": 15_000, "moving_time": 4_500},
        ])
        axis = _pace_axis(chart.chart)
        self.assertIsNotNone(axis, "Pace axis missing after update_chart")
        self.assertGreaterEqual(axis.max() - axis.min(), 1.0)

    def test_float_jitter_paces_still_get_floor_margin(self):
        # Pace difference is only float noise — without max(..., 0.5)
        # the previous code (`diff * 0.1 or 0.5`) would yield ~1e-10
        # and the axis would collapse to a sliver.
        chart = PaceDistanceChart()
        chart.update_chart([
            {"distance": 5_000, "moving_time": 1_500},
            {"distance": 5_000, "moving_time": 1_500 + 1e-6},
        ])
        axis = _pace_axis(chart.chart)
        self.assertIsNotNone(axis)
        self.assertGreaterEqual(axis.max() - axis.min(), 1.0)


if __name__ == "__main__":
    unittest.main()
