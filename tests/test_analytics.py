"""
Unit tests for analytics module.
"""
import unittest
from datetime import datetime, timedelta
from app.analytics.aggregator import ActivityAggregator
from app.analytics.smoothing import Smoother
from app.analytics.training_score import TrainingScoreCalculator


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


class TestSmoother(unittest.TestCase):
    """Test smoothing algorithms."""

    def test_simple_moving_average(self):
        """Test simple moving average."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        smoothed = Smoother.simple_moving_average(data, 3)

        self.assertEqual(len(smoothed), len(data))
        # Middle values should be averages
        self.assertAlmostEqual(smoothed[4], 4.0, places=1)

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


if __name__ == '__main__':
    unittest.main()
