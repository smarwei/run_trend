"""
Tests for AgeGradingChart (Ticket 37 slices 3-5).
"""
import os
import unittest
from datetime import datetime, timedelta

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from run_trend.charts.age_grading_chart import AgeGradingChart


def _ensure_qapplication():
    return QApplication.instance() or QApplication([])


def _aggregates(num_periods: int = 20, with_hr: bool = True) -> list:
    """Synthetic complete weekly aggregates ending today."""
    end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    aggs = []
    for i in range(num_periods):
        d = end - timedelta(weeks=(num_periods - 1 - i))
        aggs.append({
            'period_date': d,
            'period_start': d.isoformat(),
            'period': d.strftime('%Y-W%U'),
            'total_distance_km': 40.0 + i * 0.5,
            'total_moving_time_h': 4.0,
            'num_runs': 4,
            'avg_distance_per_run_km': (40.0 + i * 0.5) / 4,
            'weighted_avg_pace_min_per_km': 5.0,
            'avg_speed_kmh': 12.0,
            'efficiency_factor': 0.024 + 0.0005 * (i % 4) if with_hr else 0.0,
            'avg_heartrate': 150 if with_hr else 0,
            'num_hr_activities': 4 if with_hr else 0,
            'is_complete': True,
        })
    return aggs


def _activities(num: int = 60, hrmax: int = 180) -> list:
    """Synthetic activities for the rolling-window pipeline.

    Pace ≈ 5:00/km, HR set to ~70% of hrmax so RacePredictor classifies
    them all as easy runs (its window is 60–75% HRmax)."""
    end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    avg_hr = int(round(hrmax * 0.70))
    out = []
    for i in range(num):
        dt = end - timedelta(days=num - i)
        out.append({
            'strava_id': i,
            'name': f'Run {i}',
            'type': 'Run',
            'start_date': dt.isoformat(),
            'distance': 10000.0,
            'moving_time': 3000,  # 50 min → 5:00/km
            'average_speed': 3.33,
            'average_heartrate': avg_hr,
            'max_heartrate': hrmax - 10,
            'has_heartrate': True,
        })
    return out


class TestEmptyStates(unittest.TestCase):

    def setUp(self):
        _ensure_qapplication()
        self.chart = AgeGradingChart()

    def test_empty_when_no_birth_date(self):
        self.chart.update_chart(
            aggregates=_aggregates(),
            activities=_activities(),
            settings={'birth_date': '', 'gender': 'male', 'manual_hrmax': 180},
        )
        self.assertEqual(self.chart._outer_stack.currentIndex(), 1)
        self.assertTrue(self.chart._empty_label.text())

    def test_empty_when_birth_date_malformed(self):
        self.chart.update_chart(
            aggregates=_aggregates(),
            activities=_activities(),
            settings={'birth_date': 'nope', 'gender': 'male', 'manual_hrmax': 180},
        )
        self.assertEqual(self.chart._outer_stack.currentIndex(), 1)


class TestWmaTabRendering(unittest.TestCase):

    def setUp(self):
        _ensure_qapplication()
        self.chart = AgeGradingChart()

    def test_data_page_active_when_birth_date_set(self):
        self.chart.update_chart(
            aggregates=_aggregates(),
            activities=_activities(),
            settings={
                'birth_date': '1990-01-01',
                'gender': 'male',
                'manual_hrmax': 180,
            },
        )
        # Page 0 = data, page 1 = empty.
        self.assertEqual(self.chart._outer_stack.currentIndex(), 0)

    def test_gender_required_header_when_missing(self):
        self.chart.update_chart(
            aggregates=_aggregates(),
            activities=_activities(),
            settings={'birth_date': '1990-01-01', 'gender': '', 'manual_hrmax': 180},
        )
        # Data page is shown, but WMA header explains the gap.
        self.assertEqual(self.chart._outer_stack.currentIndex(), 0)
        text = self.chart.wma_view['header_label'].text()
        self.assertIn("Gender", text)

    def test_race_marker_overlay_adds_scatter_series(self):
        from PySide6.QtCharts import QScatterSeries
        markers = [
            {
                'race_date': (datetime.now() - timedelta(days=14)).isoformat(),
                'distance_km': 10.0,  # matches "10K"
                'time_s': 2700.0,  # 45:00 — reasonable masters time
            }
        ]
        self.chart.update_chart(
            aggregates=_aggregates(num_periods=25),
            activities=_activities(num=80),
            settings={
                'birth_date': '1980-01-01',
                'gender': 'male',
                'manual_hrmax': 180,
            },
            race_markers=markers,
        )
        scatters = [
            s for s in self.chart.wma_view['chart'].series()
            if isinstance(s, QScatterSeries)
        ]
        self.assertEqual(len(scatters), 1)

    def test_unsupported_race_marker_distance_ignored(self):
        from PySide6.QtCharts import QScatterSeries
        markers = [
            {
                'race_date': (datetime.now() - timedelta(days=10)).isoformat(),
                'distance_km': 8.0,  # ~20% off all WMA labels — ignored
                'time_s': 2200.0,
            }
        ]
        self.chart.update_chart(
            aggregates=_aggregates(num_periods=25),
            activities=_activities(num=80),
            settings={
                'birth_date': '1980-01-01',
                'gender': 'male',
                'manual_hrmax': 180,
            },
            race_markers=markers,
        )
        scatters = [
            s for s in self.chart.wma_view['chart'].series()
            if isinstance(s, QScatterSeries)
        ]
        self.assertEqual(len(scatters), 0)


