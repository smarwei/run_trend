"""
Tests for the age-grading analytics module (Ticket 37 — slice 1).
"""
import math
import unittest
from datetime import date, datetime, timedelta

from run_trend.analytics import age_grading as ag
from run_trend.analytics.wma_data import (
    FACTORS, OPEN_WR_TIMES_S, DISTANCE_METRES,
)


class TestAgeOnDate(unittest.TestCase):

    def test_age_increments_on_birthday(self):
        birth = date(1990, 5, 15)
        self.assertEqual(ag.age_on_date(birth, date(2025, 5, 14)), 34)
        self.assertEqual(ag.age_on_date(birth, date(2025, 5, 15)), 35)
        self.assertEqual(ag.age_on_date(birth, date(2025, 5, 16)), 35)

    def test_leap_year_birthday_uses_march_first(self):
        """A person born 1996-02-29 turns 30 on 2026-03-01 in non-leap years
        and 2024-02-29 in a leap year. Test the non-leap fallback."""
        birth = date(1996, 2, 29)
        # 2025 is non-leap. They turn 29 on 2025-03-01.
        self.assertEqual(ag.age_on_date(birth, date(2025, 2, 28)), 28)
        self.assertEqual(ag.age_on_date(birth, date(2025, 3, 1)), 29)
        # 2028 is leap. They turn 32 on 2028-02-29.
        self.assertEqual(ag.age_on_date(birth, date(2028, 2, 29)), 32)


class TestTanakaHRmax(unittest.TestCase):

    def test_known_values(self):
        # Tanaka 208 - 0.7*age
        self.assertAlmostEqual(ag.tanaka_hrmax(30), 187.0)
        self.assertAlmostEqual(ag.tanaka_hrmax(40), 180.0)
        self.assertAlmostEqual(ag.tanaka_hrmax(70), 159.0)

    def test_difference_from_220_age_at_age_70(self):
        """The Tanaka paper highlights ~10 bpm divergence from 220-age at 70."""
        tanaka = ag.tanaka_hrmax(70)
        old_formula = 220 - 70
        self.assertGreater(tanaka - old_formula, 8.0)


class TestWmaFactor(unittest.TestCase):
    """Sanity-check WMA factor lookup against the bundled 2023 table."""

    def test_open_class_at_age_30(self):
        for dist in ("5000m", "10000m", "HalfMarathon", "Marathon"):
            for gender in ("male", "female"):
                with self.subTest(dist=dist, gender=gender):
                    self.assertEqual(ag.wma_factor(dist, 30, gender), 1.0)

    def test_clamps_above_max_table_age(self):
        factor_110 = ag.wma_factor("Marathon", 110, "male")
        factor_125 = ag.wma_factor("Marathon", 125, "male")  # past table top
        self.assertEqual(factor_125, factor_110)

    def test_below_min_age_returns_one(self):
        self.assertEqual(ag.wma_factor("5000m", 20, "male"), 1.0)
        self.assertEqual(ag.wma_factor("5000m", 29, "female"), 1.0)

    def test_unknown_gender_returns_none(self):
        self.assertIsNone(ag.wma_factor("5000m", 40, "prefer-not-to-say"))
        self.assertIsNone(ag.wma_factor("5000m", 40, ""))

    def test_race_predictor_aliases_resolve(self):
        # RacePredictor uses "5K", "10K", "Half Marathon", "Marathon".
        for alias, canonical in [
            ("5K", "5000m"),
            ("10K", "10000m"),
            ("Half Marathon", "HalfMarathon"),
            ("Marathon", "Marathon"),
        ]:
            self.assertEqual(
                ag.wma_factor(alias, 50, "male"),
                ag.wma_factor(canonical, 50, "male"),
            )

    def test_monotone_decrease_with_age(self):
        prev = ag.wma_factor("5000m", 30, "male")
        for age in range(30, 91, 5):
            f = ag.wma_factor("5000m", age, "male")
            self.assertLessEqual(f, prev + 1e-6,
                                 f"factor should not increase: age {age}")
            prev = f


class TestWmaPercent(unittest.TestCase):

    def test_open_wr_at_age_30_is_100_percent(self):
        wr = OPEN_WR_TIMES_S["male"]["Marathon"]
        pct = ag.wma_percent(wr, "Marathon", 30, "male")
        self.assertAlmostEqual(pct, 100.0, places=1)

    def test_double_wr_time_gives_50_percent(self):
        wr = OPEN_WR_TIMES_S["male"]["5000m"]
        pct = ag.wma_percent(wr * 2, "5000m", 30, "male")
        self.assertAlmostEqual(pct, 50.0, places=1)

    def test_aged_runner_higher_percent_for_same_time(self):
        """Running the same time at 60 yields a higher age-graded % than at 30
        (because the age-adjusted target time is slower)."""
        time = 1500.0  # 25 min for 5K
        pct_30 = ag.wma_percent(time, "5000m", 30, "male")
        pct_60 = ag.wma_percent(time, "5000m", 60, "male")
        self.assertGreater(pct_60, pct_30)

    def test_invalid_inputs_return_none(self):
        self.assertIsNone(ag.wma_percent(0, "5000m", 40, "male"))
        self.assertIsNone(ag.wma_percent(-1, "5000m", 40, "male"))
        self.assertIsNone(ag.wma_percent(1500, "5000m", 40, "other"))


