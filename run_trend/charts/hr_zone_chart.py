"""
Heart-rate zone chart widget — final slice of Ticket 19.

Shows two views of zone-time-share:
- **Aggregated** stacked bars per period (week/month) over time.
- **Per Run** stacked bars for the most recent N activities.

A 80/20 indicator label sits above both, computed from the *currently
visible* dataset. Empty-state messaging covers four cases: no HR-Max
configured, no HR data at all, HR data present but no zone-cache hits,
and an outright empty dataset.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QColor, QPainter
from PySide6.QtCharts import (
    QChart, QChartView, QBarCategoryAxis, QValueAxis, QStackedBarSeries, QBarSet,
)
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QStackedWidget, QTabWidget, QVBoxLayout, QWidget,
)

from .base_chart import BaseChart
from ..analytics.hr_zones import (
    NUM_ZONES, ZONE_LABELS, aggregate_zone_seconds, polarized_ratio,
)
from ..ui.help_label import make_help_icon

logger = logging.getLogger(__name__)

# Per-zone colour palette: cool → warm.
_ZONE_COLORS = [
    "#3498db",  # Z1 — blue
    "#27ae60",  # Z2 — green
    "#f1c40f",  # Z3 — yellow
    "#e67e22",  # Z4 — orange
    "#e74c3c",  # Z5 — red
]

_PER_RUN_LIMIT = 20


class HrZoneChart(BaseChart):
    """Aggregated + per-run HR-zone stacked-bar chart with 80/20 indicator."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    # ------------------------------------------------------------------ #
    # UI                                                                   #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        # Top-level: a stack that swaps between the data view and an
        # empty-state placeholder. Built directly on `self`.
        self._outer_stack = QStackedWidget()
        wrapper = QVBoxLayout(self)
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.addWidget(self._outer_stack)

        # Page 0: indicator + tabbed views.
        data_page = QWidget()
        data_layout = QVBoxLayout(data_page)

        header = QHBoxLayout()
        self.indicator_label = QLabel("")
        self.indicator_label.setStyleSheet("font-size: 13px; padding: 4px;")
        header.addWidget(self.indicator_label)
        header.addStretch()
        header.addWidget(make_help_icon(self.tr(
            "80/20-Polarization indicator:\n\n"
            "• Low (Z1+Z2)  — easy aerobic, target ~80%\n"
            "• Middle (Z3)  — tempo, kept small in polarized training\n"
            "• High (Z4+Z5) — threshold/vo2, target ~20%\n\n"
            "Computed from the visible dataset. Needs HR-Max configured."
        )))
        data_layout.addLayout(header)

        self.tabs = QTabWidget()
        self.aggregated_view = self._build_chart_page(
            self.tr("Time in Zone (per period)")
        )
        self.per_run_view = self._build_chart_page(
            self.tr("Time in Zone (recent runs)")
        )
        self.tabs.addTab(self.aggregated_view['widget'], self.tr("Aggregated"))
        self.tabs.addTab(self.per_run_view['widget'], self.tr("Per Run"))
        data_layout.addWidget(self.tabs)

        self._outer_stack.addWidget(data_page)

        # Page 1: unified empty-state.
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

    def _build_chart_page(self, title: str) -> Dict[str, Any]:
        """Build a chart-view page (chart + chart_view) and return its handles."""
        chart = QChart()
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setContextMenuPolicy(Qt.CustomContextMenu)
        # Reuse BaseChart's export-as-PNG menu by pointing the chart_view
        # attribute at whichever page is active when the user right-clicks.
        view.customContextMenuRequested.connect(
            lambda pos, v=view, c=chart: self._show_context_menu(v, c, pos)
        )

        return {'widget': view, 'chart': chart, 'view': view}

    def _show_context_menu(self, view, chart, pos) -> None:
        # BaseChart._on_chart_context_menu reads self.chart / self.chart_view,
        # so swap them in for the duration of the export.
        self.chart = chart
        self.chart_view = view
        self._on_chart_context_menu(pos)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def update_chart(
        self,
        per_activity: Optional[List[Dict[str, Any]]],
        period_type: str = "week",
        hr_max_configured: bool = True,
        any_hr_activities: bool = True,
    ) -> None:
        """Render zones for the given activities.

        Args:
            per_activity: ``[{'date': datetime, 'activity_id': int,
                              'zone_seconds': [int]*5, 'name': str?}, ...]``
                Pass ``None`` or ``[]`` to render an empty-state.
            period_type: ``'week'`` or ``'month'`` for aggregation bucketing.
            hr_max_configured: drives empty-state copy when no HR-Max set.
            any_hr_activities: drives empty-state copy when there are
                activities with HR data but none have cached zones yet
                (lazy-fetch hasn't completed).
        """
        if not hr_max_configured:
            self._show_outer_empty(self.tr(
                "Configure your maximum heart rate in Settings to see zones."
            ))
            return
        if not any_hr_activities:
            self._show_outer_empty(self.tr(
                "No activities with heart-rate data yet."
            ))
            return
        if not per_activity:
            self._show_outer_empty(self.tr(
                "Heart-rate streams haven't been fetched yet for these runs."
            ))
            return

        self._outer_stack.setCurrentIndex(0)

        totals = aggregate_zone_seconds([a['zone_seconds'] for a in per_activity])
        self._render_indicator(totals)
        self._render_aggregated(per_activity, period_type)
        self._render_per_run(per_activity)

    # ------------------------------------------------------------------ #
    # Indicator                                                            #
    # ------------------------------------------------------------------ #

    def _render_indicator(self, totals: List[int]) -> None:
        ratio = polarized_ratio(totals)
        if sum(totals) <= 0:
            self.indicator_label.setText(
                self.tr("80/20: no zone time recorded")
            )
            return
        low = ratio['low'] * 100
        middle = ratio['middle'] * 100
        high = ratio['high'] * 100
        polarized = low >= 75 and high >= 10
        verdict = self.tr("Polarized ✓") if polarized else self.tr("Not polarized")
        self.indicator_label.setText(
            self.tr(
                "80/20: {low:.0f}% low / {mid:.0f}% middle / {high:.0f}% high — {verdict}"
            ).format(low=low, mid=middle, high=high, verdict=verdict)
        )

    # ------------------------------------------------------------------ #
    # Aggregated view                                                      #
    # ------------------------------------------------------------------ #

    def _render_aggregated(
        self, per_activity: List[Dict[str, Any]], period_type: str,
    ) -> None:
        chart = self.aggregated_view['chart']
        chart.removeAllSeries()
        for ax in chart.axes():
            chart.removeAxis(ax)

        buckets: Dict[str, List[List[int]]] = {}
        ordered_keys: List[str] = []
        for a in per_activity:
            key = self._period_key(a['date'], period_type)
            if key not in buckets:
                buckets[key] = []
                ordered_keys.append(key)
            buckets[key].append(a['zone_seconds'])
        ordered_keys.sort()

        bucket_totals = [aggregate_zone_seconds(buckets[k]) for k in ordered_keys]
        self._populate_stacked_chart(
            chart, ordered_keys, bucket_totals,
            x_title=self.tr("Period"),
        )

    @staticmethod
    def _period_key(dt: datetime, period_type: str) -> str:
        if period_type == "month":
            return dt.strftime("%Y-%m")
        iso_year, iso_week, _ = dt.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"

    # ------------------------------------------------------------------ #
    # Per-run view                                                         #
    # ------------------------------------------------------------------ #

    def _render_per_run(self, per_activity: List[Dict[str, Any]]) -> None:
        chart = self.per_run_view['chart']
        chart.removeAllSeries()
        for ax in chart.axes():
            chart.removeAxis(ax)

        sorted_acts = sorted(per_activity, key=lambda a: a['date'])
        recent = sorted_acts[-_PER_RUN_LIMIT:]

        labels = [a['date'].strftime("%Y-%m-%d") for a in recent]
        # Ensure unique x-axis labels (multi-run days get a (#) suffix).
        seen: Dict[str, int] = {}
        unique_labels: List[str] = []
        for lbl in labels:
            n = seen.get(lbl, 0)
            seen[lbl] = n + 1
            unique_labels.append(lbl if n == 0 else f"{lbl} ({n + 1})")

        per_run_zones = [a['zone_seconds'] for a in recent]
        self._populate_stacked_chart(
            chart, unique_labels, per_run_zones,
            x_title=self.tr("Run"),
        )

    # ------------------------------------------------------------------ #
    # Stacked-bar helper                                                   #
    # ------------------------------------------------------------------ #

    def _populate_stacked_chart(
        self,
        chart: QChart,
        categories: List[str],
        per_category_zones: List[List[int]],
        x_title: str,
    ) -> None:
        if not categories or not per_category_zones:
            return

        series = QStackedBarSeries()
        for zone_idx in range(NUM_ZONES):
            bar_set = QBarSet(ZONE_LABELS[zone_idx])
            bar_set.setColor(QColor(_ZONE_COLORS[zone_idx]))
            for zones in per_category_zones:
                # Show minutes; seconds make the y-axis numbers feel huge.
                bar_set.append(zones[zone_idx] / 60.0 if zone_idx < len(zones) else 0)
            series.append(bar_set)
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setTitleText(x_title)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        max_total = max(
            (sum(z) for z in per_category_zones if len(z) == NUM_ZONES), default=0
        ) / 60.0
        axis_y = QValueAxis()
        axis_y.setTitleText(self.tr("Minutes"))
        axis_y.setLabelFormat("%d")
        axis_y.setRange(0, max_total * 1.1 if max_total > 0 else 1)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

    # ------------------------------------------------------------------ #
    # Empty-state                                                          #
    # ------------------------------------------------------------------ #

    def _show_outer_empty(self, message: str) -> None:
        self._empty_label.setText(message)
        self._outer_stack.setCurrentIndex(1)

    # ------------------------------------------------------------------ #
    # BaseChart compatibility                                              #
    # ------------------------------------------------------------------ #

    def show_empty_state(self, message: str, show_connect_button: bool = False) -> None:
        """Override BaseChart's empty-state path to use our own outer stack.

        The parent implementation reads ``self._chart_stack`` from
        ``_wrap_chart_view_with_empty_state``; this widget builds its own
        layout, so we route the message through ``_outer_stack`` instead.
        ``show_connect_button`` is currently ignored — the indicator
        already steers the user to Settings when HR-Max is missing.
        """
        self._show_outer_empty(message)
