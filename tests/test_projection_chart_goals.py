"""
Tests for ProjectionChart goal-rendering (Ticket 18 — chart slice).

Covers:
- set_goals() filters out achieved goals.
- update_chart() in long-run mode adds line+scatter series for each active goal.
- update_chart() in volume mode skips goal rendering.
- on-track vs. off-track colour selection.
"""
import os
import unittest
from datetime import datetime, timedelta

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtCharts import QLineSeries, QScatterSeries
from PySide6.QtGui import QColor

from run_trend.charts.projection_chart import ProjectionChart


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _aggregates(longest_progression):
    """Build a list of weekly aggregates anchored before today."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(weeks=len(longest_progression))
    aggs = []
    for i, longest in enumerate(longest_progression):
        period_date = start + timedelta(weeks=i)
        aggs.append({
            'period_date': period_date,
            'period': period_date.strftime('%Y-%W'),
            'total_distance_km': 30.0 + i,
            'longest_run_km': longest,
            'num_runs': 4,
            'total_moving_time_h': 4.0,
            'avg_pace_min_per_km': 5.5,
            'is_complete': True,
        })
    return aggs


def _count_series_named(chart, needle):
    return sum(
        1 for s in chart.series()
        if needle in (s.name() or '')
    )


class TestProjectionChartGoals(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def setUp(self):
        self.chart = ProjectionChart()
        self.chart.projection_mode = 'long_run'
        self.chart.mode_combo.setCurrentIndex(1)

    def test_set_goals_drops_achieved(self):
        future = (datetime.now() + timedelta(weeks=12)).strftime('%Y-%m-%d')
        self.chart.set_goals([
            {'target_distance_km': 21.1, 'target_time_seconds': 6600,
             'target_date': future, 'achieved': 0},
            {'target_distance_km': 10.0, 'target_time_seconds': 2700,
             'target_date': future, 'achieved': 1},
        ])
        self.assertEqual(len(self.chart._goals), 1)
        self.assertEqual(self.chart._goals[0]['target_distance_km'], 21.1)

    def test_set_goals_handles_none(self):
        self.chart.set_goals(None)
        self.assertEqual(self.chart._goals, [])

    def test_long_run_mode_renders_goal_marker(self):
        future = (datetime.now() + timedelta(weeks=8)).strftime('%Y-%m-%d')
        self.chart.set_goals([
            {'target_distance_km': 21.1, 'target_time_seconds': 6600,
             'target_date': future, 'achieved': 0},
        ])
        # Increasing long-run trend so projection is plausibly close.
        self.chart.update_chart(_aggregates([6, 8, 10, 12, 14, 16, 18, 20]))

        # At least one scatter and one line for the goal.
        scatters = [s for s in self.chart.chart.series() if isinstance(s, QScatterSeries)]
        self.assertTrue(any('Goal' in (s.name() or '') for s in scatters))
        lines = [s for s in self.chart.chart.series() if isinstance(s, QLineSeries)]
        self.assertTrue(any('Goal target' in (s.name() or '') for s in lines))

    def test_volume_mode_skips_goal_rendering(self):
        future = (datetime.now() + timedelta(weeks=8)).strftime('%Y-%m-%d')
        self.chart.projection_mode = 'volume'
        self.chart.mode_combo.setCurrentIndex(0)
        self.chart.set_goals([
            {'target_distance_km': 21.1, 'target_time_seconds': 6600,
             'target_date': future, 'achieved': 0},
        ])
        self.chart.update_chart(_aggregates([6, 8, 10, 12, 14, 16, 18, 20]))
        names = [s.name() or '' for s in self.chart.chart.series()]
        self.assertFalse(any('Goal' in n for n in names))

    def test_off_track_goal_uses_red(self):
        # Flat low long-run, but a marathon goal — clearly off track.
        future = (datetime.now() + timedelta(weeks=8)).strftime('%Y-%m-%d')
        self.chart.set_goals([
            {'target_distance_km': 42.195, 'target_time_seconds': 14400,
             'target_date': future, 'achieved': 0},
        ])
        self.chart.update_chart(_aggregates([5, 5, 5, 5, 5, 5, 5, 5]))
        scatters = [
            s for s in self.chart.chart.series()
            if isinstance(s, QScatterSeries) and 'Goal' in (s.name() or '')
        ]
        self.assertTrue(scatters)
        self.assertEqual(scatters[0].color(), QColor("#e74c3c"))

    def test_on_track_goal_uses_green(self):
        # Rapidly growing long-run; small near-term goal — on track.
        future = (datetime.now() + timedelta(weeks=4)).strftime('%Y-%m-%d')
        self.chart.set_goals([
            {'target_distance_km': 5.0, 'target_time_seconds': 1500,
             'target_date': future, 'achieved': 0},
        ])
        self.chart.update_chart(_aggregates([10, 12, 14, 16, 18, 20, 22, 24]))
        scatters = [
            s for s in self.chart.chart.series()
            if isinstance(s, QScatterSeries) and 'Goal' in (s.name() or '')
        ]
        self.assertTrue(scatters)
        self.assertEqual(scatters[0].color(), QColor("#27ae60"))

    def test_past_target_date_is_skipped(self):
        past = (datetime.now() - timedelta(weeks=4)).strftime('%Y-%m-%d')
        self.chart.set_goals([
            {'target_distance_km': 21.1, 'target_time_seconds': 6600,
             'target_date': past, 'achieved': 0},
        ])
        self.chart.update_chart(_aggregates([6, 8, 10, 12, 14, 16, 18, 20]))
        names = [s.name() or '' for s in self.chart.chart.series()]
        self.assertFalse(any('Goal' in n for n in names))


if __name__ == '__main__':
    unittest.main()
