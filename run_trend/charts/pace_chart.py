"""
Pace/Speed progress chart widget.
"""
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from typing import List, Dict, Any, Optional

from .base_chart import BaseChart


class PaceChart(BaseChart):
    """Chart displaying pace or speed progress over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        toggle_layout = QHBoxLayout()
        self.roc_checkbox = self._make_roc_checkbox()
        toggle_layout.addWidget(self.roc_checkbox)
        toggle_layout.addStretch()
        layout.addLayout(toggle_layout)

        self.chart = QChart()
        self.chart.setTitle(self.tr("Pace/Speed Progress"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self._wrap_chart_view_with_empty_state(self.chart_view))

    def update_chart(
        self,
        aggregates: List[Dict[str, Any]],
        smoothing: str = 'off',
        metric: str = 'pace',
        prev_year_aggregates: Optional[List[Dict[str, Any]]] = None,
    ):
        self._last_aggregates = aggregates
        self._last_smoothing  = smoothing
        self._last_metric     = metric
        self._last_prev_year  = prev_year_aggregates

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

        prev_complete = self._filter_complete_aggregates(prev_year_aggregates or [])
        prev_value_key = (
            'weighted_avg_pace_min_per_km' if metric == 'pace' else 'avg_speed_kmh'
        )
        self._add_previous_year_series(
            axis_x, axis_y, series_name, prev_complete, prev_value_key, smoothing,
        )

        self._add_race_markers(axis_x, axis_y)

        if self.roc_checkbox.isChecked():
            roc_built = self._build_roc_series(
                complete_aggregates, roc_key, period_dates, label=roc_label,
            )
            if roc_built is not None:
                roc_series, valid_roc = roc_built
                self.chart.addSeries(roc_series)
                axis_y_roc = self._create_roc_axis(
                    valid_roc, roc_label, fmt="%.3f",
                )
                self.chart.addAxis(axis_y_roc, Qt.AlignRight)
                roc_series.attachAxis(axis_x)
                roc_series.attachAxis(axis_y_roc)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()

    def _on_roc_toggle(self):
        if hasattr(self, '_last_aggregates'):
            self.update_chart(
                self._last_aggregates,
                self._last_smoothing,
                self._last_metric,
                prev_year_aggregates=getattr(self, '_last_prev_year', None),
            )
