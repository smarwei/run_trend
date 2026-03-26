"""
Tests for heart rate metrics in aggregator.
"""
import unittest
from datetime import datetime, timedelta
from app.analytics.aggregator import ActivityAggregator


class TestHeartRateMetrics(unittest.TestCase):
    """Test heart rate metric calculations."""

    def setUp(self):
        """Set up test data."""
        # Create sample activities with heart rate data
        base_date = datetime(2024, 1, 1, 10, 0, 0)

        self.activities_with_hr = [
            {
                'strava_id': 1,
                'start_date': base_date.isoformat() + 'Z',
                'distance': 5000,  # 5 km
                'moving_time': 1800,  # 30 minutes
                'average_speed': 2.78,  # ~5:59 min/km
                'average_heartrate': 150,
                'max_heartrate': 165,
                'has_heartrate': True
            },
            {
                'strava_id': 2,
                'start_date': (base_date + timedelta(days=2)).isoformat() + 'Z',
                'distance': 10000,  # 10 km
                'moving_time': 3600,  # 60 minutes
                'average_speed': 2.78,
                'average_heartrate': 155,
                'max_heartrate': 170,
                'has_heartrate': True
            },
            {
                'strava_id': 3,
                'start_date': (base_date + timedelta(days=4)).isoformat() + 'Z',
                'distance': 7000,  # 7 km
                'moving_time': 2520,  # 42 minutes
                'average_speed': 2.78,
                'average_heartrate': 148,
                'max_heartrate': 162,
                'has_heartrate': True
            }
        ]

        self.activities_without_hr = [
            {
                'strava_id': 4,
                'start_date': base_date.isoformat() + 'Z',
                'distance': 5000,
                'moving_time': 1800,
                'average_speed': 2.78,
                'average_heartrate': None,
                'max_heartrate': None,
                'has_heartrate': False
            }
        ]

    def test_hr_metrics_with_data(self):
        """Test that HR metrics are calculated correctly when HR data is available."""
        aggregates = ActivityAggregator.aggregate_by_week(self.activities_with_hr)

        self.assertEqual(len(aggregates), 1, "Should have 1 weekly aggregate")

        agg = aggregates[0]

        # Check that HR metrics are present
        self.assertIn('avg_heartrate', agg)
        self.assertIn('min_avg_heartrate', agg)
        self.assertIn('max_heartrate', agg)
        self.assertIn('efficiency_factor', agg)
        self.assertIn('num_hr_activities', agg)

        # Verify values
        self.assertEqual(agg['num_hr_activities'], 3)
        self.assertAlmostEqual(agg['avg_heartrate'], (150 + 155 + 148) / 3, places=1)
        self.assertEqual(agg['min_avg_heartrate'], 148)
        self.assertEqual(agg['max_heartrate'], 170)  # Max of all max_heartrate values

        # Efficiency factor should be speed / HR
        expected_ef = 2.78 / ((150 + 155 + 148) / 3)
        self.assertAlmostEqual(agg['efficiency_factor'], expected_ef, places=3)

    def test_hr_metrics_without_data(self):
        """Test that HR metrics are zero when no HR data is available."""
        aggregates = ActivityAggregator.aggregate_by_week(self.activities_without_hr)

        self.assertEqual(len(aggregates), 1)

        agg = aggregates[0]

        # HR metrics should be zero/empty
        self.assertEqual(agg['avg_heartrate'], 0)
        self.assertEqual(agg['min_avg_heartrate'], 0)
        self.assertEqual(agg['max_heartrate'], 0)
        self.assertEqual(agg['efficiency_factor'], 0)
        self.assertEqual(agg['num_hr_activities'], 0)

    def test_efficiency_factor_calculation(self):
        """Test that efficiency factor is calculated correctly."""
        # EF = Speed (m/s) / Average HR
        # Higher EF = better aerobic fitness

        # Activity with good efficiency (low HR for given speed)
        good_efficiency = {
            'strava_id': 5,
            'start_date': datetime(2024, 1, 1).isoformat() + 'Z',
            'distance': 5000,
            'moving_time': 1800,
            'average_speed': 2.78,  # Same speed
            'average_heartrate': 140,  # Lower HR = better
            'max_heartrate': 155,
            'has_heartrate': True
        }

        # Activity with poor efficiency (high HR for given speed)
        poor_efficiency = {
            'strava_id': 6,
            'start_date': datetime(2024, 1, 8).isoformat() + 'Z',
            'distance': 5000,
            'moving_time': 1800,
            'average_speed': 2.78,  # Same speed
            'average_heartrate': 160,  # Higher HR = worse
            'max_heartrate': 175,
            'has_heartrate': True
        }

        good_agg = ActivityAggregator.aggregate_by_week([good_efficiency])
        poor_agg = ActivityAggregator.aggregate_by_week([poor_efficiency])

        good_ef = good_agg[0]['efficiency_factor']
        poor_ef = poor_agg[0]['efficiency_factor']

        # Better efficiency should have higher EF value
        self.assertGreater(good_ef, poor_ef,
                          "Lower HR at same speed should have higher efficiency factor")


if __name__ == '__main__':
    unittest.main()
