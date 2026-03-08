"""
Strava authentication with OAuth support.
"""
from typing import Optional
import webbrowser
import http.server
import socketserver
import urllib.parse
import requests
import time


class SimpleStravaAuth:
    """
    Strava authentication with OAuth 2.0.

    Handles OAuth authorization flow, token storage in settings,
    and automatic token refresh when expired.
    """

    AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
    TOKEN_URL = "https://www.strava.com/oauth/token"
    REDIRECT_PORT = 8000
    REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"

    def __init__(self, settings=None):
        """
        Initialize with settings.

        Args:
            settings: AppSettings instance containing OAuth token data
        """
        self.settings = settings
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expires_at: Optional[int] = None
        self._client_id: Optional[str] = None
        self._client_secret: Optional[str] = None
        self._load_token()
        self._load_credentials()

    def _load_token(self):
        """Load OAuth token data from settings."""
        if self.settings:
            token_data = self.settings.get('strava_token_data')
            if token_data:
                self._access_token = token_data.get('access_token')
                self._refresh_token = token_data.get('refresh_token')
                self._expires_at = token_data.get('expires_at')

    def _load_credentials(self):
        """Load client credentials from settings."""
        if self.settings:
            self._client_id = self.settings.get('strava_client_id')
            self._client_secret = self.settings.get('strava_client_secret')

    def _is_token_expired(self) -> bool:
        """Check if access token is expired."""
        if not self._expires_at:
            return False
        # Add 5 minute buffer
        return time.time() > (self._expires_at - 300)

    def _refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token.

        Returns:
            True if refresh successful
        """
        if not self._refresh_token:
            print("No refresh token available")
            return False

        if not self._client_id or not self._client_secret:
            print("No client credentials available for token refresh")
            return False

        try:
            response = requests.post(
                self.TOKEN_URL,
                data={
                    'client_id': self._client_id,
                    'client_secret': self._client_secret,
                    'refresh_token': self._refresh_token,
                    'grant_type': 'refresh_token'
                }
            )

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data['access_token']
                self._refresh_token = token_data.get('refresh_token', self._refresh_token)
                self._expires_at = token_data.get('expires_at')

                # Save updated token to settings
                if self.settings:
                    self.settings.set('strava_token_data', {
                        'access_token': self._access_token,
                        'refresh_token': self._refresh_token,
                        'expires_at': self._expires_at
                    })

                print("Token refreshed successfully!")
                return True
            else:
                print(f"Token refresh failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False

    def is_authenticated(self) -> bool:
        """
        Check if we have a token.

        Returns:
            True if access token exists
        """
        return self._access_token is not None and len(self._access_token) > 0

    def get_access_token(self) -> Optional[str]:
        """
        Get the access token, refreshing if necessary.

        Returns:
            Access token string or None
        """
        # Check if token is expired and refresh if needed
        if self._access_token and self._is_token_expired():
            print("Access token expired, refreshing...")
            if not self._refresh_access_token():
                print("Failed to refresh token")
                return None

        return self._access_token


    def authorize(self, client_id: str, client_secret: str) -> bool:
        """
        Start OAuth authorization flow.

        Args:
            client_id: Strava API client ID
            client_secret: Strava API client secret

        Returns:
            True if authorization successful
        """
        # Store credentials for token refresh
        self._client_id = client_id
        self._client_secret = client_secret

        # Build authorization URL
        auth_params = {
            'client_id': client_id,
            'redirect_uri': self.REDIRECT_URI,
            'response_type': 'code',
            'scope': 'activity:read_all',
            'approval_prompt': 'force'
        }

        auth_url = f"{self.AUTHORIZE_URL}?{urllib.parse.urlencode(auth_params)}"

        # Set up callback server
        authorization_code = {'code': None, 'error': None}

        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                # Parse callback URL
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)

                if 'code' in params:
                    authorization_code['code'] = params['code'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html = """
                    <html>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: green;">✓ Authorization Successful!</h1>
                        <p>You can close this window and return to the app.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                elif 'error' in params:
                    authorization_code['error'] = params['error'][0]
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html = """
                    <html>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: red;">✗ Authorization Failed!</h1>
                        <p>Please try again.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())

            def log_message(self, format, *args):
                # Suppress log messages
                pass

        # Open browser
        print(f"Opening browser for Strava authorization...")
        webbrowser.open(auth_url)

        # Start server and wait for callback
        try:
            with socketserver.TCPServer(("", self.REDIRECT_PORT), CallbackHandler) as httpd:
                print("Waiting for authorization...")
                httpd.handle_request()
        except OSError as e:
            print(f"Error starting callback server: {e}")
            return False

        # Check for authorization code
        if authorization_code['error']:
            print(f"Authorization error: {authorization_code['error']}")
            return False

        if not authorization_code['code']:
            print("No authorization code received")
            return False

        # Exchange code for token
        return self._exchange_code(authorization_code['code'], client_id, client_secret)

    def _exchange_code(self, code: str, client_id: str, client_secret: str) -> bool:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code
            client_id: Strava API client ID
            client_secret: Strava API client secret

        Returns:
            True if exchange successful
        """
        try:
            response = requests.post(
                self.TOKEN_URL,
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'grant_type': 'authorization_code'
                }
            )

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data['access_token']
                self._refresh_token = token_data.get('refresh_token')
                self._expires_at = token_data.get('expires_at')

                # Save to settings
                if self.settings:
                    self.settings.set('strava_token_data', token_data)

                print("Authorization successful!")
                return True
            else:
                print(f"Token exchange failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error exchanging code: {e}")
            return False

    def revoke(self):
        """Revoke authentication by clearing stored token data."""
        self._access_token = None
        self._refresh_token = None
        self._expires_at = None

        if self.settings:
            self.settings.set('strava_token_data', None)
