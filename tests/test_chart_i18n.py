"""
Tests for static-tr() translations of milestone and zone names (Ticket 25).

pylupdate6 only extracts static ``self.tr("…")`` literals; dynamic
``self.tr(variable)`` calls slip through. This test guards that:

1. ``ProjectionChart._tr_milestone`` returns its input as-is for unknown
   names (defensive fallback).
2. All milestone names from ``Forecaster.MILESTONES`` and
   ``ProjectionChart.LONG_RUN_MILESTONES`` are present as ``<source>``
   entries in both translation files.
3. All three TrainingLoadChart zone names are present in both files.
"""
import os
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from run_trend.charts.projection_chart import ProjectionChart
from run_trend.projection.forecaster import Forecaster


_TS_DIR = Path(__file__).resolve().parent.parent / "run_trend" / "translations"


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class TestMilestoneTranslator(unittest.TestCase):

    def setUp(self):
        _ensure_qapplication()
        self.chart = ProjectionChart()

    def test_unknown_name_falls_through(self):
        self.assertEqual(
            self.chart._tr_milestone("Some Unknown Distance"),
            "Some Unknown Distance",
        )

    def test_all_milestones_translate_without_error(self):
        known = (
            set(Forecaster.MILESTONES.keys())
            | set(ProjectionChart.LONG_RUN_MILESTONES.keys())
        )
        for name in known:
            with self.subTest(name=name):
                result = self.chart._tr_milestone(name)
                self.assertIsInstance(result, str)
                self.assertTrue(result, f"empty translation for {name!r}")


class TestStaticStringsArePickedUp(unittest.TestCase):
    """Regression guard — these strings used to be dynamic ``self.tr(var)``
    calls and were silently missing from the .ts files."""

    EXPECTED_MILESTONES = {
        "5K", "10K", "10K Run", "15K Run",
        "Half Marathon", "30K Run", "Marathon Ready",
    }
    # T40 renamed the bands: chart axis switched from 0-100 composite
    # score to the raw ACWR ratio (0.8 / 1.3 / 1.5 Gabbett thresholds).
    # The '>' in "Danger Zone (>1.5)" is XML-escaped in the .ts source
    # element, so we encode the expected forms accordingly.
    EXPECTED_ZONES = {
        "Safe Zone (0.8-1.3)",
        "Caution Zone (1.3-1.5)",
        "Danger Zone (&gt;1.5)",
    }

    def _ts_content(self, lang):
        path = _TS_DIR / f"runtrend_{lang}.ts"
        return path.read_text(encoding="utf-8")

    def test_milestone_sources_present_in_de(self):
        content = self._ts_content("de")
        for name in self.EXPECTED_MILESTONES:
            with self.subTest(name=name):
                self.assertIn(f"<source>{name}</source>", content)

    def test_milestone_sources_present_in_en(self):
        content = self._ts_content("en")
        for name in self.EXPECTED_MILESTONES:
            with self.subTest(name=name):
                self.assertIn(f"<source>{name}</source>", content)

    def test_zone_sources_present_in_de(self):
        content = self._ts_content("de")
        for name in self.EXPECTED_ZONES:
            with self.subTest(name=name):
                self.assertIn(f"<source>{name}</source>", content)

    def test_zone_sources_present_in_en(self):
        content = self._ts_content("en")
        for name in self.EXPECTED_ZONES:
            with self.subTest(name=name):
                self.assertIn(f"<source>{name}</source>", content)

    def test_de_translations_are_non_english(self):
        """A handful of names must actually differ from their source —
        guards against accidentally copying English over to DE."""
        content = self._ts_content("de")
        # Half Marathon → Halbmarathon
        self.assertIn("<translation type=\"finished\">Halbmarathon</translation>", content)
        # Marathon Ready → Marathon-bereit
        self.assertIn("<translation type=\"finished\">Marathon-bereit</translation>", content)
        # Safe Zone → Sichere Zone (T40-banded values)
        self.assertIn("<translation type=\"finished\">Sichere Zone (0,8-1,3)</translation>", content)


if __name__ == "__main__":
    unittest.main()
