"""
Tests for the lazy HR-zone fetcher service (Ticket 19 — service slice).

The service is exercised against in-memory fakes for ``Database`` and
``AppSettings`` plus a stub ``fetch_streams`` callable, so no Qt event loop
or HTTP traffic is required.
"""
import unittest
from typing import Any, Dict, List, Optional

from run_trend.analytics.hr_zone_service import HrZoneService


class _FakeSettings:
    def __init__(self, values: Dict[str, Any]):
        self._values = dict(values)

    def get(self, key, default=None):
        return self._values.get(key, default)

    def set(self, key, value):
        self._values[key] = value


class _FakeDatabase:
    def __init__(self):
        self.rows: Dict[int, Dict[str, Any]] = {}
        self.upsert_calls: List[Dict[str, Any]] = []

    def get_activity_hr_zones(self, strava_id: int) -> Optional[Dict[str, Any]]:
        return self.rows.get(strava_id)

    def upsert_activity_hr_zones(
        self, strava_id, zone_seconds, hr_max_used,
        hr_rest_used=None, scheme="classic",
    ):
        self.upsert_calls.append({
            'strava_id': strava_id,
            'zone_seconds': list(zone_seconds),
            'hr_max_used': hr_max_used,
            'hr_rest_used': hr_rest_used,
            'scheme': scheme,
        })
        self.rows[strava_id] = {
            'strava_id': strava_id,
            'z1_seconds': zone_seconds[0],
            'z2_seconds': zone_seconds[1],
            'z3_seconds': zone_seconds[2],
            'z4_seconds': zone_seconds[3],
            'z5_seconds': zone_seconds[4],
            'hr_max_used': hr_max_used,
            'hr_rest_used': hr_rest_used,
            'scheme': scheme,
            'computed_at': '2026-01-01T00:00:00',
        }


def _make_service(settings_dict, fetch_result=None, db=None):
    db = db if db is not None else _FakeDatabase()
    settings = _FakeSettings(settings_dict)
    fetch_calls = []

    def fake_fetch(activity_id):
        fetch_calls.append(activity_id)
        return fetch_result

    svc = HrZoneService(db, settings, fake_fetch)
    return svc, db, fetch_calls


class TestHrZoneServiceConfig(unittest.TestCase):

    def test_returns_none_when_hr_max_unset(self):
        svc, db, calls = _make_service({'manual_hrmax': 0})
        self.assertIsNone(svc.get_zone_seconds(1))
        self.assertEqual(calls, [])

    def test_karvonen_downgrades_to_classic_when_hr_rest_missing(self):
        # Build a flat 100s stream to keep arithmetic simple.
        streams = {
            'heartrate': [120, 150, 180],
            'time': [0, 50, 100],
        }
        svc, db, _ = _make_service(
            {
                'manual_hrmax': 200,
                'hr_rest': 0,
                'hr_zone_scheme': 'karvonen',
            },
            fetch_result=streams,
        )
        result = svc.get_zone_seconds(42)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        # Persisted row should record the downgraded scheme.
        self.assertEqual(db.upsert_calls[0]['scheme'], 'classic')
        self.assertIsNone(db.upsert_calls[0]['hr_rest_used'])

    def test_karvonen_preserved_when_hr_rest_valid(self):
        streams = {
            'heartrate': [140, 170],
            'time': [0, 60],
        }
        svc, db, _ = _make_service(
            {
                'manual_hrmax': 200,
                'hr_rest': 50,
                'hr_zone_scheme': 'karvonen',
            },
            fetch_result=streams,
        )
        svc.get_zone_seconds(7)
        self.assertEqual(db.upsert_calls[0]['scheme'], 'karvonen')
        self.assertEqual(db.upsert_calls[0]['hr_rest_used'], 50)