class TestDeclineRate(unittest.TestCase):

    def test_full_volume_uses_trained_anchor(self):
        # volume_ratio = 1.0 → 0.55%/yr
        self.assertAlmostEqual(ag.vo2max_annual_decline_rate(1.0), 0.0055, places=4)

    def test_sedentary_uses_lower_anchor(self):
        self.assertAlmostEqual(ag.vo2max_annual_decline_rate(0.5), 0.0305, places=4)

    def test_zero_volume_extrapolation(self):
        self.assertAlmostEqual(ag.vo2max_annual_decline_rate(0.0), 0.0460, places=4)

    def test_monotone_in_volume_ratio(self):
        # More volume → lower decline rate.
        rates = [ag.vo2max_annual_decline_rate(r) for r in [0.0, 0.3, 0.5, 0.8, 1.0]]
        for a, b in zip(rates, rates[1:]):
            self.assertGreaterEqual(a, b)

    def test_clamps_above_one(self):
        # volume_ratio > 1 (impossible for "personal peak" by definition,
        # but defensively handled) clamps to the lowest decline rate.
        self.assertEqual(
            ag.vo2max_annual_decline_rate(1.5),
            ag.vo2max_annual_decline_rate(1.0),
        )


class TestPersonalPeakEf(unittest.TestCase):

    def test_returns_none_when_history_too_short(self):
        # Only 3 samples — window_weeks default is 4.
        samples = [
            (datetime(2025, 1, i), 0.020) for i in range(1, 4)
        ]
        self.assertIsNone(ag.personal_peak_ef(samples))

    def test_picks_best_window(self):
        # Constant 0.020 EF for 8 weeks, except one 4-week run of 0.025.
        base = datetime(2025, 1, 1)
        samples = []
        for i in range(12):
            v = 0.025 if 4 <= i < 8 else 0.020
            samples.append((base + timedelta(weeks=i), v))
        peak = ag.personal_peak_ef(samples, window_weeks=4)
        self.assertIsNotNone(peak)
        peak_mean, peak_date = peak
        self.assertAlmostEqual(peak_mean, 0.025, places=5)
        # Centre date falls inside the high-window (weeks 4-7).
        self.assertGreaterEqual(peak_date, base + timedelta(weeks=4))
        self.assertLessEqual(peak_date, base + timedelta(weeks=8))

    def test_ignores_samples_older_than_lookback(self):
        base = datetime(2025, 6, 1)
        # 6 samples 18 months ago at 0.030, 5 samples last month at 0.020.
        ancient = [(base - timedelta(days=540 - i*7), 0.030) for i in range(6)]
        recent = [(base - timedelta(days=30 - i*7), 0.020) for i in range(5)]
        peak = ag.personal_peak_ef(ancient + recent, window_weeks=4)
        self.assertIsNotNone(peak)
        # Best-in-lookback is 0.020, not 0.030.
        self.assertAlmostEqual(peak[0], 0.020, places=5)


class TestExpectedEf(unittest.TestCase):

    def test_same_date_returns_peak(self):
        d = datetime(2025, 1, 1)
        self.assertEqual(ag.expected_ef(0.025, d, d, 1.0), 0.025)

    def test_one_year_at_full_volume(self):
        peak = 0.025
        peak_date = datetime(2024, 1, 1)
        now = datetime(2025, 1, 1)
        # 0.55%/yr decline.
        expected = ag.expected_ef(peak, peak_date, now, 1.0)
        self.assertAlmostEqual(expected, peak * (1 - 0.0055), places=5)

    def test_three_years_sedentary_drops_significantly(self):
        peak = 0.030
        peak_date = datetime(2022, 1, 1)
        now = datetime(2025, 1, 1)
        expected = ag.expected_ef(peak, peak_date, now, 0.5)
        # 3 yrs × 3.05%/yr ≈ 9.15% drop.
        self.assertLess(expected, peak * 0.92)
        self.assertGreater(expected, peak * 0.88)


class TestAerobicCapacityPercent(unittest.TestCase):

    def test_matching_actual_and_expected_is_100(self):
        self.assertAlmostEqual(ag.aerobic_capacity_percent(0.025, 0.025), 100.0)

    def test_higher_actual_yields_above_100(self):
        self.assertGreater(ag.aerobic_capacity_percent(0.026, 0.025), 100.0)

    def test_none_for_zero_or_negative_expected(self):
        self.assertIsNone(ag.aerobic_capacity_percent(0.025, 0))
        self.assertIsNone(ag.aerobic_capacity_percent(0.025, -1))


if __name__ == "__main__":
    unittest.main()
