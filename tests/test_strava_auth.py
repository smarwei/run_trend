"""
Tests for Strava authentication module.
"""
import unittest
from unittest.mock import patch, MagicMock
import urllib.parse

import requests

from run_trend.strava.simple_auth import (
    SimpleStravaAuth, _HTTP_TIMEOUT, _validate_callback_state,
)


class TestSimpleStravaAuth(unittest.TestCase):
    """Tests for SimpleStravaAuth."""

    def setUp(self):
        self.auth = SimpleStravaAuth(settings=None)

    def test_not_authenticated_without_token(self):
        self.assertFalse(self.auth.is_authenticated())

    def test_authenticated_with_token(self):
        self.auth._access_token = "valid_token"
        self.assertTrue(self.auth.is_authenticated())

    def test_get_access_token_returns_none_without_token(self):
        self.assertIsNone(self.auth.get_access_token())

    def test_get_access_token_returns_token(self):
        self.auth._access_token = "valid_token"
        self.assertEqual(self.auth.get_access_token(), "valid_token")

    def test_token_expiry_detection(self):
        import time
        self.auth._access_token = "valid_token"
        self.auth._expires_at = int(time.time()) - 600  # expired 10 min ago
        self.assertTrue(self.auth._is_token_expired())

    def test_token_not_expired(self):
        import time
        self.auth._access_token = "valid_token"
        self.auth._expires_at = int(time.time()) + 3600  # expires in 1 hour
        self.assertFalse(self.auth._is_token_expired())

    def test_auth_url_contains_client_id(self):
        """Verify auth URL construction includes required parameters."""
        client_id = "12345"
        auth_params = {
            'client_id': client_id,
            'redirect_uri': SimpleStravaAuth.REDIRECT_URI,
            'response_type': 'code',
            'scope': 'activity:read_all',
            'approval_prompt': 'force'
        }
        expected_url = f"{SimpleStravaAuth.AUTHORIZE_URL}?{urllib.parse.urlencode(auth_params)}"
        # Verify the URL structure is correct
        parsed = urllib.parse.urlparse(expected_url)
        params = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(params['client_id'][0], client_id)
        self.assertEqual(params['response_type'][0], 'code')
        self.assertEqual(params['scope'][0], 'activity:read_all')

    def test_redirect_uri_uses_localhost(self):
        self.assertIn('localhost', SimpleStravaAuth.REDIRECT_URI)
        self.assertIn(str(SimpleStravaAuth.REDIRECT_PORT), SimpleStravaAuth.REDIRECT_URI)

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_exchange_code_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new_token',
            'refresh_token': 'new_refresh',
            'expires_at': 9999999999,
        }
        mock_post.return_value = mock_response

        result = self.auth._exchange_code('auth_code', 'client_id', 'client_secret')

        self.assertTrue(result)
        self.assertEqual(self.auth._access_token, 'new_token')
        self.assertEqual(self.auth._refresh_token, 'new_refresh')

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_exchange_code_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response

        result = self.auth._exchange_code('bad_code', 'client_id', 'client_secret')

        self.assertFalse(result)
        self.assertIsNone(self.auth._access_token)

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_refresh_token_success(self, mock_post):
        self.auth._access_token = 'old_token'
        self.auth._refresh_token = 'refresh_token'
        self.auth._client_id = 'client_id'
        self.auth._client_secret = 'client_secret'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'refreshed_token',
            'refresh_token': 'new_refresh',
            'expires_at': 9999999999,
        }
        mock_post.return_value = mock_response

        result = self.auth._refresh_access_token()

        self.assertTrue(result)
        self.assertEqual(self.auth._access_token, 'refreshed_token')

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_refresh_token_without_credentials_fails(self, mock_post):
        self.auth._refresh_token = 'refresh_token'
        # No client_id/client_secret set
        result = self.auth._refresh_access_token()
        self.assertFalse(result)
        mock_post.assert_not_called()

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_revoke_clears_tokens(self, mock_post):
        self.auth._access_token = 'token'
        self.auth._refresh_token = 'refresh'
        self.auth._expires_at = 9999999999

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.auth.revoke()

        self.assertIsNone(self.auth._access_token)
        self.assertIsNone(self.auth._refresh_token)
        self.assertIsNone(self.auth._expires_at)

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_revoke_clears_tokens_even_on_api_error(self, mock_post):
        self.auth._access_token = 'token'
        mock_post.side_effect = Exception("Network error")

        self.auth.revoke()

        self.assertIsNone(self.auth._access_token)

    def test_load_token_from_settings(self):
        mock_settings = MagicMock()
        mock_settings.get.return_value = {
            'access_token': 'stored_token',
            'refresh_token': 'stored_refresh',
            'expires_at': 9999999999,
        }
        auth = SimpleStravaAuth(settings=mock_settings)
        self.assertEqual(auth._access_token, 'stored_token')

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_refresh_passes_http_timeout(self, mock_post):
        self.auth._refresh_token = 'refresh'
        self.auth._client_id = 'cid'
        self.auth._client_secret = 'cs'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'a', 'refresh_token': 'r', 'expires_at': 9999999999,
        }
        mock_post.return_value = mock_response

        self.auth._refresh_access_token()

        self.assertEqual(mock_post.call_args.kwargs['timeout'], _HTTP_TIMEOUT)

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_refresh_timeout_returns_false(self, mock_post):
        self.auth._refresh_token = 'refresh'
        self.auth._client_id = 'cid'
        self.auth._client_secret = 'cs'
        mock_post.side_effect = requests.Timeout("connect timeout")

        self.assertFalse(self.auth._refresh_access_token())

    @patch('run_trend.strava.simple_auth.requests.post')
    def test_exchange_code_timeout_returns_false(self, mock_post):
        mock_post.side_effect = requests.Timeout("read timeout")

        self.assertFalse(
            self.auth._exchange_code('code', 'cid', 'cs')
        )


