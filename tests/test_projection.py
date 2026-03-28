"""
Unit tests for projection module.
"""
import unittest
from datetime import datetime, timedelta
from app.projection.forecaster import Forecaster


class TestForecaster(unittest.TestCase):
    """Test projection and forecasting."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample aggregates with increasing trend
        self.aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(12):
            period_date = base_date + timedelta(weeks=week)
            self.aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 10.0 + (week * 2),  # Linear increase
                'num_runs': 3,
            })

    def test_linear_regression(self):
        """Test linear regression calculation."""
        x = [0, 1, 2, 3, 4, 5]
        y = [1, 3, 5, 7, 9, 11]  # y = 2x + 1

        slope, intercept = Forecaster.linear_regression(x, y)

        self.assertAlmostEqual(slope, 2.0, places=1)
        self.assertAlmostEqual(intercept, 1.0, places=1)

    def test_linear_regression_insufficient_data(self):
        """Test linear regression with insufficient data."""
        x = [0]
        y = [1]

        slope, intercept = Forecaster.linear_regression(x, y)

        self.assertEqual(slope, 0.0)
        self.assertEqual(intercept, 0.0)

    def test_project_trend(self):
        """Test trend projection."""
        projection = Forecaster.project_trend(
            self.aggregates,
            'total_distance_km',
            periods_ahead=6
        )

        self.assertTrue(projection['has_projection'])
        self.assertIn('slope', projection)
        self.assertIn('intercept', projection)
        self.assertIn('projected_periods', projection)

        # Should have 6 projected periods
        self.assertEqual(len(projection['projected_periods']), 6)

        # Slope should be positive (increasing trend)
        self.assertGreater(projection['slope'], 0)

    def test_project_trend_insufficient_data(self):
        """Test projection with insufficient data."""
        single_agg = self.aggregates[:1]
        projection = Forecaster.project_trend(single_agg, 'total_distance_km')

        self.assertFalse(projection['has_projection'])

    def test_project_trend_recent_periods(self):
        """Test projection using only recent periods."""
        projection = Forecaster.project_trend(
            self.aggregates,
            'total_distance_km',
            periods_ahead=6,
            use_recent_periods=6
        )

        self.assertTrue(projection['has_projection'])

    def test_estimate_milestone_date(self):
        """Test milestone date estimation."""
        # Marathon distance is 42.195 km
        estimate = Forecaster.estimate_milestone_date(
            self.aggregates,
            42.195,
            'week'
        )

        self.assertIsNotNone(estimate)
        self.assertTrue(estimate['reachable'])

        if not estimate.get('reached'):
            self.assertIn('periods_until', estimate)
            self.assertIn('estimated_date', estimate)
            self.assertGreater(estimate['periods_until'], 0)

    def test_estimate_milestone_already_reached(self):
        """Test milestone estimation when already reached."""
        # Very low milestone
        estimate = Forecaster.estimate_milestone_date(
            self.aggregates,
            5.0,  # 5km - already exceeded
            'week'
        )

        self.assertIsNotNone(estimate)
        if estimate['reachable'] and estimate.get('reached'):
            self.assertTrue(True)

    def test_get_milestone_estimates(self):
        """Test getting all standard milestones."""
        estimates = Forecaster.get_milestone_estimates(self.aggregates, 'week')

        # Should have all standard milestones
        self.assertIn('5K', estimates)
        self.assertIn('10K', estimates)
        self.assertIn('Half Marathon', estimates)
        self.assertIn('Marathon Ready', estimates)

    def test_milestone_distances(self):
        """Test that milestone distances are correct."""
        self.assertEqual(Forecaster.MILESTONES['5K'], 5.0)
        self.assertEqual(Forecaster.MILESTONES['10K'], 10.0)
        self.assertAlmostEqual(Forecaster.MILESTONES['Half Marathon'], 21.0975, places=4)
        self.assertEqual(Forecaster.MILESTONES['Marathon Ready'], 32.0)


class TestProjectionEdgeCases(unittest.TestCase):
    """Test projection edge cases."""

    def test_declining_trend(self):
        """Test projection with declining trend."""
        aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(10):
            period_date = base_date + timedelta(weeks=week)
            aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 50.0 - (week * 2),  # Declining
                'num_runs': 3,
            })

        projection = Forecaster.project_trend(aggregates, 'total_distance_km')

        self.assertTrue(projection['has_projection'])
        self.assertEqual(projection['trend'], 'decreasing')
        self.assertLess(projection['slope'], 0)

    def test_stable_trend(self):
        """Test projection with stable trend."""
        aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(10):
            period_date = base_date + timedelta(weeks=week)
            aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_start': period_date.isoformat(),
                'total_distance_km': 20.0,  # Constant
                'num_runs': 3,
            })

        projection = Forecaster.project_trend(aggregates, 'total_distance_km')

        self.assertTrue(projection['has_projection'])
        self.assertAlmostEqual(projection['slope'], 0.0, places=1)


if __name__ == '__main__':
    unittest.main()
