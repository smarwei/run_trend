"""
Application settings and configuration management.
"""
import os
import logging
import tempfile
import threading
from pathlib import Path
from typing import Any, Optional
import json

logger = logging.getLogger(__name__)


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

    # Class-level lock — AppSettings is a de-facto singleton (one instance
    # in MainWindow), but the OAuth refresh thread can race the UI thread
    # on `set(...)`. The lock serialises _save_settings across threads.
    _lock = threading.Lock()

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
        except Exception:
            logger.exception("Error loading settings")

    def _save_settings(self):
        """Save settings to file atomically.

        Writes JSON to a tempfile in the same directory and renames over
        the target via os.replace, which is atomic on POSIX and Windows.
        A crash mid-write leaves the previous config.json intact instead
        of clobbering it with a partial file. Best-effort chmod 0o600
        protects the contained OAuth tokens on shared systems.
        """
        with self._lock:
            path = Path(self.config_file)
            tmp_path: Optional[Path] = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    dir=path.parent,
                    delete=False,
                    prefix='.config-',
                    suffix='.tmp',
                    encoding='utf-8',
                ) as f:
                    json.dump(self.settings, f, indent=2)
                    tmp_path = Path(f.name)
                os.replace(tmp_path, path)
                tmp_path = None  # replace succeeded — nothing to clean up
                try:
                    os.chmod(path, 0o600)
                except OSError:
                    pass  # best effort (Windows etc.)
            except Exception:
                logger.exception("Error saving settings")
                if tmp_path is not None and tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except OSError:
                        pass

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


# Backward compatibility alias
SettingsManager = AppSettings
