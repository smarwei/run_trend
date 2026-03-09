"""
Application settings and configuration management.
"""
import os
from pathlib import Path
from typing import Any, Optional
import json


class AppSettings:
    """Manages application settings."""

    DEFAULT_SETTINGS = {
        'strava_client_id': '',
        'strava_client_secret': '',
        'training_start_date': None,
        'aggregation_period': 'week',  # 'week' or 'month'
        'metric_mode': 'pace',  # 'pace' or 'speed'
        'smoothing_method': 'sma',  # 'sma' or 'ema'
        'smoothing_strength': 'medium',  # 'off', 'light', 'medium', 'strong'
        'projection_horizon': 12,  # periods ahead to project
        'include_treadmill': True,
        'include_manual': True,
        'theme': 'light',  # 'light' or 'dark'
    }

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize settings.

        Args:
            config_file: Path to configuration file. If None, uses default.
        """
        if config_file is None:
            # Use XDG_CONFIG_HOME for Flatpak compatibility
            config_home = os.environ.get('XDG_CONFIG_HOME', str(Path.home() / ".config"))
            config_file = str(Path(config_home) / "run_trend" / "config.json")

        self.config_file = config_file
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)

        self.settings = self.DEFAULT_SETTINGS.copy()
        self._load_settings()

    def _load_settings(self):
        """Load settings from file."""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self._save_settings()

    def get_all(self) -> dict:
        """
        Get all settings.

        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._save_settings()

    @staticmethod
    def load_strava_credentials_from_file(token_file: Optional[str] = None) -> tuple:
        """
        Load Strava client ID and secret from file.

        Args:
            token_file: Path to file containing credentials

        Returns:
            Tuple of (client_id, client_secret) or (None, None)
        """
        if token_file is None:
            # Try default location (use XDG_CONFIG_HOME for Flatpak compatibility)
            config_home = os.environ.get('XDG_CONFIG_HOME', str(Path.home() / ".config"))
            token_file = str(Path(config_home) / "run_trend" / "strava_credentials.json")

        try:
            if Path(token_file).exists():
                with open(token_file, 'r') as f:
                    creds = json.load(f)
                    return (creds.get('client_id'), creds.get('client_secret'))
        except Exception as e:
            print(f"Error loading credentials: {e}")

        return (None, None)
