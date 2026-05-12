"""
Age-graded performance chart (Ticket 37).

Two views in an inner QTabWidget:

* **WMA Age-Grading** — published WMA-2023 factor tables. Per-period
  age-graded percentage for 5K / 10K / Half Marathon / Marathon based
  on race-time predictions, with optional overlay of actually-run
  races from race_markers.
* **Aerobic Capacity vs Age** — measured Efficiency Factor compared
  to a self-calibrated personal-peak EF, with the age-driven decline
  curve projected forward from that peak using a volume-coupled
  model.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, QDateTime
from PySide6.QtCharts import (
    QChart, QChartView, QDateTimeAxis, QLineSeries, QScatterSeries, QValueAxis,
)
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QLabel, QStackedWidget, QTabWidget, QVBoxLayout, QWidget,
)

from .base_chart import BaseChart
from ..analytics import age_grading as ag
from ..analytics.race_predictor import RacePredictor
from ..ui.help_label import make_help_icon


_DISTANCE_LABELS_TR_KEYS = ("5K", "10K", "Half Marathon", "Marathon")
_DISTANCE_KM = {"5K": 5.0, "10K": 10.0, "Half Marathon": 21.0975, "Marathon": 42.195}
# Riegel time-distance scaling exponent — empirical fit, widely used since
# Riegel (1981). 1.06 is the canonical value for running across 5K–marathon.
_RIEGEL_EXPONENT = 1.06
_LINE_COLORS = {
    "5K": "#3498db",
    "10K": "#27ae60",
    "Half Marathon": "#e67e22",
    "Marathon": "#e74c3c",
}
_REFERENCE_BANDS = (60, 70, 80, 90, 100)  # local/regional/national/intl/WR
_ROLLING_WINDOW_MONTHS = 3


class AgeGradingChart(BaseChart):
    """Performance vs age-adjusted reference. Two inner tabs (WMA + HF)."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    # ------------------------------------------------------------------ #
    # UI scaffolding                                                       #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        self._outer_stack = QStackedWidget()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._outer_stack)

        # Page 0: tabbed data view.
        data_page = QWidget()
        dl = QVBoxLayout(data_page)

        self.tabs = QTabWidget()
        self.wma_view = self._build_chart_page(
            self.tr("WMA Age-Graded Performance"),
            help_text=self.tr(
                "WMA age-graded percentage = (world record × age factor) "
                "÷ your time × 100.\n\n"
                "Source: World Masters Athletics 2023 factor tables "
                "(per-year, all distances).\n\n"
                "Reference bands:\n"
                "  ≥ 90 %: international class\n"
                "  80–90 %: national class\n"
                "  70–80 %: regional class\n"
                "  60–70 %: local class\n"
                "  < 60 %: recreational\n\n"
                "Each line is a 3-month rolling prediction (5K/10K/HM/"
                "Marathon) from your HR-classified easy-run pace. Real "
                "races marked via right-click on a run appear as larger "
                "scatter points on top of their line."
            ),
        )
        self.hf_view = self._build_chart_page(
            self.tr("Aerobic Capacity vs Age"),
            help_text=self.tr(
                "Efficiency Factor (EF) over time compared to your own "
                "personal peak in the last 12 months, adjusted for age.\n\n"
                "We do NOT compare your EF to other athletes — Friel and "
                "TrainingPeaks explicitly warn against that. Instead the "
                "reference line is your best 4-week EF mean in the past "
                "year, extrapolated forward using the age-driven decline "
                "rate from the literature (Coppola et al. 2022): 0.55 %/yr "
                "at full training volume, rising to ~3 %/yr at sedentary.\n\n"
                "Linear decline is a first approximation; real decline "
                "accelerates past age 70 as mitochondrial mechanisms take "
                "over. Treat the gap between measured and expected as a "
                "training-response indicator, not a diagnosis."
            ),
        )
        self.tabs.addTab(self.wma_view['widget'], self.tr("WMA Age-Graded %"))
        self.tabs.addTab(self.hf_view['widget'], self.tr("Aerobic Capacity %"))
        dl.addWidget(self.tabs)

        self._outer_stack.addWidget(data_page)

        # Page 1: empty-state placeholder.
        empty = QWidget()
        el = QVBoxLayout(empty)
        el.addStretch()
        self._empty_label = QLabel("")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setWordWrap(True)
        self._empty_label.setStyleSheet(
            "color: gray; font-size: 13px; padding: 20px;"
        )
        el.addWidget(self._empty_label)
        el.addStretch()
        self._outer_stack.addWidget(empty)

    def _build_chart_page(self, title: str, help_text: str) -> Dict[str, Any]:
        chart = QChart()
        chart.setTitle(title)
        # Avoid the QAreaSeries-style replay race when we swap series on
        # refresh (cheap insurance even though we use QLineSeries here).
        chart.setAnimationOptions(QChart.NoAnimation)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)

        container = QWidget()
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)

        header = QVBoxLayout()
        title_row = make_help_icon(help_text)
        header.addWidget(title_row, alignment=Qt.AlignRight)
        cl.addLayout(header)

        self_label_holder = QLabel("")
        self_label_holder.setStyleSheet("font-size: 13px; padding: 4px;")
        cl.addWidget(self_label_holder)
        cl.addWidget(view)

        return {
            'widget': container,
            'chart': chart,
            'view': view,
            'header_label': self_label_holder,
            # Holders for the lines we plot, so QChart's GC doesn't free
            # them prematurely between renders (PYSIDE-1285).
            'series': [],
        }

    # ------------------------------------------------------------------ #
    # Public refresh                                                       #
    # ------------------------------------------------------------------ #

    def update_chart(
        self,
        aggregates: List[Dict[str, Any]],
        activities: List[Dict[str, Any]],
        settings: Dict[str, Any],
        race_markers: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Re-render both inner tabs based on the latest data + settings.

        ``settings`` is a plain dict snapshot with at least
        ``birth_date`` (ISO), ``gender`` (str), and ``manual_hrmax`` (int).
        Passing a dict rather than a live AppSettings keeps the chart
        unit-testable.
        """
        birth_date_iso = (settings.get('birth_date') or '').strip()
        gender = (settings.get('gender') or '').strip()
        manual_hrmax = int(settings.get('manual_hrmax', 0) or 0)

        birth_date: Optional[date] = None
        if birth_date_iso:
            try:
                birth_date = date.fromisoformat(birth_date_iso)
            except ValueError:
                birth_date = None

        if birth_date is None:
            self._show_empty(self.tr(
                "Set your date of birth in Settings → General to enable "
                "the Performance charts."
            ))
            return

        # Data tab is the default; the inner tabs decide their own
        # empty-state hints.
        self._outer_stack.setCurrentIndex(0)

        self._render_wma(aggregates, activities, birth_date, gender,
                         manual_hrmax, race_markers or [])
        self._render_hf(aggregates, birth_date, manual_hrmax)

    def _show_empty(self, message: str) -> None:
        self._empty_label.setText(message)
        self._outer_stack.setCurrentIndex(1)

    # ------------------------------------------------------------------ #
    # WMA tab                                                              #
    # ------------------------------------------------------------------ #

    def _render_wma(
        self,
        aggregates: List[Dict[str, Any]],
        activities: List[Dict[str, Any]],
        birth_date: date,
        gender: str,
        manual_hrmax: int,
        race_markers: List[Dict[str, Any]],
    ) -> None:
        view = self.wma_view
        chart = view['chart']
        # Clear previous series + axes.
        for s in list(chart.series()):
            chart.removeSeries(s)
        for ax in list(chart.axes()):
            chart.removeAxis(ax)
        view['series'].clear()

        if not gender:
            view['header_label'].setText(self.tr(
                "Gender required for WMA — set it in Settings → General."
            ))
            return

        complete = self._filter_complete_aggregates(aggregates)
        if not complete:
            view['header_label'].setText(self.tr("Not enough complete periods yet."))
            return

        # Build per-distance time series.
        per_distance_points: Dict[str, List[tuple]] = {
            d: [] for d in _DISTANCE_LABELS_TR_KEYS
        }
        latest_pct_label: Dict[str, Optional[float]] = {
            d: None for d in _DISTANCE_LABELS_TR_KEYS
        }

        used_fallback = 0
        used_hr_method = 0
        for agg in complete:
            period_dt: datetime = agg['period_date']
            window_start = period_dt - timedelta(days=30 * _ROLLING_WINDOW_MONTHS)
            window_runs = _runs_in_window(activities, window_start, period_dt)

            predictions: Optional[Dict[str, Dict[str, Any]]] = None
            # Preferred: HR-classified easy runs → McMillan via RacePredictor.
            if len(window_runs) >= 3:
                pred = RacePredictor.estimate_race_times(
                    window_runs,
                    max_hr=manual_hrmax if manual_hrmax > 0 else 200,
                    efficiency_factor=agg.get('efficiency_factor'),
                    recent_months=_ROLLING_WINDOW_MONTHS,
                    manual_hrmax=manual_hrmax if manual_hrmax > 0 else None,
                )
                if pred and pred.get('has_prediction'):
                    predictions = pred['predictions']
                    used_hr_method += 1

            # Fallback: Riegel scaling from the aggregate's own average-run
            # profile. Lets the chart cover periods without HR data so it
            # actually starts where the user's training_start_date does.
            if predictions is None:
                predictions = _riegel_from_aggregate(agg)
                if predictions is not None:
                    used_fallback += 1

            if predictions is None:
                continue
            age = ag.age_on_date(birth_date, period_dt.date())
            ts_ms = int(period_dt.timestamp() * 1000)
            for dist in _DISTANCE_LABELS_TR_KEYS:
                pred_for_dist = predictions.get(dist)
                if not pred_for_dist:
                    continue
                time_s = pred_for_dist['total_time_minutes'] * 60.0
                pct = ag.wma_percent(time_s, dist, age, gender)
                if pct is None:
                    continue
                per_distance_points[dist].append((ts_ms, pct))
                latest_pct_label[dist] = pct

        any_data = any(per_distance_points.values())
        if not any_data:
            view['header_label'].setText(self.tr(
                "Not enough HR-classified easy runs yet for race "
                "predictions. The chart fills in as you log more runs."
            ))
            return

        # Determine x/y ranges.
        all_dates_ms = [p[0] for pts in per_distance_points.values() for p in pts]
        x_min = min(all_dates_ms)
        x_max = max(all_dates_ms)
        all_y = [p[1] for pts in per_distance_points.values() for p in pts]
        y_min = max(0.0, min(all_y) - 5)
        y_max = min(120.0, max(all_y) + 5)

        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        axis_x.setRange(
            QDateTime.fromMSecsSinceEpoch(x_min),
            QDateTime.fromMSecsSinceEpoch(x_max),
        )
        axis_y = QValueAxis()
        axis_y.setTitleText(self.tr("Age-graded %"))
        axis_y.setLabelFormat("%.0f")
        axis_y.setRange(y_min, y_max)
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        # Reference bands as faint horizontal lines.
        for ref_pct in _REFERENCE_BANDS:
            if not (y_min <= ref_pct <= y_max):
                continue
            line = QLineSeries()
            line.setName(self.tr("Ref {} %").format(ref_pct))
            line.append(x_min, ref_pct)
            line.append(x_max, ref_pct)
            pen = QPen(QColor(160, 160, 160, 140))
            pen.setStyle(Qt.DotLine)
            pen.setWidth(1)
            line.setPen(pen)
            chart.addSeries(line)
            line.attachAxis(axis_x)
            line.attachAxis(axis_y)
            view['series'].append(line)

        # One line per distance.
        for dist in _DISTANCE_LABELS_TR_KEYS:
            pts = per_distance_points[dist]
            if not pts:
                continue
            line = QLineSeries()
            line.setName(self._distance_translated(dist))
            for ts, pct in pts:
                line.append(ts, pct)
            pen = QPen(QColor(_LINE_COLORS[dist]))
            pen.setWidth(2)
            line.setPen(pen)
            chart.addSeries(line)
            line.attachAxis(axis_x)
            line.attachAxis(axis_y)
            view['series'].append(line)

        # Race-marker overlay (T37 slice 5): scatter points at actual race
        # times. race_markers expected as list of dicts:
        #   { 'race_date': 'YYYY-MM-DD', 'distance_km': float,
        #     'time_s': float, ... }
        scatter_added = 0
        for marker in race_markers:
            time_s = marker.get('time_s')
            try:
                dist_km = float(marker.get('distance_km', 0))
            except (TypeError, ValueError):
                continue
            if not time_s or dist_km <= 0:
                continue
            dist_label = _nearest_distance_label(dist_km)
            if dist_label is None:
                continue
            race_date_str = marker.get('race_date') or marker.get('date')
            if not race_date_str:
                continue
            try:
                race_dt = datetime.fromisoformat(race_date_str)
            except ValueError:
                continue
            age = ag.age_on_date(birth_date, race_dt.date())
            pct = ag.wma_percent(float(time_s), dist_label, age, gender)
            if pct is None:
                continue
            scatter = QScatterSeries()
            scatter.setName(self.tr("Race: {}").format(self._distance_translated(dist_label)))
            scatter.setColor(QColor(_LINE_COLORS[dist_label]).darker(120))
            scatter.setMarkerSize(12)
            scatter.setBorderColor(QColor(40, 40, 40))
            scatter.append(int(race_dt.timestamp() * 1000), pct)
            chart.addSeries(scatter)
            scatter.attachAxis(axis_x)
            scatter.attachAxis(axis_y)
            view['series'].append(scatter)
            scatter_added += 1

        # Header summary.
        parts = []
        for dist in _DISTANCE_LABELS_TR_KEYS:
            pct = latest_pct_label[dist]
            if pct is None:
                continue
            parts.append(
                f"{self._distance_translated(dist)}: {pct:.0f}%"
            )
        suffix = ""
        if scatter_added:
            suffix = "  •  " + self.tr("{} real races overlaid").format(scatter_added)
        # Note when the fallback contributed so the user knows some
        # points are pace-only (no HR classification).
        method_note = ""
        if used_fallback and used_hr_method:
            method_note = "  •  " + self.tr(
                "{} HR-based, {} pace-only (no HR data)"
            ).format(used_hr_method, used_fallback)
        elif used_fallback and not used_hr_method:
            method_note = "  •  " + self.tr(
                "pace-based fallback (no HR-classified easy runs found)"
            )
        view['header_label'].setText(
            (self.tr("Latest age-graded %") + ":  " + "  |  ".join(parts)
             + method_note + suffix)
            if parts else self.tr("No predictions yet.")
        )

    # ------------------------------------------------------------------ #
    # HF tab                                                               #
    # ------------------------------------------------------------------ #

    def _render_hf(
        self,
        aggregates: List[Dict[str, Any]],
        birth_date: date,
        manual_hrmax: int,
    ) -> None:
        view = self.hf_view
        chart = view['chart']
        for s in list(chart.series()):
            chart.removeSeries(s)
        for ax in list(chart.axes()):
            chart.removeAxis(ax)
        view['series'].clear()

        complete = self._filter_complete_aggregates(aggregates)
        # Need EF history. Build the (date, ef × 1000) series.
        ef_dated = []
        for agg in complete:
            ef = agg.get('efficiency_factor')
            if ef is None or ef <= 0:
                continue
            ef_dated.append((agg['period_date'], ef * 1000.0))

        if len(ef_dated) < 4:
            view['header_label'].setText(self.tr(
                "Need at least 4 periods with HR-derived EF to build the "
                "personal peak. Keep logging runs with heart-rate data."
            ))
            return

        peak = ag.personal_peak_ef(ef_dated, window_weeks=4, lookback_days=365)
        if peak is None:
            view['header_label'].setText(self.tr(
                "Not enough history in the last 12 months for a personal "
                "peak."
            ))
            return
        peak_value, peak_date = peak

        # Volume ratio: average distance in the last 4 periods divided by
        # the average around the peak date.
        peak_volume = _avg_volume_around(complete, peak_date, half_window_periods=2)
        latest_dt = complete[-1]['period_date']
        recent_volume = _avg_volume_around(complete, latest_dt, half_window_periods=2)
        if peak_volume > 0:
            volume_ratio = recent_volume / peak_volume
        else:
            volume_ratio = 1.0

        # Build measured + expected series.
        measured = QLineSeries()
        measured.setName(self.tr("Measured EF × 1000"))
        for d, v in ef_dated:
            measured.append(int(d.timestamp() * 1000), v)
        m_pen = QPen(QColor("#2ecc71"))
        m_pen.setWidth(2)
        measured.setPen(m_pen)

        expected = QLineSeries()
        expected.setName(self.tr("Expected (age-adjusted personal peak)"))
        for d, _ in ef_dated:
            e = ag.expected_ef(peak_value, peak_date, d, volume_ratio)
            expected.append(int(d.timestamp() * 1000), e)
        e_pen = QPen(QColor("#e67e22"))
        e_pen.setWidth(2)
        e_pen.setStyle(Qt.DashLine)
        expected.setPen(e_pen)

        # Axes.
        all_v = [v for _, v in ef_dated]
        peak_line_val = peak_value
        y_min = max(0.0, min(all_v + [peak_line_val]) * 0.95)
        y_max = max(all_v + [peak_line_val]) * 1.05

        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        axis_x.setRange(
            QDateTime.fromMSecsSinceEpoch(int(ef_dated[0][0].timestamp() * 1000)),
            QDateTime.fromMSecsSinceEpoch(int(ef_dated[-1][0].timestamp() * 1000)),
        )
        axis_y = QValueAxis()
        axis_y.setTitleText(self.tr("Efficiency Factor (m/s per bpm × 1000)"))
        axis_y.setLabelFormat("%.1f")
        axis_y.setRange(y_min, y_max)
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        # Horizontal peak-reference.
        peak_line = QLineSeries()
        peak_line.setName(self.tr("Personal peak (best 4 wk)"))
        peak_line.append(int(ef_dated[0][0].timestamp() * 1000), peak_line_val)
        peak_line.append(int(ef_dated[-1][0].timestamp() * 1000), peak_line_val)
        p_pen = QPen(QColor(120, 120, 120, 180))
        p_pen.setStyle(Qt.DotLine)
        p_pen.setWidth(1)
        peak_line.setPen(p_pen)

        for s in (peak_line, expected, measured):
            chart.addSeries(s)
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)
            view['series'].append(s)

        # Header summary.
        latest_ef = ef_dated[-1][1]
        latest_expected = ag.expected_ef(peak_value, peak_date, ef_dated[-1][0], volume_ratio)
        pct = ag.aerobic_capacity_percent(latest_ef, latest_expected)
        rate_pct_yr = ag.vo2max_annual_decline_rate(volume_ratio) * 100.0
        view['header_label'].setText(
            self.tr(
                "Current EF: {:.1f}  •  {:.0f}% of age-adjusted peak  •  "
                "Decline rate ~{:.1f}%/yr (vol ratio {:.2f})"
            ).format(
                latest_ef,
                pct if pct is not None else 0.0,
                rate_pct_yr,
                volume_ratio,
            )
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _distance_translated(self, distance_label: str) -> str:
        """Use the same translations as ProjectionChart for consistency."""
        translations = {
            "5K": self.tr("5K"),
            "10K": self.tr("10K"),
            "Half Marathon": self.tr("Half Marathon"),
            "Marathon": self.tr("Marathon"),
        }
        return translations.get(distance_label, distance_label)


def _riegel_from_aggregate(agg: Dict[str, Any]) -> Optional[Dict[str, Dict[str, Any]]]:
    """Build race-time predictions from a period's pace + average-distance.

    Uses Riegel's empirical formula ``T2 = T1 × (D2/D1)^1.06`` to scale
    the user's typical training-run profile (avg pace × avg distance)
    to 5K / 10K / HM / Marathon.

    This is the fallback when HR-based McMillan classification doesn't
    produce a prediction (historical periods without HR data, or runs
    that don't sit in the 60–75 % HRmax Easy-Run window). Less precise
    than HR-classified, but lets the chart actually cover the user's
    full training_start_date range.

    Returns ``None`` if the aggregate lacks the inputs (zero pace or
    distance).
    """
    pace_min_per_km = agg.get('weighted_avg_pace_min_per_km') or 0
    avg_distance_km = agg.get('avg_distance_per_run_km') or 0
    if pace_min_per_km <= 0 or avg_distance_km <= 0:
        return None
    known_time_min = pace_min_per_km * avg_distance_km
    if known_time_min <= 0:
        return None
    out: Dict[str, Dict[str, Any]] = {}
    for race_name, target_km in _DISTANCE_KM.items():
        time_min = known_time_min * (target_km / avg_distance_km) ** _RIEGEL_EXPONENT
        out[race_name] = {
            'total_time_minutes': time_min,
            'pace_min_per_km': time_min / target_km,
        }
    return out


def _runs_in_window(
    activities: List[Dict[str, Any]],
    window_start: datetime,
    window_end: datetime,
) -> List[Dict[str, Any]]:
    """Filter activities to those falling in [window_start, window_end].

    Returns the dicts in the shape RacePredictor expects (``distance_km``,
    ``pace_min_per_km``, ``average_heartrate``, ``max_heartrate``).
    """
    out = []
    for a in activities:
        start = a.get('start_date')
        if not start:
            continue
        try:
            dt = datetime.fromisoformat(str(start).replace('Z', '+00:00'))
        except ValueError:
            continue
        # Strip tz so the comparison matches naive period_date.
        dt = dt.replace(tzinfo=None)
        if not (window_start <= dt <= window_end):
            continue
        distance_m = a.get('distance', 0)
        moving_time = a.get('moving_time', 0)
        if not distance_m or not moving_time:
            continue
        distance_km = distance_m / 1000.0
        pace_min_per_km = (moving_time / 60.0) / distance_km if distance_km > 0 else 0
        out.append({
            'distance_km': distance_km,
            'pace_min_per_km': pace_min_per_km,
            'average_heartrate': a.get('average_heartrate'),
            'max_heartrate': a.get('max_heartrate'),
        })
    return out


def _nearest_distance_label(distance_km: float) -> Optional[str]:
    """Map an actual race distance to the closest WMA-supported label.

    Returns ``None`` if the distance is too far from any supported one
    (more than 10 % off).
    """
    best_label = None
    best_ratio = 2.0
    for label, target in _DISTANCE_KM.items():
        ratio = abs(distance_km - target) / target
        if ratio < best_ratio:
            best_ratio = ratio
            best_label = label
    return best_label if best_ratio <= 0.10 else None


def _avg_volume_around(
    complete: List[Dict[str, Any]],
    centre: datetime,
    half_window_periods: int = 2,
) -> float:
    """Return mean total_distance_km in the (2×half_window+1)-period
    window centred on ``centre``."""
    # Find index of period nearest to centre.
    if not complete:
        return 0.0
    nearest_idx = min(
        range(len(complete)),
        key=lambda i: abs((complete[i]['period_date'] - centre).total_seconds()),
    )
    lo = max(0, nearest_idx - half_window_periods)
    hi = min(len(complete), nearest_idx + half_window_periods + 1)
    window = complete[lo:hi]
    if not window:
        return 0.0
    return sum(a.get('total_distance_km', 0) for a in window) / len(window)
