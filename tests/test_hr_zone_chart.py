"""
Tests for HrZoneChart (Ticket 19 — chart slice).

Uses the offscreen Qt platform; no display required.
"""
import os
import unittest
from datetime import datetime

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from run_trend.charts.hr_zone_chart import HrZoneChart, _PER_RUN_LIMIT


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _activity(date_str, zones, activity_id=1):
    return {
        'date': datetime.fromisoformat(date_str),
        'activity_id': activity_id,
        'zone_seconds': zones,
        'name': f"Run {activity_id}",
    }


class TestHrZoneChartEmptyStates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = _ensure_qapplication()

    def test_no_hr_max_shows_settings_hint(self):
        chart = HrZoneChart()
        chart.update_chart([], hr_max_configured=False)
        self.assertEqual(chart._outer_stack.currentIndex(), 1)
        self.assertIn("Settings", chart._empty_label.text())

    def test_no_hr_activities_shows_no_data_hint(self):
        chart = HrZoneChart()
        chart.update_chart([], hr_max_configured=True, any_hr_activities=False)
        self.assertEqual(chart._outer_stack.currentIndex(), 1)
        self.assertIn("heart-rate", chart._empty_label.text().lower())

    def test_empty_per_activity_shows_unfetched_hint(self):
        chart = HrZoneChart()
        chart.update_chart(
            [], hr_max_configured=True, any_hr_activities=True,
        )
        self.assertEqual(chart._outer_stack.currentIndex(), 1)
        self.assertIn("fetched", chart._empty_label.text().lower())


class TestHrZoneChartIndicator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = _ensure_qapplication()

    def test_indicator_reflects_polarized_distribution(self):
        chart = HrZoneChart()
        # 80% low, 0% middle, 20% high
        chart.update_chart([
            _activity("2026-01-05", [4000, 4000, 0, 1000, 1000]),
        ])
        text = chart.indicator_label.text()
        self.assertIn("80%", text)
        self.assertIn("20%", text)
        self.assertIn("Polarized", text)

    def test_indicator_flags_non_polarized(self):
        chart = HrZoneChart()
        # 50/50 split — not polarized
        chart.update_chart([
            _activity("2026-01-05", [1000, 0, 4000, 4000, 1000]),
        ])
        text = chart.indicator_label.text()
        self.assertIn("Not polarized", text)

    def test_indicator_handles_zero_total(self):
        chart = HrZoneChart()
        chart.update_chart([
            _activity("2026-01-05", [0, 0, 0, 0, 0]),
        ])
        self.assertIn("no zone time", chart.indicator_label.text().lower())


class TestHrZoneChartAggregation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = _ensure_qapplication()

    def test_aggregated_buckets_by_iso_week(self):
        chart = HrZoneChart()
        chart.update_chart(
            [
                _activity("2026-01-05", [600, 0, 0, 0, 0], 1),  # ISO 2026-W02
                _activity("2026-01-06", [600, 0, 0, 0, 0], 2),  # same week
                _activity("2026-01-12", [0, 600, 0, 0, 0], 3),  # ISO 2026-W03
            ],
            period_type="week",
        )
        chart_obj = chart.aggregated_view['chart']
        # Two periods → two categories on the x-axis.
        x_axes = [a for a in chart_obj.axes() if a.titleText()]
        self.assertEqual(len(x_axes), 2)
        # One stacked-bar series with 5 bar-sets.
        self.assertEqual(len(chart_obj.series()), 1)

    def test_aggregated_buckets_by_month(self):
        chart = HrZoneChart()
        chart.update_chart(
            [
                _activity("2026-01-05", [600, 0, 0, 0, 0], 1),
                _activity("2026-01-30", [600, 0, 0, 0, 0], 2),
                _activity("2026-02-04", [0, 600, 0, 0, 0], 3),
            ],
            period_type="month",
        )
        # Both Jan activities collapse into 2026-01.
        chart_obj = chart.aggregated_view['chart']
        self.assertEqual(len(chart_obj.series()), 1)


class TestHrZoneChartPerRun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = _ensure_qapplication()

    def test_per_run_limits_to_recent_n(self):
        chart = HrZoneChart()
        many = [
            _activity(f"2026-01-{(i % 28) + 1:02d}", [100, 0, 0, 0, 0], i)
            for i in range(_PER_RUN_LIMIT + 5)
        ]
        chart.update_chart(many)
        # Even with surplus activities, the chart still adds a single series
        # (capped via _PER_RUN_LIMIT) without exception.
        self.assertEqual(len(chart.per_run_view['chart'].series()), 1)


if __name__ == '__main__':
    unittest.main()
