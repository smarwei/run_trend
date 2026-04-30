"""
Unit tests for run_trend.analytics.hr_zones (Ticket 19 — analytics slice).
"""
import unittest

from run_trend.analytics.hr_zones import (
    compute_zone_bounds,
    zone_for_bpm,
    time_in_zones,
    aggregate_zone_seconds,
    polarized_ratio,
    NUM_ZONES,
)


class TestZoneBounds(unittest.TestCase):

    def test_classic_zones_at_hr_max_200(self):
        bounds = compute_zone_bounds(200)
        # 50% .. 100% in 10pp steps
        self.assertEqual(bounds, [
            (100, 120), (120, 140), (140, 160), (160, 180), (180, 200)
        ])

    def test_karvonen_uses_reserve(self):
        # HR-Max 200, HR-Rest 50 → reserve 150
        # Z1 low: 0.50 × 150 + 50 = 125
        # Z5 high: 1.00 × 150 + 50 = 200
        bounds = compute_zone_bounds(200, hr_rest=50, scheme="karvonen")
        self.assertEqual(bounds[0][0], 125)
        self.assertEqual(bounds[-1][1], 200)

    def test_karvonen_requires_valid_rest(self):
        with self.assertRaises(ValueError):
            compute_zone_bounds(200, hr_rest=None, scheme="karvonen")
        with self.assertRaises(ValueError):
            compute_zone_bounds(200, hr_rest=200, scheme="karvonen")

    def test_invalid_hr_max_raises(self):
        with self.assertRaises(ValueError):
            compute_zone_bounds(0)


class TestZoneClassification(unittest.TestCase):

    def setUp(self):
        self.bounds = compute_zone_bounds(200)  # 100/120/140/160/180/200

    def test_below_lowest_returns_minus_one(self):
        self.assertEqual(zone_for_bpm(80, self.bounds), -1)
        self.assertEqual(zone_for_bpm(99, self.bounds), -1)

    def test_low_edge_inclusive_high_edge_exclusive(self):
        self.assertEqual(zone_for_bpm(100, self.bounds), 0)  # Z1 start
        self.assertEqual(zone_for_bpm(119, self.bounds), 0)
        self.assertEqual(zone_for_bpm(120, self.bounds), 1)  # Z2 start
        self.assertEqual(zone_for_bpm(140, self.bounds), 2)
        self.assertEqual(zone_for_bpm(160, self.bounds), 3)
        self.assertEqual(zone_for_bpm(180, self.bounds), 4)  # Z5 start

    def test_above_hr_max_clamps_to_top_zone(self):
        self.assertEqual(zone_for_bpm(210, self.bounds), 4)


class TestTimeInZones(unittest.TestCase):

    def setUp(self):
        self.bounds = compute_zone_bounds(200)

    def test_paired_streams_aggregate_left_edge(self):
        hr   = [125, 145, 165, 185, 130]
        time = [0, 60, 120, 180, 240]  # 4 segments × 60s each
        secs = time_in_zones(hr, time, self.bounds)
        # 125 → Z2, 145 → Z3, 165 → Z4, 185 → Z5
        self.assertEqual(secs, [0, 60, 60, 60, 60])

    def test_zero_or_negative_dt_skipped(self):
        hr   = [150, 150, 150]
        time = [0, 0, -5]
        secs = time_in_zones(hr, time, self.bounds)
        self.assertEqual(secs, [0] * NUM_ZONES)

    def test_below_zone_dropped(self):
        hr   = [80, 80, 130]
        time = [0, 30, 60]
        secs = time_in_zones(hr, time, self.bounds)
        # First sample below Z1 → ignored. Second sample 80 → still below Z1.
        self.assertEqual(secs, [0] * NUM_ZONES)

    def test_mismatched_lengths_raises(self):
        with self.assertRaises(ValueError):
            time_in_zones([100, 110], [0, 30, 60], self.bounds)

    def test_short_stream_returns_zeros(self):
        self.assertEqual(time_in_zones([], [], self.bounds), [0] * NUM_ZONES)
        self.assertEqual(time_in_zones([130], [0], self.bounds), [0] * NUM_ZONES)


class TestAggregateAndPolarized(unittest.TestCase):

    def test_aggregate_sums_elementwise(self):
        a = [10, 20, 30, 40, 50]
        b = [1, 2, 3, 4, 5]
        self.assertEqual(aggregate_zone_seconds([a, b]), [11, 22, 33, 44, 55])

    def test_aggregate_skips_wrong_length_vectors(self):
        a = [10, 20, 30, 40, 50]
        bad = [1, 2, 3]
        self.assertEqual(aggregate_zone_seconds([a, bad]), a)

    def test_polarized_ratio_is_fraction(self):
        secs = [40, 30, 0, 10, 10]
        total = sum(secs)
        ratio = polarized_ratio(secs)
        self.assertAlmostEqual(ratio["low"], (40 + 30) / total)
        self.assertAlmostEqual(ratio["high"], (10 + 10) / total)
        self.assertAlmostEqual(ratio["middle"], 0.0)
        self.assertAlmostEqual(
            ratio["low"] + ratio["middle"] + ratio["high"], 1.0
        )

    def test_polarized_zero_total_safe(self):
        ratio = polarized_ratio([0] * NUM_ZONES)
        self.assertEqual(ratio, {"low": 0.0, "middle": 0.0, "high": 0.0})


if __name__ == "__main__":
    unittest.main()
