"""
Unit tests for DataManager.
"""
import time
import unittest
from datetime import datetime, timedelta

from run_trend.analytics.data_manager import DataManager


def _make_activities(num_weeks: int, runs_per_week: int = 3, distance_m: float = 10000.0):
    """Build a list of fake activity dicts spread over *num_weeks* complete weeks."""
    activities = []
    # Start on a Monday so each group of days falls neatly in one ISO week.
    base = datetime(2023, 1, 2, 8, 0, 0)  # Monday 2023-01-02
    strava_id = 0
    for week in range(num_weeks):
        for day in range(runs_per_week):
            activity_date = base + timedelta(weeks=week, days=day)
            activities.append({
                'strava_id': strava_id,
                'name': f'Run w{week}d{day}',
                'type': 'Run',
                'start_date': activity_date.isoformat() + 'Z',
                'distance': distance_m + week * 500,
                'moving_time': 3600,
                'average_speed': 2.78,
                'average_heartrate': 145.0,
                'max_heartrate': 170.0,
                'has_heartrate': True,
            })
            strava_id += 1
    return activities


class TestDataManagerBuildAggregates(unittest.TestCase):

    def setUp(self):
        self.activities_6w  = _make_activities(6)
        self.activities_10w = _make_activities(10)

    # ------------------------------------------------------------------
    # Basic structure
    # ------------------------------------------------------------------

    def test_week_aggregates_not_empty(self):
        result = DataManager.build_aggregates(self.activities_6w, period='week')
        self.assertGreater(len(result), 0)

    def test_week_aggregates_have_required_fields(self):
        result = DataManager.build_aggregates(self.activities_6w, period='week')
        agg = result[0]
        for field in ('period', 'period_date', 'total_distance_km', 'num_runs'):
            self.assertIn(field, agg, f"Missing field: {field}")

    def test_month_aggregates_not_empty(self):
        # Need activities spread over several months
        activities = _make_activities(12)
        result = DataManager.build_aggregates(activities, period='month')
        self.assertGreater(len(result), 0)

    def test_month_aggregates_fewer_than_week(self):
        activities = _make_activities(12)
        week_result  = DataManager.build_aggregates(activities, period='week')
        month_result = DataManager.build_aggregates(activities, period='month')
        self.assertLess(len(month_result), len(week_result))

    # ------------------------------------------------------------------
    # Empty input
    # ------------------------------------------------------------------

    def test_empty_activities_returns_empty_list(self):
        result = DataManager.build_aggregates([], period='week')
        self.assertEqual(result, [])

    def test_empty_activities_does_not_raise(self):
        try:
            DataManager.build_aggregates([], period='month')
        except Exception as e:
            self.fail(f"build_aggregates([]) raised unexpectedly: {e}")

    # ------------------------------------------------------------------
    # Training scores
    # ------------------------------------------------------------------

    def test_training_scores_present_on_aggregates(self):
        result = DataManager.build_aggregates(self.activities_10w, period='week')
        for agg in result:
            self.assertIn('training_score', agg, "training_score missing from aggregate")

    def test_training_scores_in_valid_range(self):
        result = DataManager.build_aggregates(self.activities_10w, period='week')
        for agg in result:
            score = agg.get('training_score', 0)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    # ------------------------------------------------------------------
    # Training load
    # ------------------------------------------------------------------

    def test_first_4_complete_aggregates_have_no_training_load(self):
        result   = DataManager.build_aggregates(self.activities_10w, period='week')
        complete = [agg for agg in result if agg.get('is_complete', True)]
        for agg in complete[:4]:
            self.assertNotIn('training_load', agg,
                             "First 4 complete aggregates must not have training_load")

    def test_training_load_present_from_5th_complete_aggregate(self):
        result   = DataManager.build_aggregates(self.activities_10w, period='week')
        complete = [agg for agg in result if agg.get('is_complete', True)]
        self.assertGreaterEqual(len(complete), 5,
                                "Need at least 5 complete weeks to test training_load")
        for agg in complete[4:]:
            self.assertIn('training_load', agg,
                          "Complete aggregates from index 4 onwards must have training_load")
            self.assertTrue(agg['training_load'].get('has_load', False),
                            "training_load.has_load should be True")

    def test_incomplete_period_has_no_training_load(self):
        # The last aggregate is the current (incomplete) period.
        # Build more weeks so we definitely have an incomplete tail.
        activities = _make_activities(8)
        # Add one activity in a future partial week
        last = activities[-1]
        partial_date = datetime.fromisoformat(last['start_date'].rstrip('Z')) + timedelta(weeks=1)
        activities.append({
            **last,
            'strava_id': 9999,
            'start_date': partial_date.isoformat() + 'Z',
        })
        result = DataManager.build_aggregates(activities, period='week')
        incomplete = [agg for agg in result if not agg.get('is_complete', True)]
        for agg in incomplete:
            self.assertNotIn('training_load', agg,
                             "Incomplete period must not have training_load")

    # ------------------------------------------------------------------
    # Performance: O(n) not O(n²)
    # ------------------------------------------------------------------

    def test_build_aggregates_is_fast_for_large_dataset(self):
        """50 weeks of data should complete in well under 1 second."""
        activities = _make_activities(50)
        start = time.time()
        DataManager.build_aggregates(activities, period='week')
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0,
                        f"build_aggregates took {elapsed:.2f}s — possible O(n²) regression")


