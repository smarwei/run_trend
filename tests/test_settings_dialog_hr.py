"""
Tests for SettingsDialog HR-zone fields (Ticket 19 — settings slice).

Covers: load round-trip, save persistence, Karvonen validation,
and stale-cache invalidation when HR config changes.
"""
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox

from run_trend.settings.config import AppSettings
from run_trend.storage.database import Database
from run_trend.ui.settings_dialog import SettingsDialog


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class _FakeMainWindow:
    """Minimal stand-in: SettingsDialog only touches `.db`, `.auth`, and
    `_load_data` / `_refresh_data` from the main window."""
    def __init__(self, db):
        self.db = db
        self.auth = None  # not connected — exercises the "no auth" branch
    def _load_data(self): pass
    def _refresh_data(self): pass


class TestSettingsDialogHr(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_qapplication()

    def setUp(self):
        self.cfg_tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.cfg_tmp.close()
        self.db_tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_tmp.close()
        self.settings = AppSettings(config_file=self.cfg_tmp.name)
        self.db = Database(db_path=self.db_tmp.name)
        self.main_window = _FakeMainWindow(self.db)

    def tearDown(self):
        self.db.close()
        os.unlink(self.cfg_tmp.name)
        os.unlink(self.db_tmp.name)

    def _new_dialog(self):
        return SettingsDialog(self.settings, main_window=self.main_window)

    def test_loads_defaults(self):
        dlg = self._new_dialog()
        self.assertEqual(dlg.hr_rest_input.value(), 0)
        self.assertEqual(dlg.hr_zone_scheme_combo.currentData(), 'classic')

    def test_loads_persisted_values(self):
        self.settings.set('manual_hrmax', 195)
        self.settings.set('hr_rest', 55)
        self.settings.set('hr_zone_scheme', 'karvonen')
        dlg = self._new_dialog()
        self.assertEqual(dlg.hrmax_input.value(), 195)
        self.assertEqual(dlg.hr_rest_input.value(), 55)
        self.assertEqual(dlg.hr_zone_scheme_combo.currentData(), 'karvonen')

    def test_save_persists_classic(self):
        # Classic doesn't need credentials prompt; pre-fill them so save runs
        # without the "Missing Credentials" detour.
        self.settings.set('strava_client_id', 'x')
        self.settings.set('strava_client_secret', 'y')
        dlg = self._new_dialog()
        dlg.hrmax_input.setValue(190)
        dlg.hr_rest_input.setValue(50)
        # scheme default 'classic'

        with patch.object(QMessageBox, 'information'):
            dlg._save_settings()

        self.assertEqual(self.settings.get('manual_hrmax'), 190)
        self.assertEqual(self.settings.get('hr_rest'), 50)
        self.assertEqual(self.settings.get('hr_zone_scheme'), 'classic')

    def test_save_blocks_invalid_karvonen(self):
        self.settings.set('strava_client_id', 'x')
        self.settings.set('strava_client_secret', 'y')
        dlg = self._new_dialog()
        dlg.hrmax_input.setValue(190)
        dlg.hr_rest_input.setValue(0)  # no rest HR — Karvonen impossible
        dlg.hr_zone_scheme_combo.setCurrentIndex(
            dlg.hr_zone_scheme_combo.findData('karvonen')
        )
        warned = MagicMock()
        with patch.object(QMessageBox, 'warning', warned):
            dlg._save_settings()
        warned.assert_called_once()
        # Setting must NOT have been persisted to karvonen.
        self.assertNotEqual(self.settings.get('hr_zone_scheme'), 'karvonen')

    def test_save_blocks_when_rest_above_max(self):
        self.settings.set('strava_client_id', 'x')
        self.settings.set('strava_client_secret', 'y')
        dlg = self._new_dialog()
        dlg.hrmax_input.setValue(150)
        dlg.hr_rest_input.setValue(160)  # invalid
        dlg.hr_zone_scheme_combo.setCurrentIndex(
            dlg.hr_zone_scheme_combo.findData('karvonen')
        )
        warned = MagicMock()
        with patch.object(QMessageBox, 'warning', warned):
            dlg._save_settings()
        warned.assert_called_once()

    def test_changing_hr_max_invalidates_cache(self):
        # Seed a cache row with hr_max_used=180.
        self.db.upsert_activity_hr_zones(
            42, [60, 60, 60, 60, 60], hr_max_used=180,
        )

        self.settings.set('strava_client_id', 'x')
        self.settings.set('strava_client_secret', 'y')
        self.settings.set('manual_hrmax', 180)
        dlg = self._new_dialog()
        dlg.hrmax_input.setValue(195)  # config change

        with patch.object(QMessageBox, 'information'):
            dlg._save_settings()

        self.assertIsNone(self.db.get_activity_hr_zones(42))

    def test_unchanged_config_keeps_cache(self):
        self.db.upsert_activity_hr_zones(
            42, [60, 60, 60, 60, 60], hr_max_used=190,
        )
        self.settings.set('strava_client_id', 'x')
        self.settings.set('strava_client_secret', 'y')
        self.settings.set('manual_hrmax', 190)
        dlg = self._new_dialog()
        # Don't change anything — leave hrmax 190, scheme classic, rest 0.

        with patch.object(QMessageBox, 'information'):
            dlg._save_settings()

        self.assertIsNotNone(self.db.get_activity_hr_zones(42))


if __name__ == '__main__':
    unittest.main()
