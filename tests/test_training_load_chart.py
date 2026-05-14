"""
Tests for TrainingLoadChart — focused on T40's daily ACWR plot and the
smoothing parameter wired in afterwards.
"""
import os
import unittest
from datetime import date, timedelta

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCharts import QLineSeries
from PySide6.QtWidgets import QApplication


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _spiky_load_history(days: int = 60) -> dict:
    """40 → 80 → 40 loads alternating every other day, enough to clear the
    28-day cold-start window and leave an obviously spiky ACWR line."""
    start = date(2026, 1, 1)
    return {
        start + timedelta(days=i): (80.0 if i % 2 == 0 else 40.0)
        for i in range(days)
    }


def _line_series_points(chart) -> list:
    """Extract (x, y) from the ACWR QLineSeries on the chart."""
    for series in chart.series():
        if isinstance(series, QLineSeries) and series.name() == "ACWR":
            return [(p.x(), p.y()) for p in series.points()]
    return []


class TestTrainingLoadChartSmoothing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def setUp(self):
        # Imported here so the QApplication exists first.
        from run_trend.charts.training_load_chart import TrainingLoadChart
        self.chart_widget = TrainingLoadChart()
        self.daily = _spiky_load_history()

    def test_smoothing_off_produces_raw_ratio_values(self):
        self.chart_widget.update_chart(self.daily, 'off', variant='trimp')
        points = _line_series_points(self.chart_widget.chart)
        self.assertGreater(len(points), 0)
        # Spiky inputs → raw ACWR alternates and has wider spread than
        # any sensibly-smoothed version of the same data.
        ys = [y for _, y in points]
        raw_spread = max(ys) - min(ys)
        self.assertGreater(raw_spread, 0.0)

    def test_strong_smoothing_reduces_spread(self):
        self.chart_widget.update_chart(self.daily, 'off', variant='trimp')
        raw = [y for _, y in _line_series_points(self.chart_widget.chart)]

        self.chart_widget.update_chart(self.daily, 'strong', variant='trimp')
        smoothed = [y for _, y in _line_series_points(self.chart_widget.chart)]

        self.assertEqual(len(raw), len(smoothed))
        # Smoothing should tighten the spread; if the toolbar Glättung
        # didn't reach the chart at all the two arrays would be identical.
        raw_spread = max(raw) - min(raw)
        smoothed_spread = max(smoothed) - min(smoothed)
        self.assertLess(smoothed_spread, raw_spread)
        # And the actual values must differ at least somewhere.
        self.assertNotEqual(raw, smoothed)

    def test_smoothing_does_not_drop_points(self):
        # Sanity: smoothing must preserve length / x-axis alignment so
        # the chart's Y values still correspond to the right dates.
        self.chart_widget.update_chart(self.daily, 'medium', variant='trimp')
        smoothed_points = _line_series_points(self.chart_widget.chart)
        self.chart_widget.update_chart(self.daily, 'off', variant='trimp')
        raw_points = _line_series_points(self.chart_widget.chart)
        self.assertEqual(
            [x for x, _ in smoothed_points], [x for x, _ in raw_points]
        )


if __name__ == "__main__":
    unittest.main()