class TestDataManagerPrivateLoad(unittest.TestCase):
    """Tests for the internal _calculate_all_training_loads helper."""

    def _make_aggregates(self, n: int, all_complete: bool = True):
        from datetime import datetime, timezone
        base = datetime(2023, 1, 2, tzinfo=timezone.utc)
        return [
            {
                'period': f'2023-W{i+1:02d}',
                'period_date': base + timedelta(weeks=i),
                'total_distance_km': 30.0 + i,
                'num_runs': 3,
                'is_complete': True if all_complete or i < n - 1 else False,
                'training_score': 50.0,
            }
            for i in range(n)
        ]

    def test_no_load_below_5_periods(self):
        aggs = self._make_aggregates(4)
        DataManager._calculate_all_training_loads(aggs)
        for agg in aggs:
            self.assertNotIn('training_load', agg)

    def test_load_from_5th_period(self):
        aggs = self._make_aggregates(7)
        DataManager._calculate_all_training_loads(aggs)
        # First 4: no load
        for agg in aggs[:4]:
            self.assertNotIn('training_load', agg)
        # From 5th onwards: has load
        for agg in aggs[4:]:
            self.assertIn('training_load', agg)


class TestAlignPreviousYearAggregates(unittest.TestCase):
    """Tests for DataManager.align_previous_year_aggregates."""

    def test_empty_returns_empty(self):
        self.assertEqual(DataManager.align_previous_year_aggregates([]), [])

    def test_weekly_shifts_by_52_weeks(self):
        aggs = [
            {'period': '2024-W01', 'period_date': datetime(2024, 1, 1), 'total_distance_km': 30.0},
            {'period': '2024-W02', 'period_date': datetime(2024, 1, 8), 'total_distance_km': 35.0},
        ]
        shifted = DataManager.align_previous_year_aggregates(aggs, period='week')
        self.assertEqual(shifted[0]['period_date'], datetime(2024, 1, 1) + timedelta(weeks=52))
        self.assertEqual(shifted[1]['period_date'], datetime(2024, 1, 8) + timedelta(weeks=52))
        # Other fields preserved.
        self.assertEqual(shifted[0]['total_distance_km'], 30.0)
        self.assertEqual(shifted[0]['period'], '2024-W01')

    def test_weekly_preserves_monday_alignment(self):
        # 2024-01-01 is a Monday — 52 weeks later (2024-12-30) must also be Monday.
        aggs = [{'period_date': datetime(2024, 1, 1)}]
        shifted = DataManager.align_previous_year_aggregates(aggs, period='week')
        self.assertEqual(shifted[0]['period_date'].weekday(), 0)

    def test_monthly_jumps_to_next_calendar_year(self):
        aggs = [
            {'period_date': datetime(2023, 3, 1)},
            {'period_date': datetime(2023, 11, 1)},
        ]
        shifted = DataManager.align_previous_year_aggregates(aggs, period='month')
        self.assertEqual(shifted[0]['period_date'], datetime(2024, 3, 1))
        self.assertEqual(shifted[1]['period_date'], datetime(2024, 11, 1))

    def test_monthly_feb_29_falls_back_to_feb_28(self):
        aggs = [{'period_date': datetime(2024, 2, 29)}]  # 2025 is not a leap year
        shifted = DataManager.align_previous_year_aggregates(aggs, period='month')
        self.assertEqual(shifted[0]['period_date'], datetime(2025, 2, 28))

    def test_does_not_mutate_input(self):
        original_date = datetime(2024, 1, 1)
        aggs = [{'period_date': original_date, 'total_distance_km': 30.0}]
        DataManager.align_previous_year_aggregates(aggs, period='week')
        self.assertEqual(aggs[0]['period_date'], original_date)


if __name__ == '__main__':
    unittest.main()
