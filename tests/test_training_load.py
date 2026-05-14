"""
Unit tests for training load calculation module.
"""
import unittest
from datetime import date, datetime, timedelta
from run_trend.analytics.training_load import (
    TrainingLoadCalculator,
    daily_acwr_series,
    daily_distance_loads,
    latest_acwr,
)


class TestTrainingLoadCalculator(unittest.TestCase):
    """Test ACWR (Acute:Chronic Workload Ratio) calculation."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample aggregates with 8 weeks of data (complete periods only)
        self.aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(8):
            period_date = base_date + timedelta(weeks=week)
            self.aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'period_start': period_date.isoformat(),
                'total_distance_km': 20.0 + (week * 2),  # Gradually increasing
                'weighted_avg_pace_min_per_km': 6.0,  # Constant pace
                'avg_heartrate': 150.0,  # Constant HR
                'num_runs': 3,
                'is_complete': True
            })

    def test_calculate_acwr_basic(self):
        """Test basic ACWR calculation."""
        result = TrainingLoadCalculator.calculate_acwr(
            self.aggregates,
            'total_distance_km',
            invert=False
        )

        self.assertTrue(result['has_acwr'])
        self.assertGreater(result['acwr'], 0)
        self.assertIn('status', result)
        self.assertIn('acute_value', result)
        self.assertIn('chronic_avg', result)

    def test_calculate_acwr_insufficient_data(self):
        """Test ACWR with insufficient data (< 5 weeks)."""
        # Only 4 weeks
        result = TrainingLoadCalculator.calculate_acwr(
            self.aggregates[:4],
            'total_distance_km',
            invert=False
        )

        self.assertFalse(result['has_acwr'])
        self.assertEqual(result['acwr'], 0.0)
        self.assertIn('message', result)

    def test_calculate_acwr_pace_inversion(self):
        """Test ACWR calculation with pace inversion."""
        result = TrainingLoadCalculator.calculate_acwr(
            self.aggregates,
            'weighted_avg_pace_min_per_km',
            invert=True
        )

        self.assertTrue(result['has_acwr'])
        # With constant pace, ACWR should be ~1.0
        self.assertAlmostEqual(result['acwr'], 1.0, places=1)

    def test_calculate_acwr_zero_values(self):
        """Test ACWR with zero values (should fail gracefully)."""
        # Create aggregates with zero distance
        zero_aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(5):
            period_date = base_date + timedelta(weeks=week)
            zero_aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'total_distance_km': 0.0,  # Zero distance
                'is_complete': True
            })

        result = TrainingLoadCalculator.calculate_acwr(
            zero_aggregates,
            'total_distance_km',
            invert=False
        )

        self.assertFalse(result['has_acwr'])
        self.assertIn('Missing data', result['message'])

    def test_calculate_acwr_status_safe(self):
        """Test ACWR status classification - safe zone."""
        # Create aggregates with ACWR in safe zone (0.8-1.3)
        safe_aggregates = []
        base_date = datetime(2024, 1, 1)

        # Create 5 weeks with stable workload
        for week in range(5):
            period_date = base_date + timedelta(weeks=week)
            safe_aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'total_distance_km': 20.0,  # Constant
                'is_complete': True
            })

        result = TrainingLoadCalculator.calculate_acwr(
            safe_aggregates,
            'total_distance_km',
            invert=False
        )

        self.assertTrue(result['has_acwr'])
        self.assertEqual(result['status'], 'safe')
        self.assertAlmostEqual(result['acwr'], 1.0, places=1)

    def test_calculate_acwr_status_danger(self):
        """Test ACWR status classification - danger zone."""
        # Create aggregates with sudden spike (ACWR > 1.5)
        danger_aggregates = []
        base_date = datetime(2024, 1, 1)

        # 4 weeks baseline
        for week in range(4):
            period_date = base_date + timedelta(weeks=week)
            danger_aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'total_distance_km': 20.0,
                'is_complete': True
            })

        # Acute week with 2x workload
        acute_date = base_date + timedelta(weeks=4)
        danger_aggregates.append({
            'period': '2024-W05',
            'period_date': acute_date,
            'total_distance_km': 40.0,  # Spike
            'is_complete': True
        })

        result = TrainingLoadCalculator.calculate_acwr(
            danger_aggregates,
            'total_distance_km',
            invert=False
        )

        self.assertTrue(result['has_acwr'])
        self.assertEqual(result['status'], 'danger')
        self.assertGreater(result['acwr'], 1.5)

    def test_calculate_training_load_basic(self):
        """Test composite training load score calculation."""
        result = TrainingLoadCalculator.calculate_training_load(self.aggregates)

        self.assertTrue(result['has_load'])
        self.assertGreater(result['training_load'], 0)
        self.assertLessEqual(result['training_load'], 100)
        self.assertIn('status', result)
        self.assertIn('message', result)
        self.assertIn('components', result)

    def test_calculate_training_load_insufficient_data(self):
        """Test training load with insufficient data."""
        result = TrainingLoadCalculator.calculate_training_load(self.aggregates[:4])

        self.assertFalse(result['has_load'])
        self.assertEqual(result['training_load'], 0.0)
        self.assertEqual(result['status'], 'insufficient_data')

    def test_calculate_training_load_without_hr(self):
        """Test training load calculation without heart rate data."""
        # Create aggregates without HR data
        no_hr_aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(5):
            period_date = base_date + timedelta(weeks=week)
            no_hr_aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'total_distance_km': 20.0,
                'weighted_avg_pace_min_per_km': 6.0,
                'avg_heartrate': 0,  # No HR data
                'is_complete': True
            })

        result = TrainingLoadCalculator.calculate_training_load(no_hr_aggregates)

        self.assertTrue(result['has_load'])
        self.assertFalse(result['components']['has_hr_data'])
        # HR ACWR defaults to 1.0 (neutral) when no HR data
        self.assertEqual(result['components']['hr_acwr'], 1.0)
        # Should still calculate using distance and pace
        self.assertGreater(result['training_load'], 0)

    def test_calculate_training_load_components(self):
        """Test that training load includes all components."""
        result = TrainingLoadCalculator.calculate_training_load(self.aggregates)

        self.assertTrue(result['has_load'])
        components = result['components']

        self.assertIn('distance_acwr', components)
        self.assertIn('pace_acwr', components)
        self.assertIn('hr_acwr', components)
        self.assertIn('has_hr_data', components)

        # All ACWRs should be > 0
        self.assertGreater(components['distance_acwr'], 0)
        self.assertGreater(components['pace_acwr'], 0)
        # HR ACWR should be > 0 if has_hr_data is True
        if components['has_hr_data']:
            self.assertGreater(components['hr_acwr'], 0)

    def test_calculate_training_load_score_mapping(self):
        """Test training load score mapping to 0-100 range."""
        # Create aggregates with ideal workload (ACWR ~ 1.0)
        ideal_aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(5):
            period_date = base_date + timedelta(weeks=week)
            ideal_aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'total_distance_km': 20.0,  # Constant
                'weighted_avg_pace_min_per_km': 6.0,  # Constant
                'avg_heartrate': 150.0,  # Constant
                'is_complete': True
            })

        result = TrainingLoadCalculator.calculate_training_load(ideal_aggregates)

        self.assertTrue(result['has_load'])
        # Ideal workload (ACWR ~1.0) should give score ~50
        self.assertGreater(result['training_load'], 40)
        self.assertLess(result['training_load'], 60)
        self.assertEqual(result['status'], 'safe')

    def test_calculate_training_load_status_safe(self):
        """Test training load status classification - safe."""
        result = TrainingLoadCalculator.calculate_training_load(self.aggregates)

        # Gradual increase should be safe
        self.assertTrue(result['has_load'])
        self.assertIn(result['status'], ['safe', 'caution'])
        self.assertLess(result['training_load'], 80)

    def test_calculate_training_load_status_warning(self):
        """Test training load status classification - warning."""
        # Create aggregates with significant spike
        warning_aggregates = []
        base_date = datetime(2024, 1, 1)

        # 4 weeks baseline
        for week in range(4):
            period_date = base_date + timedelta(weeks=week)
            warning_aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'total_distance_km': 20.0,
                'weighted_avg_pace_min_per_km': 6.0,
                'avg_heartrate': 150.0,
                'is_complete': True
            })

        # Acute week with dramatic spike (2x baseline)
        acute_date = base_date + timedelta(weeks=4)
        warning_aggregates.append({
            'period': '2024-W05',
            'period_date': acute_date,
            'total_distance_km': 50.0,  # 2.5x spike
            'weighted_avg_pace_min_per_km': 5.0,  # Much faster pace
            'avg_heartrate': 165.0,  # Significantly higher HR
            'is_complete': True
        })

        result = TrainingLoadCalculator.calculate_training_load(warning_aggregates)

        self.assertTrue(result['has_load'])
        # Dramatic spike should trigger caution, warning, or danger
        self.assertIn(result['status'], ['caution', 'warning', 'danger'])
        self.assertGreater(result['training_load'], 65)

    def test_calculate_training_load_missing_pace_data(self):
        """Test training load with missing pace data."""
        # Create aggregates without pace
        no_pace_aggregates = []
        base_date = datetime(2024, 1, 1)

        for week in range(5):
            period_date = base_date + timedelta(weeks=week)
            no_pace_aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'total_distance_km': 20.0,
                'weighted_avg_pace_min_per_km': 0.0,  # Missing pace
                'avg_heartrate': 150.0,
                'is_complete': True
            })

        result = TrainingLoadCalculator.calculate_training_load(no_pace_aggregates)

        # Should fail because pace is required
        self.assertFalse(result['has_load'])
        self.assertIn('Missing distance or pace data', result['message'])

    def test_get_explanation(self):
        """Test training load explanation."""
        explanation = TrainingLoadCalculator.get_explanation()

        self.assertIsInstance(explanation, str)
        self.assertGreater(len(explanation), 0)
        self.assertIn('ACWR', explanation)
        self.assertIn('Training Load', explanation)

    def test_acwr_thresholds(self):
        """Test that ACWR threshold constants are correctly defined."""
        self.assertEqual(TrainingLoadCalculator.ACWR_SAFE_MIN, 0.8)
        self.assertEqual(TrainingLoadCalculator.ACWR_SAFE_MAX, 1.3)
        self.assertEqual(TrainingLoadCalculator.ACWR_CAUTION_MAX, 1.5)
        self.assertEqual(TrainingLoadCalculator.ACWR_DANGER, 1.5)

    def test_component_weights(self):
        """Test that component weights sum to 1.0."""
        total_weight = (
            TrainingLoadCalculator.WEIGHT_DISTANCE +
            TrainingLoadCalculator.WEIGHT_PACE +
            TrainingLoadCalculator.WEIGHT_HR
        )
        self.assertAlmostEqual(total_weight, 1.0, places=2)

    def test_calculate_training_load_edge_case_undertraining(self):
        """Test training load with decreasing workload (undertraining)."""
        # Create aggregates with decreasing workload
        undertraining_aggregates = []
        base_date = datetime(2024, 1, 1)

        # 4 weeks baseline
        for week in range(4):
            period_date = base_date + timedelta(weeks=week)
            undertraining_aggregates.append({
                'period': f'2024-W{week + 1:02d}',
                'period_date': period_date,
                'total_distance_km': 40.0,  # Higher baseline
                'weighted_avg_pace_min_per_km': 6.0,
                'avg_heartrate': 150.0,
                'is_complete': True
            })

        # Acute week with significant drop
        acute_date = base_date + timedelta(weeks=4)
        undertraining_aggregates.append({
            'period': '2024-W05',
            'period_date': acute_date,
            'total_distance_km': 20.0,  # 50% drop
            'weighted_avg_pace_min_per_km': 6.0,
            'avg_heartrate': 150.0,
            'is_complete': True
        })

        result = TrainingLoadCalculator.calculate_training_load(undertraining_aggregates)

        self.assertTrue(result['has_load'])
        # Significant drop should result in low training load
        self.assertLess(result['training_load'], 50)
        self.assertIn(result['status'], ['undertraining', 'safe'])


class TestDailyAcwrSeries(unittest.TestCase):
    """T40 — daily-rolling Gabbett ACWR over a {date: load} map."""

    def test_constant_load_converges_to_one(self):
        # 60 days of constant 50 TRIMP/day → after the chronic window
        # is fully populated, acute and chronic match → ACWR = 1.0.
        start = date(2026, 1, 1)
        loads = {start + timedelta(days=i): 50.0 for i in range(60)}
        series = daily_acwr_series(loads)
        self.assertEqual(len(series), 60)
        # First 27 days: cold-start, no ACWR.
        for entry in series[:27]:
            self.assertFalse(entry['has_acwr'])
            self.assertIsNone(entry['acwr'])
        # Day 28 onwards: ACWR present and right around 1.0.
        for entry in series[27:]:
            self.assertTrue(entry['has_acwr'])
            self.assertAlmostEqual(entry['acwr'], 1.0, places=6)
            self.assertEqual(entry['status'], 'safe')

    def test_spike_pushes_acwr_into_danger(self):
        # 28 days at 50 to populate chronic, then 7 days at 200 — acute
        # quadruples while chronic only crawls up → ACWR climbs > 1.5
        # by the end of the spike week.
        start = date(2026, 1, 1)
        loads = {}
        for i in range(28):
            loads[start + timedelta(days=i)] = 50.0
        for i in range(28, 35):
            loads[start + timedelta(days=i)] = 200.0
        series = daily_acwr_series(loads)
        # Last day's ACWR: acute = 7*200 = 1400; chronic = (21*50 + 7*200)/4 = (1050+1400)/4 = 612.5
        # acwr = 1400 / 612.5 ≈ 2.286 → danger.
        last = series[-1]
        self.assertTrue(last['has_acwr'])
        self.assertGreater(last['acwr'], 1.5)
        self.assertEqual(last['status'], 'danger')

    def test_taper_drives_acute_to_zero(self):
        # 28 days at 50, then 7 days of rest → acute crashes to 0,
        # chronic still > 0 → ACWR = 0 → status 'undertraining'.
        start = date(2026, 1, 1)
        loads = {start + timedelta(days=i): 50.0 for i in range(28)}
        # 7 days of complete rest follow (no key in dict → 0).
        series = daily_acwr_series(loads, end=start + timedelta(days=34))
        last = series[-1]
        self.assertTrue(last['has_acwr'])
        self.assertEqual(last['acute'], 0)
        # chronic uses the trailing 28-day window: 21 days at 50 + 7 days at 0
        # → sum=1050, divided by 4 (chronic_window/acute_window) = 262.5
        self.assertAlmostEqual(last['chronic'], 262.5, places=4)
        self.assertEqual(last['acwr'], 0.0)
        self.assertEqual(last['status'], 'undertraining')

    def test_cold_start_returns_no_acwr(self):
        # Only 10 days of history → can never form a 28-day chronic
        # window → has_acwr stays False throughout.
        start = date(2026, 1, 1)
        loads = {start + timedelta(days=i): 50.0 for i in range(10)}
        series = daily_acwr_series(loads)
        self.assertEqual(len(series), 10)
        for entry in series:
            self.assertFalse(entry['has_acwr'])
            self.assertIsNone(entry['acwr'])
            self.assertIsNone(entry['status'])

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(daily_acwr_series({}), [])

    def test_explicit_end_extends_past_last_load(self):
        # Series can be asked to walk past the last known load — the
        # missing days are treated as zero, which is exactly the taper
        # scenario above.
        start = date(2026, 1, 1)
        loads = {start: 50.0}
        series = daily_acwr_series(
            loads,
            start=start,
            end=start + timedelta(days=4),
        )
        self.assertEqual(len(series), 5)
        # All within cold-start (< 28 days history).
        for entry in series:
            self.assertFalse(entry['has_acwr'])

    def test_custom_windows_supported(self):
        # 14-day chronic vs 7-day acute — same constant-load shape →
        # cold-start ends earlier, ACWR converges to 1.0.
        start = date(2026, 1, 1)
        loads = {start + timedelta(days=i): 50.0 for i in range(20)}
        series = daily_acwr_series(loads, acute_window=7, chronic_window=14)
        self.assertFalse(series[12]['has_acwr'])  # day 13: still cold
        self.assertTrue(series[13]['has_acwr'])   # day 14: chronic full
        self.assertAlmostEqual(series[-1]['acwr'], 1.0, places=6)


class TestLatestAcwr(unittest.TestCase):
    """T40 — single-day convenience wrapper."""

    def test_returns_last_day_record(self):
        start = date(2026, 1, 1)
        loads = {start + timedelta(days=i): 50.0 for i in range(35)}
        latest = latest_acwr(loads)
        self.assertTrue(latest['has_acwr'])
        self.assertAlmostEqual(latest['acwr'], 1.0, places=6)
        self.assertEqual(latest['status'], 'safe')

    def test_empty_input(self):
        result = latest_acwr({})
        self.assertFalse(result['has_acwr'])
        self.assertIsNone(result['acwr'])

    def test_cold_start_message(self):
        start = date(2026, 1, 1)
        loads = {start + timedelta(days=i): 50.0 for i in range(10)}
        result = latest_acwr(loads)
        self.assertFalse(result['has_acwr'])
        self.assertIn('28 days', result['message'])


class TestDailyDistanceLoads(unittest.TestCase):
    """T40 — fallback load source when HR / TRIMP isn't available."""

    def test_distance_aggregated_per_day_in_km(self):
        activities = [
            {'start_date': '2026-01-01T08:00:00', 'distance': 5000.0},
            {'start_date': '2026-01-01T18:00:00', 'distance': 3000.0},
            {'start_date': '2026-01-02T08:00:00', 'distance': 10000.0},
        ]
        out = daily_distance_loads(activities)
        self.assertAlmostEqual(out[date(2026, 1, 1)], 8.0, places=6)
        self.assertAlmostEqual(out[date(2026, 1, 2)], 10.0, places=6)

    def test_zero_or_missing_distance_skipped(self):
        activities = [
            {'start_date': '2026-01-01T08:00:00', 'distance': 0.0},
            {'start_date': '2026-01-01T18:00:00'},
            {'start_date': '2026-01-02T08:00:00', 'distance': 5000.0},
        ]
        out = daily_distance_loads(activities)
        self.assertNotIn(date(2026, 1, 1), out)
        self.assertAlmostEqual(out[date(2026, 1, 2)], 5.0, places=6)

    def test_bad_date_skipped(self):
        activities = [
            {'start_date': 'not-a-date', 'distance': 5000.0},
            {'start_date': '2026-01-02T08:00:00', 'distance': 5000.0},
        ]
        out = daily_distance_loads(activities)
        self.assertEqual(list(out.keys()), [date(2026, 1, 2)])


if __name__ == '__main__':
    unittest.main()
