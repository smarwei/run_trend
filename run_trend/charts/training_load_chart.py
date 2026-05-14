"""
Training Load (ACWR) chart — daily Gabbett 7:28 ratio with safe zones.

T40 reworked this chart from weekly aggregates (one point per week, 0-100
"score" axis) to a daily-rolling ratio (one point per day, 0-2 ACWR
axis). The zone bands now match the Gabbett thresholds directly: safe
0.8-1.3, caution 1.3-1.5, danger ≥ 1.5.
"""
from datetime import date as _date_type
from typing import Mapping

from PySide6.QtCharts import QChart, QLineSeries, QAreaSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor, QBrush

from .base_chart import BaseChart
from ..analytics.training_load import daily_acwr_series


class TrainingLoadChart(BaseChart):
    """Chart displaying daily Gabbett ACWR over time with zone backgrounds."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self._setup_chart_view(
            self.tr("Training Load (ACWR)"),
            help_tooltip=self.tr(
                "ACWR — Acute:Chronic Workload Ratio (Gabbett 2016).\n\n"
                "Formula: load of last 7 days ÷ average daily load over the "
                "last 28 days (both expressed in weekly units). Computed "
                "daily — the line updates every day rather than jumping at "
                "week boundaries.\n\n"
                "Load source: Banister TRIMP when Resting HR, Gender, and "
                "either Max HR or Date of Birth are configured; otherwise "
                "daily kilometres (a coarser load proxy that ignores "
                "intensity).\n\n"
                "Sweet-spot: 0.8–1.3 (sustainable progression).\n"
                "Caution:    1.3–1.5 (monitor recovery).\n"
                "Danger:     ≥1.5    (elevated injury risk).\n\n"
                "Cold-start: the line only appears after 28 days of "
                "history; before that the chronic window isn't full.\n\n"
                "Caveat: Gabbett's Sweet-Spot bands (2016) are empirically "
                "widespread but scientifically contested — Impellizzeri et "
                "al. 2020 documented mathematical artefacts at small chronic "
                "values and weak injury correlations in follow-up studies. "
                "Treat ACWR as an indicator, not a diagnosis."
            ),
        )
        # QAreaSeries + SeriesAnimations races on series-replace and crashes
        # in AreaBoundItem::updateGeometry — see tickets/22-*.md.
        self.chart.setAnimationOptions(QChart.NoAnimation)

    def update_chart(
        self,
        daily_loads: Mapping[_date_type, float],
        smoothing: str = 'off',
        *,
        variant: str = 'trimp',
    ):
        self._clear_chart()
        if not daily_loads:
            self.chart.setTitle(self.tr("Training Load (Need activities)"))
            return

        series_records = daily_acwr_series(daily_loads)
        plotted = [rec for rec in series_records if rec['has_acwr']]
        if not plotted:
            self.chart.setTitle(self.tr("Training Load (Need 28 days)"))
            return

        # Smoothing applies after we drop cold-start days — a window
        # spanning the cold-start boundary would smear in zero-loads and
        # under-state today's ratio. Smoother is the same SMA used by the
        # other charts, but indices here are days, not periods, so the
        # 'light' / 'medium' / 'strong' windows give a finer effect.
        smoothed_values = self._smooth_data(
            [rec['acwr'] for rec in plotted], smoothing,
        )

        # Variant tag in the title so users see which load proxy is in play.
        variant_label = self.tr("TRIMP") if variant == 'trimp' else self.tr("Distance")
        self.chart.setTitle(self.tr("Training Load (ACWR) — {}").format(variant_label))

        from datetime import datetime as _dt
        plotted_dts = [_dt(rec['date'].year, rec['date'].month, rec['date'].day)
                       for rec in plotted]

        axis_x = self._create_datetime_axis(plotted_dts, self.tr("Date"))
        axis_y = self._create_value_axis(
            self.tr("ACWR"), fmt="%.2f", min_val=0.0, max_val=2.0,
        )
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)

        # Zone backgrounds — instance vars required to prevent GC (PYSIDE-1285).
        def _zone(lo, hi, color_rgba, translated_name):
            lower = QLineSeries()
            upper = QLineSeries()
            for dt in [plotted_dts[0], plotted_dts[-1]]:
                ts = int(dt.timestamp() * 1000)
                lower.append(ts, lo)
                upper.append(ts, hi)
            area = QAreaSeries(upper, lower)
            area.setName(translated_name)
            area.setBrush(QBrush(QColor(*color_rgba)))
            area.setPen(QPen(Qt.NoPen))
            self.chart.addSeries(area)
            area.attachAxis(axis_x)
            area.attachAxis(axis_y)
            return lower, upper, area

        self._safe_lower, self._safe_upper, self._safe_area = _zone(
            0.8, 1.3, (39, 174, 96, 30), self.tr("Safe Zone (0.8-1.3)")
        )
        self._caution_lower, self._caution_upper, self._caution_area = _zone(
            1.3, 1.5, (243, 156, 18, 30), self.tr("Caution Zone (1.3-1.5)")
        )
        self._danger_lower, self._danger_upper, self._danger_area = _zone(
            1.5, 2.0, (231, 76, 60, 30), self.tr("Danger Zone (>1.5)")
        )

        # ACWR line (smoothed if requested by the toolbar combo).
        acwr_series = QLineSeries()
        acwr_series.setName(self.tr("ACWR"))
        for i, value in enumerate(smoothed_values):
            acwr_series.append(int(plotted_dts[i].timestamp() * 1000), value)
        pen = QPen(QColor("#2c3e50"))
        pen.setWidth(2)
        acwr_series.setPen(pen)
        self.chart.addSeries(acwr_series)
        acwr_series.attachAxis(axis_x)
        acwr_series.attachAxis(axis_y)

        self._add_race_markers(axis_x, axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()