class TestHrZoneServiceCache(unittest.TestCase):

    def test_cache_hit_skips_fetch(self):
        db = _FakeDatabase()
        db.rows[10] = {
            'strava_id': 10,
            'z1_seconds': 100, 'z2_seconds': 200, 'z3_seconds': 50,
            'z4_seconds': 0, 'z5_seconds': 0,
            'hr_max_used': 190, 'hr_rest_used': None, 'scheme': 'classic',
            'computed_at': '2026-01-01T00:00:00',
        }
        svc, db, calls = _make_service(
            {'manual_hrmax': 190, 'hr_rest': 0, 'hr_zone_scheme': 'classic'},
            fetch_result=None,
            db=db,
        )
        result = svc.get_zone_seconds(10)
        self.assertEqual(result, [100, 200, 50, 0, 0])
        self.assertEqual(calls, [])  # never fetched

    def test_cache_mismatch_triggers_refetch(self):
        db = _FakeDatabase()
        db.rows[10] = {
            'strava_id': 10,
            'z1_seconds': 100, 'z2_seconds': 0, 'z3_seconds': 0,
            'z4_seconds': 0, 'z5_seconds': 0,
            'hr_max_used': 180, 'hr_rest_used': None, 'scheme': 'classic',
            'computed_at': '2026-01-01T00:00:00',
        }
        streams = {'heartrate': [120, 130], 'time': [0, 60]}
        svc, db, calls = _make_service(
            {'manual_hrmax': 200, 'hr_rest': 0, 'hr_zone_scheme': 'classic'},
            fetch_result=streams,
            db=db,
        )
        result = svc.get_zone_seconds(10)
        self.assertIsNotNone(result)
        self.assertEqual(calls, [10])
        self.assertEqual(db.upsert_calls[0]['hr_max_used'], 200)

    def test_cache_match_requires_hr_rest_equality(self):
        db = _FakeDatabase()
        db.rows[10] = {
            'strava_id': 10,
            'z1_seconds': 1, 'z2_seconds': 2, 'z3_seconds': 3,
            'z4_seconds': 4, 'z5_seconds': 5,
            'hr_max_used': 200, 'hr_rest_used': 60, 'scheme': 'karvonen',
            'computed_at': '2026-01-01T00:00:00',
        }
        # User changed hr_rest from 60 → 50.
        streams = {'heartrate': [150, 170], 'time': [0, 60]}
        svc, db, calls = _make_service(
            {'manual_hrmax': 200, 'hr_rest': 50, 'hr_zone_scheme': 'karvonen'},
            fetch_result=streams,
            db=db,
        )
        svc.get_zone_seconds(10)
        self.assertEqual(calls, [10])
        self.assertEqual(db.upsert_calls[0]['hr_rest_used'], 50)


class TestHrZoneServiceFetchFailures(unittest.TestCase):

    def test_returns_none_when_fetch_returns_none(self):
        svc, db, calls = _make_service(
            {'manual_hrmax': 190}, fetch_result=None,
        )
        self.assertIsNone(svc.get_zone_seconds(1))
        self.assertEqual(calls, [1])
        self.assertEqual(db.upsert_calls, [])

    def test_returns_none_when_heartrate_stream_missing(self):
        svc, db, _ = _make_service(
            {'manual_hrmax': 190},
            fetch_result={'time': [0, 30, 60]},
        )
        self.assertIsNone(svc.get_zone_seconds(1))
        self.assertEqual(db.upsert_calls, [])

    def test_returns_none_when_time_stream_missing(self):
        svc, db, _ = _make_service(
            {'manual_hrmax': 190},
            fetch_result={'heartrate': [120, 150, 180]},
        )
        self.assertIsNone(svc.get_zone_seconds(1))
        self.assertEqual(db.upsert_calls, [])

    def test_returns_none_when_streams_empty(self):
        svc, db, _ = _make_service(
            {'manual_hrmax': 190},
            fetch_result={'heartrate': [], 'time': []},
        )
        self.assertIsNone(svc.get_zone_seconds(1))
        self.assertEqual(db.upsert_calls, [])


if __name__ == '__main__':
    unittest.main()
