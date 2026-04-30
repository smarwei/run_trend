"""
Unit tests for analytics module.
"""
import unittest
from datetime import datetime, timedelta
from run_trend.analytics.aggregator import ActivityAggregator
from run_trend.analytics.smoothing import Smoother
from run_trend.analytics.training_score import TrainingScoreCalculator


class TestActivityAggregator(unittest.TestCase):
    """Test activity aggregation."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_activities = []
        base_date = datetime(2024, 1, 1, 10, 0, 0)

        # Create sample activities over 4 weeks
        for week in range(4):
            for day in range(3):  # 3 runs per week
                activity_date = base_date + timedelta(weeks=week, days=day)
                self.sample_activities.append({
                    'strava_id': week * 10 + day,
                    'name': f'Run {week}-{day}',
                    'type': 'Run',
                    'start_date': activity_date.isoformat() + 'Z',
                    'distance': 5000.0 + (week * 1000),  # Increasing distance
                    'moving_time': 1800,  # 30 minutes
                    'average_speed': 2.78,  # ~10 km/h
                })

    def test_per_activity_metrics(self):
        """Test per-activity metrics calculation."""
        activity = self.sample_activities[0]
        metrics = ActivityAggregator.compute_per_activity_metrics(activity)

        self.assertAlmostEqual(metrics['distance_km'], 5.0, places=1)
        self.assertAlmostEqual(metrics['duration_min'], 30.0, places=1)
        self.assertGreater(metrics['pace_min_per_km'], 0)
        self.assertGreater(metrics['speed_kmh'], 0)

    def test_aggregate_by_week(self):
        """Test weekly aggregation."""
        aggregates = ActivityAggregator.aggregate_by_week(self.sample_activities)

        self.assertEqual(len(aggregates), 4)  # 4 weeks

        # Check first week
        first_week = aggregates[0]
        self.assertEqual(first_week['num_runs'], 3)
        self.assertAlmostEqual(first_week['total_distance_km'], 15.0, places=1)
        self.assertGreater(first_week['weighted_avg_pace_min_per_km'], 0)

    def test_aggregate_by_month(self):
        """Test monthly aggregation."""
        aggregates = ActivityAggregator.aggregate_by_month(self.sample_activities)

        self.assertEqual(len(aggregates), 1)  # All in same month

        first_month = aggregates[0]
        self.assertEqual(first_month['num_runs'], 12)
        self.assertGreater(first_month['total_distance_km'], 0)

    def test_empty_activities(self):
        """Test aggregation with empty activity list."""
        aggregates = ActivityAggregator.aggregate_by_week([])
        self.assertEqual(len(aggregates), 0)

    def test_weighted_pace_calculation(self):
        """Test that weighted pace is calculated correctly."""
        aggregates = ActivityAggregator.aggregate_by_week(self.sample_activities)

        for agg in aggregates:
            # Weighted pace should be total time / total distance
            if agg['total_distance_km'] > 0:
                expected_pace = agg['total_moving_time_min'] / agg['total_distance_km']
                self.assertAlmostEqual(
                    agg['weighted_avg_pace_min_per_km'],
                    expected_pace,
                    places=2
                )

    def test_duration_metrics(self):
        """Test that duration metrics are calculated correctly."""
        aggregates = ActivityAggregator.aggregate_by_week(self.sample_activities)

        for agg in aggregates:
            # Check that duration metrics exist
            self.assertIn('avg_duration_per_run_min', agg)
            self.assertIn('avg_duration_per_run_h', agg)
            self.assertIn('longest_duration_min', agg)
            self.assertIn('longest_duration_h', agg)
            self.assertIn('avg_long_run_duration_min', agg)
            self.assertIn('avg_long_run_duration_h', agg)

            # All duration metrics should be non-negative
            self.assertGreaterEqual(agg['avg_duration_per_run_min'], 0)
            self.assertGreaterEqual(agg['avg_duration_per_run_h'], 0)
            self.assertGreaterEqual(agg['longest_duration_min'], 0)
            self.assertGreaterEqual(agg['longest_duration_h'], 0)
            self.assertGreaterEqual(agg['avg_long_run_duration_min'], 0)
            self.assertGreaterEqual(agg['avg_long_run_duration_h'], 0)

            # Average duration should be total time / num runs
            num_runs = agg['num_runs']
            if num_runs > 0:
                expected_avg_min = agg['total_moving_time_min'] / num_runs
                expected_avg_h = agg['total_moving_time_h'] / num_runs
                self.assertAlmostEqual(
                    agg['avg_duration_per_run_min'],
                    expected_avg_min,
                    places=2
                )
                self.assertAlmostEqual(
                    agg['avg_duration_per_run_h'],
                    expected_avg_h,
                    places=4
                )

            # Longest duration should be >= average duration
            self.assertGreaterEqual(
                agg['longest_duration_min'],
                agg['avg_duration_per_run_min']
            )

            # Conversion between minutes and hours should be correct
            self.assertAlmostEqual(
                agg['avg_duration_per_run_h'] * 60,
                agg['avg_duration_per_run_min'],
                places=2
            )
            self.assertAlmostEqual(
                agg['longest_duration_h'] * 60,
                agg['longest_duration_min'],
                places=2
            )
            self.assertAlmostEqual(
                agg['avg_long_run_duration_h'] * 60,
                agg['avg_long_run_duration_min'],
                places=2
            )

    def test_long_run_duration_calculation(self):
        """Test that long run duration is calculated for top 30% runs."""
        # Create activities with varying durations
        activities = []
        base_date = datetime(2024, 1, 1, 10, 0, 0)

        # Create 10 runs with varying distances and times
        for i in range(10):
            activity_date = base_date + timedelta(days=i)
            activities.append({
                'strava_id': i,
                'name': f'Run {i}',
                'type': 'Run',
                'start_date': activity_date.isoformat() + 'Z',
                'distance': 5000.0 + (i * 1000),  # 5km to 14km
                'moving_time': 1800 + (i * 300),  # 30 to 75 minutes
                'average_speed': 2.78,
            })

        aggregates = ActivityAggregator.aggregate_by_week(activities)

        # Should have data since we have >= 3 runs
        self.assertGreater(len(aggregates), 0)
        agg = aggregates[0]

        # With 10 runs, top 30% = 3 runs (the longest ones by distance)
        # These would be runs 7, 8, 9 (12km, 13km, 14km)
        # Times: 3900s, 4200s, 4500s = 12600s total / 3 = 4200s = 70 minutes
        self.assertGreater(agg['avg_long_run_duration_min'], 0)
        # Should be higher than overall average since it's the longest runs
        self.assertGreater(
            agg['avg_long_run_duration_min'],
            agg['avg_duration_per_run_min']
        )

    def test_duration_metrics_with_few_runs(self):
        """Test duration metrics when there are fewer than 3 runs."""
        activities = []
        base_date = datetime(2024, 1, 1, 10, 0, 0)

        # Create only 2 runs
        for i in range(2):
            activity_date = base_date + timedelta(days=i)
            activities.append({
                'strava_id': i,
                'name': f'Run {i}',
                'type': 'Run',
                'start_date': activity_date.isoformat() + 'Z',
                'distance': 5000.0,
                'moving_time': 1800,
                'average_speed': 2.78,
            })

        aggregates = ActivityAggregator.aggregate_by_week(activities)

        self.assertGreater(len(aggregates), 0)
        agg = aggregates[0]

        # With < 3 runs, avg_long_run_duration should be 0
        self.assertEqual(agg['avg_long_run_duration_min'], 0.0)
        self.assertEqual(agg['avg_long_run_duration_h'], 0.0)

        # But other duration metrics should still work
        self.assertGreater(agg['avg_duration_per_run_min'], 0)
        self.assertGreater(agg['longest_duration_min'], 0)


class TestSmoother(unittest.TestCase):
    """Test smoothing algorithms."""

    def test_simple_moving_average(self):
        """Test simple moving average."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        smoothed = Smoother.simple_moving_average(data, 3)

        self.assertEqual(len(smoothed), len(data))
        # Implementation uses centered window: index 4 averages [4,5,6] = 5.0
        self.assertAlmostEqual(smoothed[4], 5.0, places=1)

    def test_exponential_moving_average(self):
        """Test exponential moving average."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        smoothed = Smoother.exponential_moving_average(data, 0.5)

        self.assertEqual(len(smoothed), len(data))
        # First value should be unchanged
        self.assertEqual(smoothed[0], 1)
        # Values should be smoothed
        self.assertLess(smoothed[1], 2)

    def test_smooth_series_sma(self):
        """Test smooth_series with SMA."""
        data = [10, 20, 30, 40, 50]
        smoothed = Smoother.smooth_series(data, 'sma', 'medium')

        self.assertEqual(len(smoothed), len(data))

    def test_smooth_series_ema(self):
        """Test smooth_series with EMA."""
        data = [10, 20, 30, 40, 50]
        smoothed = Smoother.smooth_series(data, 'ema', 'medium')

        self.assertEqual(len(smoothed), len(data))

    def test_smooth_series_off(self):
        """Test smooth_series with smoothing off."""
        data = [10, 20, 30, 40, 50]
        smoothed = Smoother.smooth_series(data, 'sma', 'off')

        self.assertEqual(smoothed, data)

    def test_empty_data(self):
        """Test smoothing with empty data."""
        smoothed = Smoother.simple_moving_average([], 3)
        self.assertEqual(smoothed, [])


class TestTrainingScoreCalculator(unittest.TestCase):
    """Test training score calculation."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample aggregates
        self.aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(10):
            period_date = base_date + timedelta(weeks=week)
            self.aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 20.0 + week,  # Increasing trend
                'num_runs': 3,
                'weighted_avg_pace_min_per_km': 6.0 - (week * 0.05),  # Improving pace
                'avg_speed_kmh': 10.0,
                'efficiency_factor': 0.018 + (week * 0.001),  # Improving efficiency
            })

    def test_calculate_scores(self):
        """Test score calculation."""
        scored = TrainingScoreCalculator.calculate_scores(self.aggregates)

        self.assertEqual(len(scored), len(self.aggregates))

        # All should have training_score
        for agg in scored:
            self.assertIn('training_score', agg)
            self.assertGreaterEqual(agg['training_score'], 0)
            self.assertLessEqual(agg['training_score'], 100)

    def test_score_components(self):
        """Test that score components are included."""
        scored = TrainingScoreCalculator.calculate_scores(self.aggregates)

        for agg in scored:
            self.assertIn('score_components', agg)
            components = agg['score_components']
            self.assertIn('normalized_distance', components)
            self.assertIn('normalized_frequency', components)
            self.assertIn('normalized_pace', components)
            self.assertIn('normalized_efficiency', components)
            self.assertIn('has_hr_data', components)

    def test_empty_aggregates(self):
        """Test with empty aggregates."""
        scored = TrainingScoreCalculator.calculate_scores([])
        self.assertEqual(scored, [])

    def test_insufficient_data(self):
        """Test with insufficient data."""
        single_agg = self.aggregates[:1]
        scored = TrainingScoreCalculator.calculate_scores(single_agg)
        self.assertEqual(scored, single_agg)

    def test_get_explanation(self):
        """Test score explanation."""
        explanation = TrainingScoreCalculator.get_score_explanation()
        self.assertIsInstance(explanation, str)
        self.assertGreater(len(explanation), 0)
        self.assertIn('training', explanation.lower())

    def test_score_contributions_with_hr(self):
        """Contributions sum to the training score; maxima sum to 100."""
        scored = TrainingScoreCalculator.calculate_scores(self.aggregates)
        agg = scored[-1]
        contributions = TrainingScoreCalculator.get_score_contributions(
            agg['score_components']
        )

        self.assertEqual(set(contributions.keys()),
                         {'distance', 'frequency', 'pace', 'efficiency'})
        for c in contributions.values():
            self.assertTrue(c['has_data'])

        max_total = sum(c['max'] for c in contributions.values())
        self.assertAlmostEqual(max_total, 100.0)

        contribution_total = sum(c['contribution'] for c in contributions.values())
        self.assertAlmostEqual(contribution_total, agg['training_score'], places=4)

    def test_score_contributions_without_hr(self):
        """Without HR data, efficiency is flagged absent and max still totals 100."""
        aggregates_no_hr = []
        base_date = datetime(2024, 1, 1)
        for week in range(5):
            period_date = base_date + timedelta(weeks=week)
            aggregates_no_hr.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 20.0 + week,
                'num_runs': 3,
                'weighted_avg_pace_min_per_km': 6.0 - (week * 0.05),
                'avg_speed_kmh': 10.0,
                'efficiency_factor': 0,
            })
        scored = TrainingScoreCalculator.calculate_scores(aggregates_no_hr)
        contributions = TrainingScoreCalculator.get_score_contributions(
            scored[-1]['score_components']
        )

        self.assertFalse(contributions['efficiency']['has_data'])
        self.assertEqual(contributions['efficiency']['max'], 0)
        self.assertAlmostEqual(
            contributions['distance']['max']
            + contributions['frequency']['max']
            + contributions['pace']['max'],
            100.0,
        )

    def test_score_contributions_empty(self):
        """Empty input returns empty dict, not an exception."""
        self.assertEqual(TrainingScoreCalculator.get_score_contributions({}), {})
        self.assertEqual(TrainingScoreCalculator.get_score_contributions(None), {})

    def test_ef_dropped_when_fewer_than_three_samples(self):
        """With < 3 EF samples in history, EF must not contribute to the score."""
        aggregates = []
        base_date = datetime(2024, 1, 1)
        # 5 weeks: only 2 of them carry HR-derived efficiency_factor.
        ef_values = [0.018, 0.0, 0.019, 0.0, 0.0]
        for week, ef in enumerate(ef_values):
            period_date = base_date + timedelta(weeks=week)
            aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 20.0 + week,
                'num_runs': 3,
                'weighted_avg_pace_min_per_km': 6.0 - (week * 0.05),
                'avg_speed_kmh': 10.0,
                'efficiency_factor': ef,
            })

        scored = TrainingScoreCalculator.calculate_scores(aggregates)
        # Even on the periods that *do* carry an EF value, the global
        # threshold is not reached so EF must not enter the score.
        for agg in scored:
            comps = agg['score_components']
            self.assertFalse(comps['has_hr_data'])
            self.assertEqual(comps['normalized_efficiency'], 0.0)

        # Re-normalised maxima still sum to 100.
        contributions = TrainingScoreCalculator.get_score_contributions(
            scored[-1]['score_components']
        )
        self.assertFalse(contributions['efficiency']['has_data'])
        self.assertEqual(contributions['efficiency']['max'], 0)
        self.assertAlmostEqual(
            contributions['distance']['max']
            + contributions['frequency']['max']
            + contributions['pace']['max'],
            100.0,
        )

    def test_ef_active_at_three_samples(self):
        """At exactly 3 EF samples in history, EF starts contributing."""
        aggregates = []
        base_date = datetime(2024, 1, 1)
        ef_values = [0.018, 0.019, 0.020, 0.0, 0.021]  # 4 valid samples
        for week, ef in enumerate(ef_values):
            period_date = base_date + timedelta(weeks=week)
            aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 20.0 + week,
                'num_runs': 3,
                'weighted_avg_pace_min_per_km': 6.0 - (week * 0.05),
                'avg_speed_kmh': 10.0,
                'efficiency_factor': ef,
            })
        scored = TrainingScoreCalculator.calculate_scores(aggregates)
        # Periods that themselves carry an EF value must now contribute it.
        last = scored[-1]
        self.assertTrue(last['score_components']['has_hr_data'])
        self.assertGreater(last['score_components']['normalized_efficiency'], 0.0)

    def test_no_arbitrary_default_baseline_for_efficiency(self):
        """Sparse EF history must not be papered over by a hardcoded baseline.

        Two athletes with identical volume/pace/frequency but different EF
        histories (none vs. plenty) should NOT produce identical scores via
        an injected baseline. With < 3 EF samples the component is dropped
        entirely; the score reflects only the available metrics.
        """
        # No EF data at all — replicates a fresh user without HR sensor.
        aggregates_no_ef = []
        base_date = datetime(2024, 1, 1)
        for week in range(5):
            period_date = base_date + timedelta(weeks=week)
            aggregates_no_ef.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 20.0 + week,
                'num_runs': 3,
                'weighted_avg_pace_min_per_km': 6.0 - (week * 0.05),
                'avg_speed_kmh': 10.0,
                'efficiency_factor': 0,
            })
        scored = TrainingScoreCalculator.calculate_scores(aggregates_no_ef)
        # All periods should report no EF and a renormalised score (no sneaky
        # 0.018 default leaking in).
        for agg in scored:
            self.assertFalse(agg['score_components']['has_hr_data'])
            self.assertEqual(agg['score_components']['normalized_efficiency'], 0.0)

    def test_fallback_without_hr_data(self):
        """Test that score calculation works without HR data."""
        # Create aggregates without efficiency_factor
        aggregates_no_hr = []
        base_date = datetime(2024, 1, 1)

        for week in range(5):
            period_date = base_date + timedelta(weeks=week)
            aggregates_no_hr.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 20.0 + week,
                'num_runs': 3,
                'weighted_avg_pace_min_per_km': 6.0 - (week * 0.05),
                'avg_speed_kmh': 10.0,
                'efficiency_factor': 0,  # No HR data
            })

        scored = TrainingScoreCalculator.calculate_scores(aggregates_no_hr)

        # Should still calculate scores
        self.assertEqual(len(scored), len(aggregates_no_hr))

        for agg in scored:
            self.assertIn('training_score', agg)
            self.assertGreaterEqual(agg['training_score'], 0)
            self.assertLessEqual(agg['training_score'], 100)
            # Should mark as no HR data
            self.assertFalse(agg['score_components']['has_hr_data'])
            # Efficiency should be 0
            self.assertEqual(agg['score_components']['normalized_efficiency'], 0.0)


