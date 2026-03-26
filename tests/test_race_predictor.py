"""
Tests for race time prediction module.
"""
import unittest
from datetime import datetime, timedelta, timezone
from app.analytics.race_predictor import RacePredictor


class TestRacePredictor(unittest.TestCase):
    """Test race time prediction functionality."""

    def setUp(self):
        """Set up test data."""
        # Create sample runs (timezone-aware)
        now = datetime.now(timezone.utc)

        self.runs = [
            # Easy runs (60-75% HRmax)
            {
                'distance_km': 10.0,
                'pace_min_per_km': 6.0,
                'average_heartrate': 140,  # 70% of 200
                'start_date': now.isoformat()
            },
            {
                'distance_km': 8.0,
                'pace_min_per_km': 6.2,
                'average_heartrate': 138,  # 69% of 200
                'start_date': (now - timedelta(days=7)).isoformat()
            },
            {
                'distance_km': 12.0,
                'pace_min_per_km': 5.8,
                'average_heartrate': 142,  # 71% of 200
                'start_date': (now - timedelta(days=14)).isoformat()
            },
            # Tempo run (too high HR)
            {
                'distance_km': 8.0,
                'pace_min_per_km': 5.0,
                'average_heartrate': 165,  # 82.5% of 200 - too high
                'start_date': (now - timedelta(days=3)).isoformat()
            },
            # Recovery run (too low HR)
            {
                'distance_km': 5.0,
                'pace_min_per_km': 7.0,
                'average_heartrate': 110,  # 55% of 200 - too low
                'start_date': (now - timedelta(days=5)).isoformat()
            },
            # Too short (< 5km)
            {
                'distance_km': 3.0,
                'pace_min_per_km': 6.0,
                'average_heartrate': 140,
                'start_date': now.isoformat()
            },
            # Old run (> 6 months)
            {
                'distance_km': 10.0,
                'pace_min_per_km': 7.0,
                'average_heartrate': 140,
                'start_date': (now - timedelta(days=200)).isoformat()
            }
        ]

        self.max_hr = 200

    def test_identify_easy_runs(self):
        """Test easy run identification."""
        easy_runs = RacePredictor.identify_easy_runs(self.runs, self.max_hr)

        # With 10% safety margin (200 * 1.10 = 220 bpm) and 60-75% zone:
        # - Run 1: 140/220 = 63.6% ✅
        # - Run 2: 138/220 = 62.7% ✅
        # - Run 3: 142/220 = 64.5% ✅
        # - Run 4: 165/220 = 75.0% ✅ (exactly at boundary)
        # - Run 5: 110/220 = 50% ❌ (too low)
        # - Run 6: 140/220 = 63.6%, 3km ✅ (MIN_DISTANCE = 3km)
        # - Run 7: Old ❌
        # Should find 5 easy runs
        self.assertEqual(len(easy_runs), 5)

        # Check that paces are correct
        paces = [run['pace_min_per_km'] for run in easy_runs]
        self.assertIn(6.0, paces)  # Run 1 and 6
        self.assertIn(6.2, paces)  # Run 2
        self.assertIn(5.8, paces)  # Run 3
        self.assertIn(5.0, paces)  # Run 4

    def test_identify_easy_runs_no_hrmax(self):
        """Test that no easy runs are found without HRmax."""
        easy_runs = RacePredictor.identify_easy_runs(self.runs, 0)
        self.assertEqual(len(easy_runs), 0)

    def test_calculate_median_easy_pace(self):
        """Test median easy pace calculation."""
        easy_runs = RacePredictor.identify_easy_runs(self.runs, self.max_hr)
        median_pace = RacePredictor.calculate_median_easy_pace(easy_runs)

        # Median of [5.0, 5.8, 6.0, 6.0, 6.2] should be 6.0
        self.assertEqual(median_pace, 6.0)

    def test_calculate_median_insufficient_data(self):
        """Test that None is returned with insufficient data."""
        # Only 2 easy runs
        easy_runs = [
            {'pace_min_per_km': 6.0},
            {'pace_min_per_km': 6.2}
        ]
        median_pace = RacePredictor.calculate_median_easy_pace(easy_runs)
        self.assertIsNone(median_pace)

    def test_predict_race_times(self):
        """Test race time prediction."""
        easy_pace = 6.0  # min/km
        predictions = RacePredictor.predict_race_times(easy_pace)

        # Should have all 4 distances
        self.assertIn('5K', predictions)
        self.assertIn('10K', predictions)
        self.assertIn('Half Marathon', predictions)
        self.assertIn('Marathon', predictions)

        # 5K should be fastest pace (Easy - 75 sec/km)
        # Easy: 6:00/km = 360 sec/km
        # 5K: 360 - 75 = 285 sec/km = 4:45/km
        self.assertAlmostEqual(predictions['5K']['pace_min_per_km'], 4.75, places=2)

        # Marathon should be slowest (Easy - 30 sec/km)
        # Marathon: 360 - 30 = 330 sec/km = 5:30/km
        self.assertAlmostEqual(predictions['Marathon']['pace_min_per_km'], 5.5, places=2)

    def test_predict_race_times_with_ef(self):
        """Test that efficiency factor improves predictions slightly."""
        easy_pace = 6.0

        # Without EF
        pred_no_ef = RacePredictor.predict_race_times(easy_pace)

        # With good EF
        pred_with_ef = RacePredictor.predict_race_times(easy_pace, efficiency_factor=0.020)

        # With EF should be slightly faster
        self.assertLess(
            pred_with_ef['Marathon']['total_time_minutes'],
            pred_no_ef['Marathon']['total_time_minutes']
        )

    def test_format_time(self):
        """Test time formatting."""
        # 1:23:45 (83.75 minutes)
        formatted = RacePredictor.format_time(83.75)
        self.assertEqual(formatted, "1:23:45")

        # 45:30 (45.5 minutes)
        formatted = RacePredictor.format_time(45.5)
        self.assertEqual(formatted, "45:30")

        # 3:45:00 (225 minutes)
        formatted = RacePredictor.format_time(225.0)
        self.assertEqual(formatted, "3:45:00")

    def test_format_pace(self):
        """Test pace formatting."""
        # 5:30 min/km
        formatted = RacePredictor.format_pace(5.5)
        self.assertEqual(formatted, "5:30")

        # 4:15 min/km
        formatted = RacePredictor.format_pace(4.25)
        self.assertEqual(formatted, "4:15")

    def test_estimate_race_times_full_workflow(self):
        """Test complete race time estimation workflow."""
        result = RacePredictor.estimate_race_times(
            self.runs,
            self.max_hr,
            efficiency_factor=0.018
        )

        # Should have prediction
        self.assertTrue(result['has_prediction'])
        self.assertEqual(result['easy_runs_count'], 5)  # Updated: 5 runs with new logic
        self.assertEqual(result['median_easy_pace'], 6.0)
        self.assertIn('predictions', result)
        self.assertEqual(result['method'], 'McMillan (HR-based)')

    def test_estimate_race_times_insufficient_data(self):
        """Test that proper error is returned with insufficient data."""
        # Only one easy run
        runs = [self.runs[0]]

        result = RacePredictor.estimate_race_times(runs, self.max_hr)

        self.assertFalse(result['has_prediction'])
        self.assertEqual(result['reason'], 'insufficient_easy_runs')

    def test_manual_hrmax_priority(self):
        """Test that manual HRmax takes priority over detected HRmax."""
        # With detected HRmax of 200 and manual HRmax of 180:
        # - Detected: 200 * 1.10 = 220 bpm → 60-75% = 132-165 bpm
        # - Manual: 180 bpm (no margin) → 60-75% = 108-135 bpm

        manual_hrmax = 180
        easy_runs = RacePredictor.identify_easy_runs(
            self.runs,
            self.max_hr,
            manual_hrmax=manual_hrmax
        )

        # With manual 180 bpm (no safety margin), 60-75% = 108-135 bpm:
        # - Run 1: 140 bpm → 77.8% ❌ (too high)
        # - Run 2: 138 bpm → 76.7% ❌ (too high)
        # - Run 3: 142 bpm → 78.9% ❌ (too high)
        # - Run 4: 165 bpm → 91.7% ❌ (way too high)
        # - Run 5: 110 bpm → 61.1% ✅
        # - Run 6: 140 bpm → 77.8% ❌ (too high)
        # - Run 7: Old ❌
        # Should find only 1 easy run
        self.assertEqual(len(easy_runs), 1)
        # Verify it's the recovery run (pace 7.0)
        self.assertEqual(easy_runs[0]['pace_min_per_km'], 7.0)

    def test_hrmax_plausibility_too_low(self):
        """Test HRmax plausibility check for unusually low detected max."""
        detected_hrmax = 140  # Too low
        check = RacePredictor.check_hrmax_plausibility(detected_hrmax, self.runs)

        self.assertIsNotNone(check)
        self.assertFalse(check['is_plausible'])
        self.assertEqual(check['reason'], 'detected_hrmax_too_low')
        self.assertEqual(check['detected_hrmax'], 140)
        self.assertEqual(check['suggested_hrmax'], 180)

    def test_hrmax_plausibility_insufficient_easy_runs(self):
        """Test HRmax plausibility check with varied pace data (triggers regression)."""
        # Create 10+ runs with varied paces but ALL HRs too high for detected HRmax
        # Even with 10% safety margin (150 * 1.10 = 165), none are easy runs
        now = datetime.now(timezone.utc)
        varied_runs = []

        # All runs have HR > 75% of estimated HRmax (165)
        # 75% of 165 = 124 bpm, so all runs > 124 are NOT easy
        paces_hrs = [
            (7.0, 128), (7.2, 130), (6.8, 126),  # "Easy" pace but HR too high
            (6.0, 135), (6.1, 137), (5.9, 133),  # Moderate
            (5.0, 145), (4.8, 148), (5.2, 143),  # Tempo
            (4.0, 155), (4.2, 152), (3.8, 158)   # Threshold
        ]

        for i, (pace, hr) in enumerate(paces_hrs):
            varied_runs.append({
                'distance_km': 8.0,  # Long enough
                'pace_min_per_km': pace,
                'average_heartrate': hr,
                'start_date': (now - timedelta(days=i*7)).isoformat()
            })

        detected_hrmax = 150  # Too low!

        # Without converted_runs, should return None
        check = RacePredictor.check_hrmax_plausibility(detected_hrmax, varied_runs)
        # Actually this one might trigger the <150 check
        # Let's use 155 instead

        detected_hrmax = 155
        check = RacePredictor.check_hrmax_plausibility(detected_hrmax, varied_runs)
        self.assertIsNone(check)

        # With converted_runs, should detect the issue
        # HR range: 126-158, Pace range: 3.8-7.2 (variation > 2.0)
        # median HR ~140, which is 140/155 = 90% (< 80% so no warning... wait)
        # Let me recalculate: median of [126,128,130,133,135,137,143,145,148,152,155,158] = 140
        # 140/155 = 90% > 80%, so NO WARNING (tempo runner)

        # I need median < 80%. Let me adjust HRs:
        paces_hrs = [
            (7.0, 110), (7.2, 112), (6.8, 108),  # Easy pace, lowish HR
            (6.0, 120), (6.1, 122), (5.9, 118),  # Moderate
            (5.0, 135), (4.8, 138), (5.2, 132),  # Tempo
            (4.0, 148), (4.2, 145), (3.8, 150)   # Threshold
        ]

        varied_runs = []
        for i, (pace, hr) in enumerate(paces_hrs):
            varied_runs.append({
                'distance_km': 8.0,
                'pace_min_per_km': pace,
                'average_heartrate': hr,
                'start_date': (now - timedelta(days=i*7)).isoformat()
            })

        detected_hrmax = 155
        # median HR = (118+120)/2 = 119, which is 119/155 = 76.8% < 80%
        # With safety margin: 155 * 1.10 = 170.5
        # 60-75% of 170.5 = 102-128 bpm
        # Easy runs: 110, 112, 108, 120, 122, 118 - all in range!
        # So this will find 6 easy runs, no warning...

        # OK, I need to make it so even with safety margin, no easy runs are found
        # Let's use distance = 2.0 km (too short)
        # IMPORTANT: median HR must be < 80% of 155 = 124 bpm
        # Median of 12 values is average of 6th and 7th values (indices 5 and 6)
        paces_hrs = [
            (7.0, 105), (7.2, 108), (6.8, 110),  # Would be easy but too short
            (6.0, 112), (6.1, 115), (5.9, 118),  # Median will be (118+123)/2 = 120.5
            (5.0, 123), (4.8, 135), (5.2, 138),  # 120.5/155 = 77.7% < 80%
            (4.0, 145), (4.2, 148), (3.8, 150)   #
        ]

        varied_runs = []
        for i, (pace, hr) in enumerate(paces_hrs):
            varied_runs.append({
                'distance_km': 2.0,  # TOO SHORT!
                'pace_min_per_km': pace,
                'average_heartrate': hr,
                'start_date': (now - timedelta(days=i*7)).isoformat()
            })

        check = RacePredictor.check_hrmax_plausibility(
            detected_hrmax,
            varied_runs,
            varied_runs
        )

        self.assertIsNotNone(check)
        self.assertFalse(check['is_plausible'])
        self.assertEqual(check['reason'], 'insufficient_easy_runs')
        self.assertEqual(check['detected_hrmax'], 155)
        # Regression should suggest higher HRmax
        self.assertGreater(check['suggested_hrmax'], 160)

    def test_hrmax_plausibility_valid(self):
        """Test that plausible HRmax passes check."""
        detected_hrmax = 190
        check = RacePredictor.check_hrmax_plausibility(detected_hrmax, self.runs, self.runs)

        # Should be None (plausible) - with 190 HRmax, the test runs should have enough easy runs
        self.assertIsNone(check)

    def test_estimate_hrmax_regression(self):
        """Test HRmax estimation using regression with varied pace data."""
        now = datetime.now(timezone.utc)

        # Create runs with clear pace-HR relationship
        # Slower pace = lower HR, faster pace = higher HR
        runs = [
            {'pace_min_per_km': 7.0, 'average_heartrate': 120, 'start_date': now.isoformat()},
            {'pace_min_per_km': 6.5, 'average_heartrate': 130, 'start_date': now.isoformat()},
            {'pace_min_per_km': 6.0, 'average_heartrate': 140, 'start_date': now.isoformat()},
            {'pace_min_per_km': 5.5, 'average_heartrate': 150, 'start_date': now.isoformat()},
            {'pace_min_per_km': 5.0, 'average_heartrate': 160, 'start_date': now.isoformat()},
            {'pace_min_per_km': 4.5, 'average_heartrate': 170, 'start_date': now.isoformat()},
        ]

        estimated_hrmax = RacePredictor._estimate_hrmax_from_regression(runs)

        # Should estimate HRmax in reasonable range (180-200)
        self.assertIsNotNone(estimated_hrmax)
        self.assertGreater(estimated_hrmax, 170)
        self.assertLess(estimated_hrmax, 210)

    def test_estimate_hrmax_percentile(self):
        """Test HRmax estimation using percentile method."""
        now = datetime.now(timezone.utc)

        # Create runs with mixed paces (easy and tempo)
        runs = [
            {'pace_min_per_km': 7.0, 'average_heartrate': 120, 'start_date': now.isoformat()},
            {'pace_min_per_km': 7.2, 'average_heartrate': 122, 'start_date': now.isoformat()},
            {'pace_min_per_km': 6.8, 'average_heartrate': 125, 'start_date': now.isoformat()},
            {'pace_min_per_km': 6.9, 'average_heartrate': 123, 'start_date': now.isoformat()},
            {'pace_min_per_km': 7.1, 'average_heartrate': 121, 'start_date': now.isoformat()},
            {'pace_min_per_km': 5.0, 'average_heartrate': 150, 'start_date': now.isoformat()},
            {'pace_min_per_km': 5.2, 'average_heartrate': 148, 'start_date': now.isoformat()},
        ]

        hr_values = [r['average_heartrate'] for r in runs]
        estimated_hrmax = RacePredictor._estimate_hrmax_from_percentile(runs, hr_values)

        # Should estimate based on easy runs (pace >= median)
        # Median pace ~6.9, so easy runs: 7.0, 7.2, 6.9, 7.1 with HRs 120, 122, 123, 121
        # 75th percentile ~122.5, so 122.5 / 0.75 = ~163
        self.assertGreater(estimated_hrmax, 150)
        self.assertLess(estimated_hrmax, 180)

    def test_hrmax_plausibility_tempo_runner(self):
        """Test that tempo runners don't get false warnings."""
        # Create a runner who does mostly tempo/threshold runs (Zone 4)
        now = datetime.now(timezone.utc)
        tempo_runs = []

        for i in range(12):
            tempo_runs.append({
                'distance_km': 8.0,
                'pace_min_per_km': 4.5,
                'average_heartrate': 175,  # 87.5% of 200 - Zone 4
                'start_date': (now - timedelta(days=i*7)).isoformat()
            })

        detected_hrmax = 200

        # Should NOT trigger warning despite high HR in all runs
        # Because with HRmax=200, 175bpm is only 87.5% (plausible for tempo work)
        check = RacePredictor.check_hrmax_plausibility(
            detected_hrmax,
            tempo_runs,
            tempo_runs
        )

        # Should return None (no warning) - it's OK to have no easy runs
        # if your training style is tempo-heavy
        self.assertIsNone(check)


if __name__ == '__main__':
    unittest.main()