class TestRiegelFallback(unittest.TestCase):
    """Periods without HR-classified easy runs still need predictions —
    otherwise the chart starts wherever HR coverage starts, not at the
    user's training_start_date."""

    def setUp(self):
        _ensure_qapplication()
        self.chart = AgeGradingChart()

    def test_aggregate_without_hr_still_renders_lines(self):
        from PySide6.QtCharts import QLineSeries
        # Build aggregates where HR data is entirely absent.
        no_hr_aggs = _aggregates(num_periods=20, with_hr=False)
        # Activities also without HR — RacePredictor would fail.
        no_hr_acts = []
        end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(40):
            dt = end - timedelta(days=40 - i)
            no_hr_acts.append({
                'strava_id': i,
                'name': f'Run {i}',
                'type': 'Run',
                'start_date': dt.isoformat(),
                'distance': 8000.0,
                'moving_time': 2640,  # 5:30/km × 8km
                'average_speed': 3.03,
                'has_heartrate': False,
            })
        self.chart.update_chart(
            aggregates=no_hr_aggs,
            activities=no_hr_acts,
            settings={
                'birth_date': '1990-01-01',
                'gender': 'male',
                'manual_hrmax': 0,  # unset → HR-method should fail
            },
        )
        wma_chart = self.chart.wma_view['chart']
        line_series = [
            s for s in wma_chart.series() if isinstance(s, QLineSeries)
        ]
        # 4 distances × 1 line + reference bands. We just check ≥ 4 actual
        # data lines (the ones with non-zero start_date plot points).
        data_lines = [s for s in line_series if s.count() > 2]
        self.assertGreaterEqual(len(data_lines), 4)

    def test_header_notes_fallback_when_no_hr(self):
        no_hr_aggs = _aggregates(num_periods=15, with_hr=False)
        end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        acts = [
            {
                'strava_id': i,
                'name': f'r{i}',
                'type': 'Run',
                'start_date': (end - timedelta(days=30 - i)).isoformat(),
                'distance': 8000.0,
                'moving_time': 2640,
                'average_speed': 3.03,
            }
            for i in range(30)
        ]
        self.chart.update_chart(
            aggregates=no_hr_aggs,
            activities=acts,
            settings={
                'birth_date': '1990-01-01',
                'gender': 'male',
                'manual_hrmax': 0,
            },
        )
        header = self.chart.wma_view['header_label'].text()
        # Fallback-only mode: header contains the explicit note.
        self.assertIn("pace-based", header)


class TestRiegelHelper(unittest.TestCase):
    """Direct check of the _riegel_from_aggregate helper."""

    def test_predicts_all_four_distances(self):
        from run_trend.charts.age_grading_chart import _riegel_from_aggregate
        agg = {
            'weighted_avg_pace_min_per_km': 5.5,
            'avg_distance_per_run_km': 8.0,
        }
        result = _riegel_from_aggregate(agg)
        self.assertIsNotNone(result)
        self.assertEqual(
            set(result.keys()),
            {'5K', '10K', 'Half Marathon', 'Marathon'},
        )
        # Marathon time should be longer than HM time (Riegel monotone).
        self.assertGreater(
            result['Marathon']['total_time_minutes'],
            result['Half Marathon']['total_time_minutes'],
        )

    def test_returns_none_for_missing_inputs(self):
        from run_trend.charts.age_grading_chart import _riegel_from_aggregate
        self.assertIsNone(_riegel_from_aggregate({}))
        self.assertIsNone(_riegel_from_aggregate({'weighted_avg_pace_min_per_km': 0,
                                                   'avg_distance_per_run_km': 5}))
        self.assertIsNone(_riegel_from_aggregate({'weighted_avg_pace_min_per_km': 5,
                                                   'avg_distance_per_run_km': 0}))


class TestHfTabRendering(unittest.TestCase):

    def setUp(self):
        _ensure_qapplication()
        self.chart = AgeGradingChart()

    def test_insufficient_history_shows_header_hint(self):
        # Only 2 EF points → too short for personal-peak (needs ≥ 4).
        self.chart.update_chart(
            aggregates=_aggregates(num_periods=2),
            activities=_activities(num=10),
            settings={
                'birth_date': '1990-01-01',
                'gender': 'male',
                'manual_hrmax': 180,
            },
        )
        header = self.chart.hf_view['header_label'].text()
        self.assertTrue(header)
        # The header is the empty-state inside the HF tab.
        self.assertIn("4", header)  # mentions the minimum samples count

    def test_renders_with_enough_ef_history(self):
        self.chart.update_chart(
            aggregates=_aggregates(num_periods=30),
            activities=_activities(num=80),
            settings={
                'birth_date': '1990-01-01',
                'gender': 'male',
                'manual_hrmax': 180,
            },
        )
        # HF chart should have at least the three lines: measured,
        # expected, peak reference.
        chart = self.chart.hf_view['chart']
        self.assertGreaterEqual(len(chart.series()), 3)
        header = self.chart.hf_view['header_label'].text()
        self.assertIn("Current EF", header)
        self.assertIn("%", header)


if __name__ == "__main__":
    unittest.main()
