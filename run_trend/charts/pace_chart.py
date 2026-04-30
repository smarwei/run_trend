"""
Pace/Speed progress chart widget.
"""
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QCheckBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from typing import List, Dict, Any
import math

from .base_chart import BaseChart


class PaceChart(BaseChart):
    """Chart displaying pace or speed progress over time."""

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
        layout.addLayout(toggle_layout)

        self.chart = QChart()
        self.chart.setTitle(self.tr("Pace/Speed Progress"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

    def update_chart(
        self,
        aggregates: List[Dict[str, Any]],
        smoothing: str = 'off',
        metric: str = 'pace',
    ):
        self._last_aggregates = aggregates
        self._last_smoothing  = smoothing
        self._last_metric     = metric

        self._clear_chart()
        if not aggregates:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        if not complete_aggregates:
            return

        period_dates = [agg['period_date'] for agg in complete_aggregates]

        if metric == 'pace':
            data        = [agg['weighted_avg_pace_min_per_km'] for agg in complete_aggregates]
            title       = self.tr("Pace Progress")
            y_label     = self.tr("Pace (min/km)")
            series_name = self.tr("Pace")
            roc_key     = 'weighted_avg_pace_min_per_km'
            roc_label   = self.tr("Pace RoC (min/km per week)")
        else:
            data        = [agg['avg_speed_kmh'] for agg in complete_aggregates]
            title       = self.tr("Speed Progress")
            y_label     = self.tr("Speed (km/h)")
            series_name = self.tr("Speed")
            roc_key     = 'avg_speed_kmh'
            roc_label   = self.tr("Speed RoC (km/h per week)")

        self.chart.setTitle(title)
        data = self._smooth_data(data, smoothing)

        series = QLineSeries()
        series.setName(series_name)
        pen = QPen(QColor("#3498db"))
        pen.setWidth(2)
        series.setPen(pen)
        for i, v in enumerate(data):
            series.append(int(period_dates[i].timestamp() * 1000), v)
        self.chart.addSeries(series)

        axis_x = self._create_datetime_axis(period_dates, self.tr("Date"))
        valid = [d for d in data if d > 0]
        if metric == 'pace' and valid:
            lo, hi = min(valid), max(valid)
            margin = max((hi - lo) * 0.1, 0.05)
            axis_y = self._create_pace_axis(
                y_label, max(0.0, lo - margin), hi + margin,
            )
        else:
            axis_y = QValueAxis()
            axis_y.setTitleText(y_label)
            axis_y.setLabelFormat("%.2f")
            if valid:
                lo, hi = min(valid), max(valid)
                margin = (hi - lo) * 0.1
                axis_y.setRange(max(0, lo - margin), hi + margin)

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        if self.roc_checkbox.isChecked():
            roc_data = self._calculate_rate_of_change(complete_aggregates, roc_key)
            roc_series = QLineSeries()
            roc_series.setName(roc_label)
            pen = QPen(QColor("#9b59b6"))
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            roc_series.setPen(pen)
            for i, v in enumerate(roc_data):
                if not math.isnan(v):
                    roc_series.append(int(period_dates[i].timestamp() * 1000), v)

            if roc_series.count() > 0:
                self.chart.addSeries(roc_series)
                valid_roc = [v for v in roc_data if not math.isnan(v)]
                lo_r, hi_r = min(valid_roc), max(valid_roc)
                margin = (hi_r - lo_r) * 0.2 if hi_r != lo_r else 0.1
                axis_y_roc = self._create_value_axis(
                    roc_label, fmt="%.3f",
                    min_val=lo_r - margin, max_val=hi_r + margin,
                )
                self.chart.addAxis(axis_y_roc, Qt.AlignRight)
                roc_series.attachAxis(axis_x)
                roc_series.attachAxis(axis_y_roc)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()

    def _on_roc_toggle(self):
        if hasattr(self, '_last_aggregates'):
            self.update_chart(self._last_aggregates, self._last_smoothing, self._last_metric)
