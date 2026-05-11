"""
Tests for AppSettings persistence — atomic writes, thread-safety, file
mode (Ticket 23).
"""
import json
import os
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from run_trend.settings.config import AppSettings


class TestAtomicWrite(unittest.TestCase):
    """The save path must use tempfile + os.replace, not a naive truncate.

    A crash between truncate and write would otherwise destroy the entire
    config.json — including stored OAuth tokens.
    """

    def setUp(self):
        import tempfile as _tempfile
        self.tmp_dir = _tempfile.mkdtemp(prefix="runtrend-cfg-test-")
        self.config_file = str(Path(self.tmp_dir) / "config.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_set_persists_to_disk(self):
        settings = AppSettings(config_file=self.config_file)
        settings.set('strava_client_id', '42')

        data = json.loads(Path(self.config_file).read_text())
        self.assertEqual(data['strava_client_id'], '42')

    def test_save_failure_preserves_existing_file(self):
        settings = AppSettings(config_file=self.config_file)
        settings.set('first', 'kept')
        original = Path(self.config_file).read_text()

        # Simulate a crash exactly at the replace step. The tempfile was
        # written; the rename failed. Existing config.json must be
        # untouched.
        with patch(
            'run_trend.settings.config.os.replace',
            side_effect=OSError("disk full"),
        ):
            settings.set('second', 'lost')

        self.assertEqual(Path(self.config_file).read_text(), original)

    def test_save_failure_cleans_up_tempfile(self):
        settings = AppSettings(config_file=self.config_file)

        with patch(
            'run_trend.settings.config.os.replace',
            side_effect=OSError("nope"),
        ):
            settings.set('foo', 'bar')

        leftovers = list(Path(self.tmp_dir).glob('.config-*.tmp'))
        self.assertEqual(leftovers, [], f"tempfile leaked: {leftovers}")

    @unittest.skipUnless(os.name == 'posix', "chmod 0o600 is POSIX-only")
    def test_save_sets_restrictive_mode(self):
        settings = AppSettings(config_file=self.config_file)
        settings.set('strava_client_id', 'cid')

        mode = Path(self.config_file).stat().st_mode & 0o777
        self.assertEqual(mode, 0o600, f"unexpected mode {oct(mode)}")


class TestDeadCodeRemoved(unittest.TestCase):
    """Ticket 30 — load_strava_credentials_from_file was unreferenced
    dead code that suggested an alternative credential path that never
    existed. Guard against accidental re-introduction."""

    def test_load_strava_credentials_from_file_does_not_exist(self):
        self.assertFalse(
            hasattr(AppSettings, 'load_strava_credentials_from_file'),
            "load_strava_credentials_from_file was removed in T30 — do "
            "not re-add without a real caller and tests.",
        )


class TestThreadSafety(unittest.TestCase):
    """Two threads calling set() concurrently must not corrupt the JSON
    file and both writes must be visible afterwards."""

    def setUp(self):
        import tempfile as _tempfile
        self.tmp_dir = _tempfile.mkdtemp(prefix="runtrend-cfg-thread-")
        self.config_file = str(Path(self.tmp_dir) / "config.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_parallel_set_keeps_both_writes(self):
        settings = AppSettings(config_file=self.config_file)

        iterations = 200

        def writer(key, value):
            for _ in range(iterations):
                settings.set(key, value)

        t1 = threading.Thread(target=writer, args=('alpha', 'A'))
        t2 = threading.Thread(target=writer, args=('beta', 'B'))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # File is well-formed JSON (no torn writes).
        data = json.loads(Path(self.config_file).read_text())
        # Both keys survived; values are deterministic since each thread
        # writes a constant value.
        self.assertEqual(data['alpha'], 'A')
        self.assertEqual(data['beta'], 'B')


if __name__ == '__main__':
    unittest.main()
