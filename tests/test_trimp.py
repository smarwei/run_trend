"""
Tests for the TRIMP / CTL / ATL / TSB analytics module (Ticket 38).
"""
import math
import unittest
from datetime import date, datetime, timedelta

from run_trend.analytics import trimp


class TestBanisterTrimp(unittest.TestCase):

    def test_easy_run_lower_than_tempo(self):
        # 30 min @ 130 bpm (easy, HRr ~0.4) vs 30 min @ 175 bpm (tempo, ~0.85).
        # Exponential factor makes the tempo run much heavier per unit HR.
        easy = trimp.banister_trimp(30, 130, hr_rest=50, hr_max=200, gender="male")
        tempo = trimp.banister_trimp(30, 175, hr_rest=50, hr_max=200, gender="male")
        self.assertGreater(tempo, easy)
        # Same duration but exponential weight should at least double the load.
        self.assertGreater(tempo / max(easy, 1e-9), 2.0)

    def test_gender_factor_male_higher_than_female_at_high_intensity(self):
        # Female b is 1.67 vs male 1.92 — at high HRr, male load > female.
        # At very low HRr the two are basically equal.
        male = trimp.banister_trimp(60, 170, hr_rest=50, hr_max=200, gender="male")
        female = trimp.banister_trimp(60, 170, hr_rest=50, hr_max=200, gender="female")
        self.assertGreater(male, female)

    def test_zero_duration_returns_zero(self):
        self.assertEqual(
            trimp.banister_trimp(0, 150, hr_rest=50, hr_max=200), 0.0
        )

    def test_missing_hr_rest_returns_zero(self):
        # Without hr_rest we can't compute HRr — be explicit, not silent garbage.
        self.assertEqual(
            trimp.banister_trimp(60, 150, hr_rest=0, hr_max=200), 0.0
        )

    def test_hr_rest_above_hr_max_returns_zero(self):
        # Defensive: nonsensical config shouldn't blow up the EWMA.
        self.assertEqual(
            trimp.banister_trimp(60, 150, hr_rest=210, hr_max=200), 0.0
        )

    def test_hr_above_max_clamps_to_full_load(self):
        # Brief HR spikes above the recorded max shouldn't push HRr > 1.0.
        load = trimp.banister_trimp(60, 220, hr_rest=50, hr_max=200, gender="male")
        # Max-load = 60 × 1.0 × 0.64 × e^1.92 ≈ 261.9
        self.assertAlmostEqual(load, 60 * 1.0 * 0.64 * math.exp(1.92), places=2)

    def test_hr_below_rest_clamps_to_zero(self):
        load = trimp.banister_trimp(60, 40, hr_rest=50, hr_max=200, gender="male")
        self.assertEqual(load, 0.0)


class TestDailyTrimpSeries(unittest.TestCase):

    def test_aggregates_two_activities_same_day(self):
        activities = [
            {
                'start_date': '2026-01-15T07:00:00',
                'moving_time': 3600,
                'average_heartrate': 140,
            },
            {
                'start_date': '2026-01-15T18:00:00',
                'moving_time': 1800,
                'average_heartrate': 160,
            },
        ]
        series = trimp.daily_trimp_series(activities, hr_rest=50, hr_max=200)
        self.assertEqual(list(series.keys()), [date(2026, 1, 15)])
        # Both activities contributed.
        self.assertGreater(series[date(2026, 1, 15)], 0)

    def test_skips_activities_without_hr(self):
        activities = [
            {'start_date': '2026-01-15T07:00:00', 'moving_time': 3600},
            {
                'start_date': '2026-01-16T07:00:00',
                'moving_time': 3600,
                'average_heartrate': 140,
            },
        ]
        series = trimp.daily_trimp_series(activities, hr_rest=50, hr_max=200)
        self.assertEqual(list(series.keys()), [date(2026, 1, 16)])

    def test_skips_malformed_dates(self):
        activities = [
            {
                'start_date': 'not-an-iso-string',
                'moving_time': 3600,
                'average_heartrate': 140,
            },
        ]
        self.assertEqual(
            trimp.daily_trimp_series(activities, hr_rest=50, hr_max=200), {}
        )


