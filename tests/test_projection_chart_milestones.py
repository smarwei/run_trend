"""
Regression guard: the Long-Run Projection chart must not draw a future
milestone marker (e.g. "15K Run") for a distance the runner has already
crossed in any aggregate — including the in-progress current week.

Pre-fix the chart was happily painting orange "15K Run" / "10K Run"
markers floating above a projected trend that was still climbing past
those distances, even though the runner had set a new personal PR for
the longest run in the current incomplete week. Confusing for the
runner ("why does it think I'll reach 15 km next month when I just ran
17 today?").
"""
import os
import unittest
from datetime import datetime, timedelta

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCharts import QScatterSeries
from PySide6.QtWidgets import QApplication

from run_trend.charts.projection_chart import ProjectionChart


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _weekly_aggs(longest_progression, *, current_week_longest=None):
    """Build weekly aggregates ending today. If current_week_longest is
    provided, append an in-progress current week with that longest run.
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    monday_of_this_week = today - timedelta(days=today.weekday())
    start = monday_of_this_week - timedelta(weeks=len(longest_progression))
    aggs = []
    for i, longest in enumerate(longest_progression):
        period_date = start + timedelta(weeks=i)
        aggs.append({
            'period_date': period_date,
            'period': period_date.strftime('%Y-%W'),
            'total_distance_km': 25.0 + i,
            'longest_run_km': longest,
            'num_runs': 4,
            'total_moving_time_h': 4.0,
            'avg_pace_min_per_km': 5.5,
            'is_complete': True,
        })
    if current_week_longest is not None:
        aggs.append({
            'period_date': monday_of_this_week,
            'period': monday_of_this_week.strftime('%Y-%W'),
            'total_distance_km': 17.1,
            'longest_run_km': current_week_longest,
            'num_runs': 1,
            'total_moving_time_h': 1.5,
            'avg_pace_min_per_km': 5.5,
            'is_complete': False,
        })
    return aggs


def _milestone_marker_names(chart):
    return {
        s.name()
        for s in chart.chart.series()
        if isinstance(s, QScatterSeries) and s.name()
    }


class TestProjectionChartMilestoneSkipping(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def setUp(self):
        self.chart = ProjectionChart()
        self.chart.projection_mode = 'long_run'

    def test_skip_milestone_already_passed_in_complete_history(self):
        # Long-run grew 8 → 16 across complete weeks; the runner has
        # clearly passed 10K and 15K. The projected trend, extrapolated,
        # will eventually pass Half Marathon, so HM should still show.
        # But the chart must not advertise 10K Run or 15K Run as future
        # milestones — they're history.
        self.chart.update_chart(
            _weekly_aggs([8, 10, 12, 13, 14, 15, 16, 16]),
            period_type='week',
        )
        names = _milestone_marker_names(self.chart)
        for already_done in ('10K Run', '15K Run'):
            self.assertNotIn(
                already_done, names,
                f"{already_done} marker must not appear when the runner "
                f"already exceeded that distance in complete weeks.",
            )

    def test_skip_milestone_passed_in_in_progress_week(self):
        # Past completed weeks topped out at 12 km, but the in-progress
        # current week has a 17 km long run. "15K Run" must NOT appear
        # as a future target — the runner already did it, even though
        # the chart line itself only draws completed weeks.
        self.chart.update_chart(
            _weekly_aggs(
                [6, 8, 8, 10, 10, 11, 12, 12],
                current_week_longest=17.1,
            ),
            period_type='week',
        )
        names = _milestone_marker_names(self.chart)
        self.assertNotIn(
            '15K Run', names,
            "15K Run marker must be suppressed once any aggregate — "
            "incomplete current week included — exceeds 15 km.",
        )
        self.assertNotIn('10K Run', names)

    def test_keep_future_milestones_above_max(self):
        # Runner topped out at 11 km on a gentle upward trend. The
        # projection extends 20 future weeks at ~+1 km/week, so it
        # clearly crosses the 15K Run milestone — that marker MUST
        # still appear.
        self.chart.periods_ahead = 20
        self.chart.update_chart(
            _weekly_aggs([4, 5, 6, 7, 8, 9, 10, 11]),
            period_type='week',
        )
        names = _milestone_marker_names(self.chart)
        self.assertIn(
            '15K Run', names,
            "15K Run must still appear when historical max is below 15 "
            "and the projection extends past it.",
        )


if __name__ == '__main__':
    unittest.main()
