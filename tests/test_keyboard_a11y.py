"""
Tests for keyboard shortcuts and accessibility attributes (Ticket 35).

MainWindow is instantiated with XDG_* env vars redirected to a temp dir so
the test doesn't touch the real user config / data. We do NOT spin the
event loop, so the queued QTimer.singleShot in _check_authentication
never fires.
"""
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QKeySequence


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class _MainWindowFixture:
    """Shared setUp/tearDown logic for tests that need a real MainWindow."""

    def _make_main_window(self):
        # Redirect XDG dirs so AppSettings / Database don't write to $HOME.
        self.tmp_dir = tempfile.mkdtemp(prefix="runtrend-mw-test-")
        os.environ['XDG_DATA_HOME'] = self.tmp_dir
        os.environ['XDG_CONFIG_HOME'] = self.tmp_dir

        _ensure_qapplication()
        # Import deferred so the env vars are honored.
        from run_trend.ui.main_window import MainWindow
        self.window = MainWindow()
        return self.window

    def _cleanup_main_window(self):
        if hasattr(self, 'window'):
            # Cancel the auto-refresh timer so it doesn't fire during tearDown.
            if hasattr(self.window, '_status_refresh_timer'):
                self.window._status_refresh_timer.stop()
            self.window.deleteLater()
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


class TestToolbarShortcuts(unittest.TestCase, _MainWindowFixture):

    def setUp(self):
        self._make_main_window()

    def tearDown(self):
        self._cleanup_main_window()

    def test_sync_action_has_f5(self):
        self.assertEqual(
            self.window.sync_action.shortcut(),
            QKeySequence("F5"),
        )

    def test_settings_action_has_ctrl_comma(self):
        self.assertEqual(
            self.window.settings_action.shortcut(),
            QKeySequence("Ctrl+,"),
        )

    def test_help_action_has_f1(self):
        self.assertEqual(
            self.window.help_action.shortcut(),
            QKeySequence("F1"),
        )


class TestMenuShortcuts(unittest.TestCase, _MainWindowFixture):

    def setUp(self):
        self._make_main_window()

    def tearDown(self):
        self._cleanup_main_window()

    def test_export_csv_has_ctrl_e(self):
        self.assertEqual(
            self.window.export_csv_action.shortcut(),
            QKeySequence("Ctrl+E"),
        )

    def test_manage_races_has_ctrl_r(self):
        self.assertEqual(
            self.window.manage_races_action.shortcut(),
            QKeySequence("Ctrl+R"),
        )

    def test_manage_goals_has_ctrl_g(self):
        self.assertEqual(
            self.window.manage_goals_action.shortcut(),
            QKeySequence("Ctrl+G"),
        )

    def test_quit_action_is_present(self):
        self.assertTrue(hasattr(self.window, 'quit_action'))
        # On Linux QKeySequence.Quit resolves to Ctrl+Q.
        # Compare via string for portability.
        shortcut_str = self.window.quit_action.shortcut().toString()
        self.assertTrue(
            shortcut_str.endswith('Q'),
            f"Quit shortcut should end with Q, got {shortcut_str!r}",
        )


class TestTabShortcuts(unittest.TestCase, _MainWindowFixture):

    def setUp(self):
        self._make_main_window()

    def tearDown(self):
        self._cleanup_main_window()

    def test_ctrl_1_switches_to_first_tab(self):
        # Move to a different tab first so we can observe the change.
        self.window.tab_widget.setCurrentIndex(3)
        # Find and trigger the Ctrl+1 QShortcut by emulating activation.
        from PySide6.QtGui import QShortcut
        shortcuts = self.window.findChildren(QShortcut)
        ctrl_1 = next(
            (s for s in shortcuts if s.key() == QKeySequence("Ctrl+1")),
            None,
        )
        self.assertIsNotNone(ctrl_1, "Ctrl+1 shortcut not found")
        ctrl_1.activated.emit()
        self.assertEqual(self.window.tab_widget.currentIndex(), 0)

    def test_ctrl_5_switches_to_fifth_tab(self):
        self.window.tab_widget.setCurrentIndex(0)
        from PySide6.QtGui import QShortcut
        shortcuts = self.window.findChildren(QShortcut)
        ctrl_5 = next(
            (s for s in shortcuts if s.key() == QKeySequence("Ctrl+5")),
            None,
        )
        self.assertIsNotNone(ctrl_5)
        ctrl_5.activated.emit()
        self.assertEqual(self.window.tab_widget.currentIndex(), 4)


class TestChartAccessibility(unittest.TestCase, _MainWindowFixture):

    def setUp(self):
        self._make_main_window()

    def tearDown(self):
        self._cleanup_main_window()

    def test_all_charts_have_accessible_name(self):
        charts = [
            self.window.distance_chart,
            self.window.pace_chart,
            self.window.frequency_chart,
            self.window.heartrate_chart,
            self.window.hr_zone_chart,
            self.window.endurance_chart,
            self.window.duration_chart,
            self.window.structure_overview_chart,
            self.window.score_chart,
            self.window.training_load_chart,
            self.window.projection_chart,
            self.window.pace_distance_chart,
        ]
        for chart in charts:
            with self.subTest(chart=type(chart).__name__):
                self.assertTrue(
                    chart.accessibleName(),
                    f"{type(chart).__name__}.accessibleName is empty",
                )
                self.assertTrue(
                    chart.accessibleDescription(),
                    f"{type(chart).__name__}.accessibleDescription is empty",
                )

    def test_accessible_names_are_distinct(self):
        names = [
            self.window.distance_chart.accessibleName(),
            self.window.pace_chart.accessibleName(),
            self.window.heartrate_chart.accessibleName(),
        ]
        self.assertEqual(len(set(names)), len(names), "Accessible names collide")


if __name__ == "__main__":
    unittest.main()