class TestComputeCtlAtl(unittest.TestCase):

    def test_steady_load_converges_to_load_value(self):
        # EWMA needs ~4 time constants to converge; with W_ctl=42 that's
        # ~168 days. Run 200 days at constant 60 TRIMP and CTL ≈ ATL ≈ 60.
        loads = {
            date(2026, 1, 1) + timedelta(days=i): 60.0 for i in range(200)
        }
        series = trimp.compute_ctl_atl_series(loads)
        last = series[-1]
        self.assertAlmostEqual(last['ctl'], 60.0, delta=1.0)
        self.assertAlmostEqual(last['atl'], 60.0, delta=0.1)
        self.assertAlmostEqual(last['tsb'], 0.0, delta=1.0)

    def test_42_days_at_zero_after_60_days_full_decay(self):
        # Train hard for 60 days, then 60 days of nothing → CTL drops a lot.
        loads = {
            date(2026, 1, 1) + timedelta(days=i): 100.0 for i in range(60)
        }
        # Walk an extra 60 days with no entries (key absent ⇒ load = 0).
        series = trimp.compute_ctl_atl_series(
            loads,
            start=date(2026, 1, 1),
            end=date(2026, 1, 1) + timedelta(days=119),
        )
        peak_ctl = max(d['ctl'] for d in series)
        last_ctl = series[-1]['ctl']
        self.assertGreater(peak_ctl - last_ctl, peak_ctl * 0.5)
        # ATL decays faster than CTL — after 60 days off, ATL ≈ 0.
        self.assertLess(series[-1]['atl'], 1.0)

    def test_taper_produces_positive_tsb(self):
        # 90 days of high load builds CTL toward ~80 (CTL warmup is slow);
        # then 14 days of full rest crashes ATL (7-day window decays much
        # faster) while CTL barely budges → TSB swings positive
        # ("race fresh"). This is the classic taper signature.
        loads: dict = {}
        for i in range(90):
            loads[date(2026, 1, 1) + timedelta(days=i)] = 80.0
        for i in range(90, 104):
            loads[date(2026, 1, 1) + timedelta(days=i)] = 0.0
        series = trimp.compute_ctl_atl_series(loads)
        self.assertGreater(series[-1]['tsb'], 0.0)

    def test_empty_input_yields_empty_series(self):
        self.assertEqual(trimp.compute_ctl_atl_series({}), [])


class TestTsbZone(unittest.TestCase):

    def test_known_thresholds(self):
        self.assertEqual(trimp.tsb_zone(30), "transitional")
        self.assertEqual(trimp.tsb_zone(15), "race-fresh")
        self.assertEqual(trimp.tsb_zone(0), "neutral")
        self.assertEqual(trimp.tsb_zone(-15), "productive")
        self.assertEqual(trimp.tsb_zone(-25), "fatigue-limit")
        self.assertEqual(trimp.tsb_zone(-40), "overreaching")

    def test_boundary_values(self):
        # >+25 = transitional, =+25 = race-fresh.
        self.assertEqual(trimp.tsb_zone(25.0), "race-fresh")
        self.assertEqual(trimp.tsb_zone(25.01), "transitional")


class TestLatestFitnessState(unittest.TestCase):

    def test_none_for_empty(self):
        self.assertIsNone(trimp.latest_fitness_state({}))

    def test_cold_start_flag(self):
        # Only 10 days of history < 42-day ctl_window → cold_start = True.
        loads = {
            date(2026, 1, 1) + timedelta(days=i): 50.0 for i in range(10)
        }
        state = trimp.latest_fitness_state(loads, on_date=date(2026, 1, 10))
        self.assertIsNotNone(state)
        self.assertTrue(state['cold_start'])
        self.assertEqual(state['days_of_history'], 10)

    def test_warmed_up_after_42_days(self):
        loads = {
            date(2026, 1, 1) + timedelta(days=i): 50.0 for i in range(50)
        }
        state = trimp.latest_fitness_state(loads, on_date=date(2026, 2, 19))
        self.assertFalse(state['cold_start'])
        self.assertIn(state['zone'], (
            "transitional", "race-fresh", "neutral",
            "productive", "fatigue-limit", "overreaching",
        ))


if __name__ == "__main__":
    unittest.main()