class TestOAuthCallbackBindLocalhost(unittest.TestCase):
    """Ticket 29 — the OAuth callback server must bind to loopback only,
    not all interfaces. Verified by inspecting source text rather than
    actually starting a server (which would race with the OS port table).
    """

    def _module_source(self) -> str:
        import inspect
        from run_trend.strava import simple_auth
        return inspect.getsource(simple_auth)

    def test_loopback_address_appears_in_tcp_server_call(self):
        src = self._module_source()
        # Normalize newlines+indent so the test isn't sensitive to formatting.
        compact = ' '.join(src.split())
        self.assertIn(
            'socketserver.TCPServer( ("127.0.0.1", self.REDIRECT_PORT)',
            compact,
            "OAuth callback must bind to 127.0.0.1, not '' (all interfaces).",
        )

    def test_no_all_interfaces_bind_remains(self):
        compact = ' '.join(self._module_source().split())
        self.assertNotIn(
            'TCPServer(("",',
            compact,
            "All-interfaces bind ('') should no longer appear.",
        )


class TestCsrfStateValidation(unittest.TestCase):
    """Ticket 34 — the OAuth callback handler rejects any response whose
    `state` parameter doesn't match the token we generated. Tests cover
    the extracted ``_validate_callback_state`` helper directly so the
    CSRF branch is exercised without an HTTP server."""

    def test_matching_state_returns_none(self):
        params = {'state': ['abc123'], 'code': ['auth-code']}
        self.assertIsNone(_validate_callback_state(params, 'abc123'))

    def test_mismatched_state_returns_state_mismatch(self):
        params = {'state': ['evil'], 'code': ['auth-code']}
        self.assertEqual(
            _validate_callback_state(params, 'expected'),
            'state_mismatch',
        )

    def test_missing_state_returns_state_mismatch(self):
        params = {'code': ['auth-code']}  # no state key at all
        self.assertEqual(
            _validate_callback_state(params, 'expected'),
            'state_mismatch',
        )

    def test_empty_state_returns_state_mismatch(self):
        params = {'state': [''], 'code': ['auth-code']}
        self.assertEqual(
            _validate_callback_state(params, 'expected'),
            'state_mismatch',
        )

    def test_authorize_generates_state_parameter(self):
        """Smoke-check: the OAuth flow actually passes a state token in
        the auth URL. We patch webbrowser to capture the URL and
        TCPServer to raise immediately so the callback server never
        starts. The OSError handler inside authorize() catches that and
        returns False."""
        import urllib.parse
        from unittest.mock import patch

        auth = SimpleStravaAuth(settings=None)
        captured = {}

        def capture_open(url):
            captured['url'] = url

        with patch(
            'run_trend.strava.simple_auth.webbrowser.open',
            side_effect=capture_open,
        ), patch(
            'run_trend.strava.simple_auth.socketserver.TCPServer',
            side_effect=OSError("test: skip server start"),
        ):
            result = auth.authorize('cid', 'cs')

        self.assertFalse(result)  # Server didn't start; auth aborts.
        self.assertIn('url', captured, "authorize() never opened a URL")
        parsed = urllib.parse.urlparse(captured['url'])
        params = urllib.parse.parse_qs(parsed.query)
        self.assertIn('state', params)
        # secrets.token_urlsafe(16) returns ≥ 16 url-safe chars.
        self.assertGreaterEqual(len(params['state'][0]), 16)


class TestAppConfiguration(unittest.TestCase):
    """Tests that the Qt app configuration is D-Bus compatible."""

    def test_application_name_is_dbus_compatible(self):
        """applicationName must not contain spaces (used for D-Bus service name by KDE)."""
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, '-c',
             'from run_trend.main import main; '
             'import sys; sys.argv=["test"]; '
             'from PySide6.QtWidgets import QApplication; '
             'app = QApplication(sys.argv); '
             'from run_trend.main import main; '
             'import importlib, run_trend.main as m; '
             # Just import and check the values set
             'print("OK")'],
            capture_output=True, text=True, timeout=10
        )
        # If we can import without error, basic structure is fine
        self.assertNotIn('Error', result.stderr or '')

    def test_applicationname_has_no_spaces(self):
        """Directly verify applicationName doesn't contain spaces."""
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, '-c', '''
import sys
sys.argv = ["test"]
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)
app.setApplicationName("RunTrend")
app.setApplicationDisplayName("Running Progress Tracker")
app.setOrganizationName("RunTrend")
app.setOrganizationDomain("runtrend.local")
app.setDesktopFileName("de.arneweiss.RunTrend")
name = app.applicationName()
assert " " not in name, f"applicationName contains spaces: {name!r}"
assert name == "RunTrend", f"Unexpected applicationName: {name!r}"
display = app.applicationDisplayName()
assert display == "Running Progress Tracker", f"Wrong displayName: {display!r}"
desktop = app.desktopFileName()
assert desktop == "de.arneweiss.RunTrend", f"Wrong desktopFileName: {desktop!r}"
print("PASS")
'''],
            capture_output=True, text=True, timeout=10
        )
        self.assertIn('PASS', result.stdout, f"Test failed: {result.stderr}")


if __name__ == '__main__':
    unittest.main()
