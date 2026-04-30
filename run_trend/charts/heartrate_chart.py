"""
Heart rate analysis chart widget with efficiency factor.
"""
import logging
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QCheckBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any
import math

from .base_chart import BaseChart
from ..ui.help_label import make_help_icon

logger = logging.getLogger(__name__)


class HeartRateChart(BaseChart):
    """Chart displaying heart rate metrics and efficiency factor."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        toggle_layout = QHBoxLayout()
        self.roc_checkbox = QCheckBox(self.tr("Show Rate of Change"))
        self.roc_checkbox.setChecked(False)
        self.roc_checkbox.stateChanged.connect(self._on_roc_toggle)
        toggle_layout.addWidget(self.roc_checkbox)
        toggle_layout.addStretch()
        toggle_layout.addWidget(make_help_icon(self.tr(
            "Heart-rate metrics:\n\n"
            "• Average HR — mean heart rate across runs in this period.\n"
            "• HR Range — min/max average HR per run, shown as a band.\n"
            "• Efficiency Factor (EF) = pace (m/s) ÷ HR (bpm) × 1000.\n"
            "  Higher EF = same pace at lower HR = better aerobic fitness.\n\n"
            "Needs HR-sensor data; otherwise the chart stays empty."
        )))
        layout.addLayout(toggle_layout)

        self.chart = QChart()
        self.chart.setTitle(self.tr("Heart Rate Analysis"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self._wrap_chart_view_with_empty_state(self.chart_view))

    def update_chart(self, aggregates: List[Dict[str, Any]], smoothing: str = 'off'):
        self._last_aggregates = aggregates
        self._last_smoothing  = smoothing

        self._clear_chart()
        if not aggregates:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        hr_aggregates = [agg for agg in complete_aggregates if agg.get('num_hr_activities', 0) > 0]

        if not hr_aggregates:
            self.chart.setTitle(self.tr("Heart Rate Analysis (No HR data available)"))
            return

        period_dates = [agg['period_date'] for agg in hr_aggregates]

        avg_hr_data = self._smooth_data([agg['avg_heartrate']           for agg in hr_aggregates], smoothing)
        min_hr_data = self._smooth_data([agg['min_avg_heartrate']       for agg in hr_aggregates], smoothing)
        max_hr_data = self._smooth_data([agg['max_heartrate']           for agg in hr_aggregates], smoothing)
        ef_data     = self._smooth_data([agg['efficiency_factor'] * 1000 for agg in hr_aggregates], smoothing)

        # Area series (HR range) — instance vars required to prevent GC (PYSIDE-1285)
        valid_area_points = [
            (int(period_dates[i].timestamp() * 1000), min_hr_data[i], max_hr_data[i])
            for i in range(len(hr_aggregates))
            if (min_hr_data[i] is not None and min_hr_data[i] > 0 and
                max_hr_data[i] is not None and max_hr_data[i] > 0)
        ]
        if valid_area_points:
            self._hr_lower_series = QLineSeries()
            self._hr_upper_series = QLineSeries()
            for ts, lo, hi in valid_area_points:
                self._hr_lower_series.append(ts, lo)
                self._hr_upper_series.append(ts, hi)
            self._hr_area = QAreaSeries(self._hr_upper_series, self._hr_lower_series)
            self._hr_area.setName(self.tr("HR Range (Min-Max)"))
            self._hr_area.setBrush(QBrush(QColor(52, 152, 219, 60)))
            self._hr_area.setPen(QPen(QColor(41, 128, 185)))
            self.chart.addSeries(self._hr_area)

        avg_hr_series = QLineSeries()
        avg_hr_series.setName(self.tr("Average HR"))
        for i, v in enumerate(avg_hr_data):
            if v is not None and v > 0:
                avg_hr_series.append(int(period_dates[i].timestamp() * 1000), v)
        if avg_hr_series.count() > 0:
            pen = QPen(QColor("#e74c3c"))
            pen.setWidth(2)
            avg_hr_series.setPen(pen)
            self.chart.addSeries(avg_hr_series)

        ef_series = QLineSeries()
        ef_series.setName(self.tr("Efficiency Factor (×1000)"))
        for i, v in enumerate(ef_data):
            if v is not None and v > 0:
                ef_series.append(int(period_dates[i].timestamp() * 1000), v)
        self._ef_series = ef_series if ef_series.count() > 0 else None
        if self._ef_series:
            pen = QPen(QColor("#2ecc71"))
            pen.setWidth(2)
            ef_series.setPen(pen)
            self.chart.addSeries(ef_series)

        roc_series = None
        if self.roc_checkbox.isChecked():
            roc_data = self._calculate_rate_of_change(hr_aggregates, 'avg_heartrate')
            roc_series = QLineSeries()
            roc_series.setName(self.tr("HR RoC (bpm/week)"))
            pen = QPen(QColor("#9b59b6"))
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            roc_series.setPen(pen)
            for i, v in enumerate(roc_data):
                if not math.isnan(v):
                    roc_series.append(int(period_dates[i].timestamp() * 1000), v)
            if roc_series.count() > 0:
                self.chart.addSeries(roc_series)
            else:
                roc_series = None

        if not self.chart.series():
            return

        # Axes
        axis_x    = self._create_datetime_axis(period_dates, self.tr("Date"))
        all_hr    = [v for v in min_hr_data + avg_hr_data + max_hr_data if v is not None and v > 0]
        hr_margin = (max(all_hr) - min(all_hr)) * 0.1 if len(all_hr) > 1 else 10
        axis_y_hr = self._create_value_axis(
            self.tr("Heart Rate (bpm)"), fmt="%d",
            min_val=max(0, min(all_hr) - hr_margin) if all_hr else 0,
            max_val=(max(all_hr) + hr_margin) if all_hr else 200,
        )

        valid_ef  = [v for v in ef_data if v is not None and v > 0]
        ef_margin = (max(valid_ef) - min(valid_ef)) * 0.1 if len(valid_ef) > 1 else 1
        axis_y_ef = self._create_value_axis(
            self.tr("Efficiency Factor (m/s per bpm ×1000)"), fmt="%.2f",
            min_val=max(0, min(valid_ef) - ef_margin) if valid_ef else 0,
            max_val=(max(valid_ef) + ef_margin) if valid_ef else 10,
        )

        axis_y_roc = None
        if roc_series is not None:
            roc_data   = self._calculate_rate_of_change(hr_aggregates, 'avg_heartrate')
            valid_roc  = [v for v in roc_data if not math.isnan(v)]
            lo_r, hi_r = min(valid_roc), max(valid_roc)
            margin     = (hi_r - lo_r) * 0.2 if hi_r != lo_r else 0.1
            axis_y_roc = self._create_value_axis(
                self.tr("HR Rate of Change (bpm/week)"), fmt="%.2f",
                min_val=lo_r - margin, max_val=hi_r + margin,
            )

        self.chart.addAxis(axis_x,    Qt.AlignBottom)
        self.chart.addAxis(axis_y_hr, Qt.AlignLeft)
        right_axis = axis_y_roc if axis_y_roc is not None else axis_y_ef
        self.chart.addAxis(right_axis, Qt.AlignRight)

        for s in self.chart.series():
            if isinstance(s, QAreaSeries):
                try:
                    s.attachAxis(axis_x)
                    s.attachAxis(axis_y_hr)
                except Exception:
                    logger.exception("Could not attach area series")
                    continue
            else:
                s.attachAxis(axis_x)
                if s is roc_series:
                    s.attachAxis(right_axis)
                elif s is self._ef_series:
                    s.attachAxis(right_axis if axis_y_roc is None else axis_y_hr)
                else:
                    s.attachAxis(axis_y_hr)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()

    def _on_roc_toggle(self):
        if hasattr(self, '_last_aggregates'):
            self.update_chart(self._last_aggregates, self._last_smoothing)
