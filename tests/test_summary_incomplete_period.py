"""
Regression guard: training-status numbers in the SummaryPanel must not
read from an in-progress (incomplete) period. Comparing partial-period
runs against a full-period baseline produces misleadingly low numbers
(reported as "Frequency 3.7/20 even though I run every other day").
"""
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


class _MwFixture:
    """Shared XDG-redirect MainWindow setup, copied from test_keyboard_a11y."""

    def _make(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="runtrend-summary-test-")
        os.environ['XDG_DATA_HOME'] = self.tmp_dir
        os.environ['XDG_CONFIG_HOME'] = self.tmp_dir
        _ensure_qapplication()
        from run_trend.ui.main_window import MainWindow
        self.window = MainWindow()
        return self.window

    def _cleanup(self):
        if hasattr(self, 'window'):
            if hasattr(self.window, '_status_refresh_timer'):
                self.window._status_refresh_timer.stop()
            self.window.deleteLater()
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


def _aggregate(period_date: datetime, *, complete: bool, num_runs: int,
               distance_km: float = 30.0, pace: float = 5.0) -> dict:
    return {
        'period_date': period_date,
        'period_start': period_date.isoformat(),
        'period': period_date.strftime('%Y-W%U'),
        'is_complete': complete,
        'num_runs': num_runs,
        'total_distance_km': distance_km,
        'total_moving_time_h': 4.0,
        'avg_distance_per_run_km': distance_km / max(num_runs, 1),
        'weighted_avg_pace_min_per_km': pace,
        'avg_speed_kmh': 60.0 / pace,
        'efficiency_factor': 0.0,
        'avg_heartrate': 0,
        'max_heartrate': 0,
        'min_avg_heartrate': 0,
        'num_hr_activities': 0,
        'active_days': min(num_runs, 7),
        'consistency_ratio': min(num_runs, 7) / 7.0,
        'training_score': 50.0 + num_runs,  # synthetic, used only for fallback
        'score_components': {
            'normalized_distance': 1.0,
            'normalized_frequency': num_runs / 4.0,  # if baseline is 4 runs/wk
            'normalized_pace': 1.0,
            'normalized_efficiency': 0.0,
            'has_hr_data': False,
        },
        'training_load': {'has_load': True, 'training_load': 60.0,
                          'status': 'safe', 'message': ''},
    }


class TestScoreUsesLastCompletePeriod(unittest.TestCase, _MwFixture):

    def setUp(self):
        self._make()

    def tearDown(self):
        self._cleanup()

    def _run_update(self):
        # Drive _update_summary via direct attribute assignment + call.
        # No real DB / Strava traffic happens; the panel reads from
        # self.aggregates / self.activities.
        self.window._update_summary()

    def test_incomplete_current_period_does_not_drag_score(self):
        # Three complete weeks @ 4 runs each + one in-progress week @ 1 run.
        base = datetime(2026, 1, 5)  # a Monday
        self.window.aggregates = [
            _aggregate(base, complete=True, num_runs=4),
            _aggregate(base + timedelta(weeks=1), complete=True, num_runs=4),
            _aggregate(base + timedelta(weeks=2), complete=True, num_runs=4),
            _aggregate(base + timedelta(weeks=3), complete=False, num_runs=1),
        ]
        self.window.activities = []

        self._run_update()

        # The score label should reflect a complete period (score=54 for
        # num_runs=4) plus a "(last complete period)" annotation, not the
        # partial period's score of 51.
        label = self.window.summary_panel.score_label.text()
        self.assertIn("54", label)
        self.assertIn("last complete period", label)

    def test_complete_current_period_uses_latest_silently(self):
        base = datetime(2026, 1, 5)
        self.window.aggregates = [
            _aggregate(base, complete=True, num_runs=4),
            _aggregate(base + timedelta(weeks=1), complete=True, num_runs=4),
            _aggregate(base + timedelta(weeks=2), complete=True, num_runs=5),
        ]
        self.window.activities = []
        self._run_update()

        label = self.window.summary_panel.score_label.text()
        self.assertIn("55", label)  # 50 + 5
        # No "last complete" hint when the current period IS complete.
        self.assertNotIn("last complete period", label)

    def test_consistency_label_marks_partial_week(self):
        base = datetime(2026, 1, 5)
        self.window.aggregates = [
            _aggregate(base, complete=True, num_runs=4),
            _aggregate(base + timedelta(weeks=1), complete=False, num_runs=2),
        ]
        self.window.activities = []
        self._run_update()
        label = self.window.summary_panel.consistency_label.text()
        self.assertIn("so far", label)

    def test_training_load_pulled_from_last_complete(self):
        # Different load values across periods to verify which one wins.
        base = datetime(2026, 1, 5)
        complete = _aggregate(base, complete=True, num_runs=4)
        complete['training_load']['training_load'] = 70.0
        inprogress = _aggregate(base + timedelta(weeks=1), complete=False, num_runs=1)
        inprogress['training_load']['training_load'] = 12.0
        self.window.aggregates = [complete, inprogress]
        self.window.activities = []
        self._run_update()

        load_score_text = self.window.summary_panel.load_score_label.text()
        # We don't know the exact formatting, but 70 should appear (the
        # last-complete value), not 12.
        self.assertIn("70", load_score_text)
        self.assertNotIn("12.0", load_score_text)


if __name__ == "__main__":
    unittest.main()
