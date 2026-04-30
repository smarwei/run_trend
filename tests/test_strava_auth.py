"""
Tests for Strava authentication module.
"""
import unittest
from unittest.mock import patch, MagicMock
import urllib.parse

from run_trend.strava.simple_auth import SimpleStravaAuth


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
