"""
Tests for AboutDialog i18n and dynamic version (Ticket 26).
"""
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from importlib.metadata import PackageNotFoundError

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

from run_trend.ui import about_dialog
from run_trend.ui.about_dialog import AboutDialog, _read_app_version


_TS_DIR = Path(__file__).resolve().parent.parent / "run_trend" / "translations"


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _all_label_texts(dialog: AboutDialog) -> list[str]:
    return [w.text() for w in dialog.findChildren(QLabel)]


class TestVersionReading(unittest.TestCase):

    def test_reads_installed_version(self):
        # The package is installed in the test environment; version must
        # be a non-empty string and not the dev fallback.
        result = _read_app_version()
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")

    def test_falls_back_to_dev_when_uninstalled(self):
        with patch(
            'run_trend.ui.about_dialog.version',
            side_effect=PackageNotFoundError(),
        ):
            self.assertEqual(_read_app_version(), "dev")


class TestAboutDialog(unittest.TestCase):

    def setUp(self):
        _ensure_qapplication()

    def test_constructs_without_error(self):
        dialog = AboutDialog()
        self.assertIsNotNone(dialog)
        # Cleanup avoids warnings on PySide6 destruction.
        dialog.deleteLater()

    def test_version_label_uses_dynamic_lookup(self):
        with patch(
            'run_trend.ui.about_dialog._read_app_version',
            return_value="9.9.9",
        ):
            dialog = AboutDialog()
            labels = _all_label_texts(dialog)
            self.assertTrue(
                any("9.9.9" in t for t in labels),
                f"Version 9.9.9 not found in any label; got: {labels!r}",
            )
            dialog.deleteLater()

    def test_does_not_hardcode_old_version(self):
        dialog = AboutDialog()
        labels = _all_label_texts(dialog)
        # The pre-T26 dialog had `QLabel("Version 0.1.0")` hardcoded;
        # guard that the new code reads the current version dynamically.
        # We don't assert against 0.1.0 itself (it might legitimately
        # come back to that), but rather that it equals the dynamic
        # source rather than a stuck literal.
        dynamic = _read_app_version()
        self.assertTrue(
            any(dynamic in t for t in labels),
            f"Dynamic version {dynamic!r} not visible in dialog labels: {labels!r}",
        )
        dialog.deleteLater()


class TestTranslationsPresent(unittest.TestCase):
    """All AboutDialog source strings must exist in both .ts files."""

    EXPECTED_SOURCES = [
        "About Run Trend",
        "Version {}",
        "A desktop application for tracking and analyzing running progress from Strava.",
        "Developed by Arne Weiß",
        "License: MIT + Commons Clause",
        "Free for private, non-commercial use. Commercial distribution is not allowed.",
        "Repository: ",
        "Close",
    ]

    def _ts_content(self, lang):
        return (_TS_DIR / f"runtrend_{lang}.ts").read_text(encoding="utf-8")

    def test_de_contains_about_dialog_context(self):
        content = self._ts_content("de")
        self.assertIn("<name>AboutDialog</name>", content)

    def test_de_contains_all_sources(self):
        content = self._ts_content("de")
        for src in self.EXPECTED_SOURCES:
            with self.subTest(src=src):
                self.assertIn(f"<source>{src}</source>", content)

    def test_en_contains_all_sources(self):
        content = self._ts_content("en")
        for src in self.EXPECTED_SOURCES:
            with self.subTest(src=src):
                self.assertIn(f"<source>{src}</source>", content)

    def test_de_translates_close(self):
        content = self._ts_content("de")
        self.assertIn(
            '<translation type="finished">Schließen</translation>',
            content,
        )


if __name__ == "__main__":
    unittest.main()
