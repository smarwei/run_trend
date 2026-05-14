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

        # Big score number reflects a complete period (54 for num_runs=4),
        # not the partial period's score of 51. No visible "last complete
        # period" annotation — the score label stays compact.
        score_text = self.window.summary_panel.score_label.text()
        self.assertIn("54", score_text)
        self.assertNotIn("last complete", score_text)
        self.assertNotIn("(", score_text)

    def test_complete_current_period_uses_latest(self):
        base = datetime(2026, 1, 5)
        self.window.aggregates = [
            _aggregate(base, complete=True, num_runs=4),
            _aggregate(base + timedelta(weeks=1), complete=True, num_runs=4),
            _aggregate(base + timedelta(weeks=2), complete=True, num_runs=5),
        ]
        self.window.activities = []
        self._run_update()

        score_text = self.window.summary_panel.score_label.text()
        self.assertIn("55", score_text)  # 50 + 5

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

    def test_fitness_hint_when_hr_rest_missing(self):
        # Birth date + gender + manual HRmax set, but no hr_rest → hint.
        self.window.settings.set('birth_date', '1990-01-01')
        self.window.settings.set('gender', 'male')
        self.window.settings.set('manual_hrmax', 195)
        self.window.settings.set('hr_rest', 0)
        self.window.aggregates = [
            _aggregate(datetime(2026, 1, 5), complete=True, num_runs=4),
        ]
        self.window.activities = []
        self._run_update()

        text = self.window.summary_panel.training_fitness_label.text()
        self.assertIn("Resting HR", text)

    def test_fitness_hint_when_gender_missing(self):
        self.window.settings.set('birth_date', '1990-01-01')
        self.window.settings.set('gender', '')
        self.window.settings.set('manual_hrmax', 195)
        self.window.settings.set('hr_rest', 50)
        self.window.aggregates = [
            _aggregate(datetime(2026, 1, 5), complete=True, num_runs=4),
        ]
        self.window.activities = []
        self._run_update()

        text = self.window.summary_panel.training_fitness_label.text()
        self.assertIn("Gender", text)

    def test_fitness_hint_when_hrmax_unknown(self):
        # No manual HRmax and no birth date → can't derive Tanaka either.
        self.window.settings.set('birth_date', '')
        self.window.settings.set('gender', 'male')
        self.window.settings.set('manual_hrmax', 0)
        self.window.settings.set('hr_rest', 50)
        self.window.aggregates = [
            _aggregate(datetime(2026, 1, 5), complete=True, num_runs=4),
        ]
        self.window.activities = []
        self._run_update()

        text = self.window.summary_panel.training_fitness_label.text()
        self.assertIn("Max HR", text)
        self.assertIn("Date of Birth", text)

    def test_fitness_hint_when_no_hr_activities(self):
        # All prereqs configured, but activities have no HR data.
        self.window.settings.set('birth_date', '1990-01-01')
        self.window.settings.set('gender', 'male')
        self.window.settings.set('manual_hrmax', 195)
        self.window.settings.set('hr_rest', 50)
        self.window.aggregates = [
            _aggregate(datetime(2026, 1, 5), complete=True, num_runs=4),
        ]
        self.window.activities = [
            {
                'strava_id': 1, 'name': 'Run', 'type': 'Run',
                'start_date': '2026-01-05T10:00:00',
                'distance': 5000.0, 'moving_time': 1800,
                # No average_heartrate.
            },
        ]
        self._run_update()

        text = self.window.summary_panel.training_fitness_label.text()
        self.assertIn("HR-equipped", text)

    def test_fitness_computed_with_full_prereqs(self):
        self.window.settings.set('birth_date', '1990-01-01')
        self.window.settings.set('gender', 'male')
        self.window.settings.set('manual_hrmax', 195)
        self.window.settings.set('hr_rest', 50)
        # 30 days of moderate HR runs to build up some CTL.
        base = datetime(2026, 1, 1)
        self.window.aggregates = [
            _aggregate(base, complete=True, num_runs=4),
        ]
        self.window.activities = [
            {
                'strava_id': i,
                'name': f'Run {i}',
                'type': 'Run',
                'start_date': (base + timedelta(days=i)).isoformat(),
                'distance': 10000.0,
                'moving_time': 3000,
                'average_heartrate': 145,
            }
            for i in range(30)
        ]
        self._run_update()

        text = self.window.summary_panel.training_fitness_label.text()
        # Should show a numeric CTL — not the literal placeholder.
        self.assertNotIn("-", text.replace("Training Fitness:", ""))
        self.assertRegex(text, r"\d")
        form_text = self.window.summary_panel.form_label.text()
        self.assertRegex(form_text, r"[+-]?\d")

    def test_label_says_trend_not_score(self):
        # T39: the old "Score:" label is now "Trend:" — semantically more
        # honest since the underlying value is baseline-relative, not
        # absolute fitness.
        self.window.settings.set('birth_date', '1990-01-01')
        self.window.settings.set('gender', 'male')
        self.window.settings.set('manual_hrmax', 195)
        self.window.settings.set('hr_rest', 50)
        self.window.aggregates = [
            _aggregate(datetime(2026, 1, 5), complete=True, num_runs=4),
        ]
        self.window.activities = []
        self._run_update()

        text = self.window.summary_panel.score_label.text()
        self.assertIn("Trend", text)
        self.assertNotIn("Score:", text)

    def test_trend_subtitle_visible_static(self):
        # T39: the "relative to your baseline" subtitle is statically
        # present (no hover required) so the baseline-relative reading
        # is obvious.
        self.window.settings.set('birth_date', '1990-01-01')
        self.window.settings.set('gender', 'male')
        self.window.settings.set('manual_hrmax', 195)
        self.window.settings.set('hr_rest', 50)
        self.window.aggregates = [
            _aggregate(datetime(2026, 1, 5), complete=True, num_runs=4),
        ]
        self.window.activities = []
        self._run_update()

        subtitle = self.window.summary_panel.trend_subtitle_label
        self.assertIn("baseline", subtitle.text())

    def test_acwr_label_without_activities_shows_placeholder(self):
        # T40: the panel now sources ACWR from the daily-load pipeline,
        # not from aggregate periods. With no activities the daily map
        # is empty → label reads "ACWR: -" rather than a stale period
        # value. (Replaces the pre-T40 last-complete-period guard;
        # there is no periodic ACWR anymore.)
        base = datetime(2026, 1, 5)
        self.window.aggregates = [
            _aggregate(base, complete=True, num_runs=4),
        ]
        self.window.activities = []
        self._run_update()

        load_score_text = self.window.summary_panel.load_score_label.text()
        self.assertIn("ACWR", load_score_text)
        self.assertIn("-", load_score_text)

    def test_acwr_label_shows_ratio_with_28_days_of_activities(self):
        # T40 happy path: 30 days of HR-equipped runs → daily TRIMP
        # populated → ACWR computed from the rolling window. Expect
        # roughly 1.0 (steady-state, acute ≈ chronic).
        self.window.settings.set('birth_date', '1990-01-01')
        self.window.settings.set('gender', 'male')
        self.window.settings.set('manual_hrmax', 195)
        self.window.settings.set('hr_rest', 50)
        base = datetime(2026, 1, 1)
        self.window.aggregates = [
            _aggregate(base, complete=True, num_runs=4),
        ]
        self.window.activities = [
            {
                'strava_id': i,
                'name': f'Run {i}',
                'type': 'Run',
                'start_date': (base + timedelta(days=i)).isoformat(),
                'distance': 10000.0,
                'moving_time': 3000,
                'average_heartrate': 145,
            }
            for i in range(30)
        ]
        self._run_update()

        label_text = self.window.summary_panel.load_score_label.text()
        self.assertIn("ACWR", label_text)
        self.assertRegex(label_text, r"\d\.\d{2}")  # has a 1.05-shaped value
        self.assertIn("TRIMP", label_text)


if __name__ == "__main__":
    unittest.main()
