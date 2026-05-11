"""
Tests for the Profile section of the Settings dialog (Ticket 37 slice 2):
birth_date + gender persistence and load/save roundtrip.
"""
import os
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QMessageBox

from run_trend.settings.config import AppSettings
from run_trend.ui.settings_dialog import SettingsDialog


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class _SettingsFixture:
    def setUp(self):
        _ensure_qapplication()
        self.tmp_dir = tempfile.mkdtemp(prefix="runtrend-profile-test-")
        cfg = str(Path(self.tmp_dir) / "config.json")
        self.settings = AppSettings(config_file=cfg)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


class TestProfileDefaults(unittest.TestCase, _SettingsFixture):

    def setUp(self):
        _SettingsFixture.setUp(self)

    def tearDown(self):
        _SettingsFixture.tearDown(self)

    def test_birth_date_defaults_to_not_set(self):
        dlg = SettingsDialog(self.settings)
        self.assertEqual(dlg.birth_date_input.date(), dlg._birth_date_unset)
        dlg.deleteLater()

    def test_gender_defaults_to_prefer_not_to_say(self):
        dlg = SettingsDialog(self.settings)
        self.assertEqual(dlg.gender_combo.currentData(), '')
        dlg.deleteLater()


class TestProfileRoundtrip(unittest.TestCase, _SettingsFixture):

    def setUp(self):
        _SettingsFixture.setUp(self)

    def tearDown(self):
        _SettingsFixture.tearDown(self)

    def test_save_then_load_birth_date(self):
        self.settings.set('strava_client_id', 'x')
        self.settings.set('strava_client_secret', 'y')

        dlg = SettingsDialog(self.settings)
        dlg.birth_date_input.setDate(QDate(1990, 5, 15))
        dlg.gender_combo.setCurrentIndex(
            dlg.gender_combo.findData('male')
        )
        with patch.object(QMessageBox, 'information'):
            dlg._save_settings()
        dlg.deleteLater()

        self.assertEqual(self.settings.get('birth_date'), '1990-05-15')
        self.assertEqual(self.settings.get('gender'), 'male')

        # Reload in a new dialog instance → fields show stored values.
        dlg2 = SettingsDialog(self.settings)
        self.assertEqual(dlg2.birth_date_input.date(), QDate(1990, 5, 15))
        self.assertEqual(dlg2.gender_combo.currentData(), 'male')
        dlg2.deleteLater()

    def test_clearing_birth_date_persists_as_empty(self):
        self.settings.set('strava_client_id', 'x')
        self.settings.set('strava_client_secret', 'y')
        self.settings.set('birth_date', '1990-05-15')

        dlg = SettingsDialog(self.settings)
        # User resets to sentinel.
        dlg.birth_date_input.setDate(dlg._birth_date_unset)
        with patch.object(QMessageBox, 'information'):
            dlg._save_settings()
        dlg.deleteLater()

        self.assertEqual(self.settings.get('birth_date'), '')

    def test_prefer_not_to_say_persists_as_empty(self):
        self.settings.set('strava_client_id', 'x')
        self.settings.set('strava_client_secret', 'y')

        dlg = SettingsDialog(self.settings)
        dlg.gender_combo.setCurrentIndex(
            dlg.gender_combo.findData('')
        )
        with patch.object(QMessageBox, 'information'):
            dlg._save_settings()
        dlg.deleteLater()

        self.assertEqual(self.settings.get('gender'), '')

    def test_invalid_stored_birth_date_falls_back_to_unset(self):
        self.settings.set('birth_date', 'garbage-not-iso')

        dlg = SettingsDialog(self.settings)
        self.assertEqual(dlg.birth_date_input.date(), dlg._birth_date_unset)
        dlg.deleteLater()


if __name__ == "__main__":
    unittest.main()
