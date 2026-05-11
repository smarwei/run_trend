"""
Tests for StravaClient.get_activity_streams (Ticket 19 — streams slice).
"""
import unittest
from unittest.mock import MagicMock, patch

import requests

from run_trend.strava.client import StravaClient, _HTTP_TIMEOUT


class _FakeAuth:
    def get_access_token(self):
        return "test-token"


class TestGetActivityStreams(unittest.TestCase):

    def setUp(self):
        self.client = StravaClient(_FakeAuth())

    def _patch_request(self, payload):
        mock = MagicMock(return_value=payload)
        self.client._make_request = mock
        return mock

    def test_returns_paired_streams(self):
        payload = {
            'heartrate': {'data': [120, 130, 140], 'series_type': 'time'},
            'time':      {'data': [0, 30, 60],     'series_type': 'time'},
        }
        mock = self._patch_request(payload)
        streams = self.client.get_activity_streams(42)
        self.assertEqual(streams, {
            'heartrate': [120, 130, 140],
            'time': [0, 30, 60],
        })
        endpoint, kwargs = mock.call_args.args[0], mock.call_args.kwargs
        self.assertEqual(endpoint, "activities/42/streams")
        self.assertEqual(kwargs['params']['key_by_type'], 'true')
        self.assertEqual(kwargs['params']['keys'], 'heartrate,time')

    def test_custom_keys_passed_through(self):
        payload = {
            'cadence': {'data': [80, 82], 'series_type': 'time'},
        }
        mock = self._patch_request(payload)
        streams = self.client.get_activity_streams(42, keys=['cadence'])
        self.assertEqual(streams, {'cadence': [80, 82]})
        self.assertEqual(mock.call_args.kwargs['params']['keys'], 'cadence')

    def test_missing_stream_keys_dropped(self):
        # Activity without HR data — Strava returns only the time stream.
        payload = {
            'time': {'data': [0, 30, 60], 'series_type': 'time'},
        }
        self._patch_request(payload)
        streams = self.client.get_activity_streams(42)
        self.assertEqual(streams, {'time': [0, 30, 60]})

    def test_empty_payload_returns_none(self):
        self._patch_request({})
        self.assertIsNone(self.client.get_activity_streams(42))

    def test_request_failure_returns_none(self):
        self._patch_request(None)
        self.assertIsNone(self.client.get_activity_streams(42))

    def test_malformed_entry_skipped(self):
        payload = {
            'heartrate': "not a dict",
            'time': {'data': [0, 30], 'series_type': 'time'},
        }
        self._patch_request(payload)
        streams = self.client.get_activity_streams(42)
        self.assertEqual(streams, {'time': [0, 30]})


class TestMakeRequestTimeout(unittest.TestCase):
    """Ticket 23 — _make_request must pass a timeout to requests.get and
    convert Timeout exceptions to a None return (no propagation)."""

    def setUp(self):
        self.client = StravaClient(_FakeAuth())

    @patch('run_trend.strava.client.requests.get')
    def test_passes_http_timeout(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        mock_get.return_value = mock_response

        self.client._make_request("athlete")

        self.assertEqual(mock_get.call_args.kwargs['timeout'], _HTTP_TIMEOUT)

    @patch('run_trend.strava.client.requests.get')
    def test_timeout_returns_none(self, mock_get):
        mock_get.side_effect = requests.Timeout("read timeout")

        self.assertIsNone(self.client._make_request("athlete"))


if __name__ == '__main__':
    unittest.main()