class TestIncompletePeriodDetection(unittest.TestCase):
    """Test incomplete period detection functionality."""

    def test_is_period_complete_week_complete(self):
        """Test that a week in the past is detected as complete."""
        # Create a Monday from two weeks ago
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        # Get Monday of that week
        monday = two_weeks_ago - timedelta(days=two_weeks_ago.weekday())

        is_complete = ActivityAggregator.is_period_complete(monday, 'week')
        self.assertTrue(is_complete)

    def test_is_period_complete_week_incomplete(self):
        """Test that current week is detected as incomplete (if not Sunday)."""
        # Get Monday of current week
        today = datetime.now()
        monday_this_week = today - timedelta(days=today.weekday())

        is_complete = ActivityAggregator.is_period_complete(monday_this_week, 'week')

        # Should be incomplete unless today is Monday and past Sunday
        # If today is Sunday, the week might be complete
        if today.weekday() == 6:  # Sunday
            # Could be complete if we're at end of day
            pass  # Don't assert
        else:
            self.assertFalse(is_complete)

    def test_is_period_complete_month_complete(self):
        """Test that a month in the past is detected as complete."""
        # Create first day of last month
        today = datetime.now()
        if today.month == 1:
            last_month = datetime(today.year - 1, 12, 1)
        else:
            last_month = datetime(today.year, today.month - 1, 1)

        is_complete = ActivityAggregator.is_period_complete(last_month, 'month')
        self.assertTrue(is_complete)

    def test_is_period_complete_month_incomplete(self):
        """Test that current month is detected as incomplete."""
        # First day of current month
        today = datetime.now()
        current_month = datetime(today.year, today.month, 1)

        is_complete = ActivityAggregator.is_period_complete(current_month, 'month')
        self.assertFalse(is_complete)

    def test_mark_incomplete_periods_week(self):
        """Test that mark_incomplete_periods adds is_complete flag for weeks."""
        # Create sample aggregates with different dates
        aggregates = []

        # Add a week from last month (should be complete)
        last_month = datetime.now() - timedelta(weeks=4)
        monday_last_month = last_month - timedelta(days=last_month.weekday())
        aggregates.append({
            'period': '2024-W01',
            'period_date': monday_last_month,
            'total_distance_km': 20.0
        })

        # Add current week (should be incomplete)
        today = datetime.now()
        monday_this_week = today - timedelta(days=today.weekday())
        aggregates.append({
            'period': '2024-W10',
            'period_date': monday_this_week,
            'total_distance_km': 10.0
        })

        marked = ActivityAggregator.mark_incomplete_periods(aggregates, 'week')

        # Check that is_complete flag is added
        self.assertEqual(len(marked), 2)
        self.assertIn('is_complete', marked[0])
        self.assertIn('is_complete', marked[1])

        # First should be complete, second might not be
        self.assertTrue(marked[0]['is_complete'])

    def test_mark_incomplete_periods_month(self):
        """Test that mark_incomplete_periods adds is_complete flag for months."""
        # Create sample aggregates
        aggregates = []

        # Add last month (should be complete)
        today = datetime.now()
        if today.month == 1:
            last_month = datetime(today.year - 1, 12, 1)
        else:
            last_month = datetime(today.year, today.month - 1, 1)

        aggregates.append({
            'period': '2024-01',
            'period_date': last_month,
            'total_distance_km': 100.0
        })

        # Add current month (should be incomplete)
        current_month = datetime(today.year, today.month, 1)
        aggregates.append({
            'period': '2024-03',
            'period_date': current_month,
            'total_distance_km': 50.0
        })

        marked = ActivityAggregator.mark_incomplete_periods(aggregates, 'month')

        # Check that is_complete flag is added
        self.assertEqual(len(marked), 2)
        self.assertIn('is_complete', marked[0])
        self.assertIn('is_complete', marked[1])

        # First should be complete, second should be incomplete
        self.assertTrue(marked[0]['is_complete'])
        self.assertFalse(marked[1]['is_complete'])

    def test_mark_incomplete_periods_no_period_date(self):
        """Test backward compatibility when period_date is missing."""
        aggregates = [{
            'period': '2024-W01',
            'total_distance_km': 20.0
            # No period_date
        }]

        marked = ActivityAggregator.mark_incomplete_periods(aggregates, 'week')

        # Should default to complete for backward compatibility
        self.assertTrue(marked[0]['is_complete'])


if __name__ == '__main__':
    unittest.main()
