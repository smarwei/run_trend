"""
Distance progress chart widget.
"""
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from typing import List, Dict, Any, Optional

from .base_chart import BaseChart


class DistanceChart(BaseChart):
    """Chart displaying distance progress over time."""

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
        self.chart.setTitle(self.tr("Distance Progress"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self._wrap_chart_view_with_empty_state(self.chart_view))

    def update_chart(
        self,
        aggregates: List[Dict[str, Any]],
        smoothing: str = 'off',
        prev_year_aggregates: Optional[List[Dict[str, Any]]] = None,
    ):
        self._last_aggregates = aggregates
        self._last_smoothing  = smoothing
        self._last_prev_year  = prev_year_aggregates

        self._clear_chart()
        if not aggregates:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        if not complete_aggregates:
            return

        period_dates  = [agg['period_date']          for agg in complete_aggregates]
        distances     = self._smooth_data([agg['total_distance_km']    for agg in complete_aggregates], smoothing)
        moving_times  = self._smooth_data([agg['total_moving_time_h']  for agg in complete_aggregates], smoothing)
        run_counts    = self._smooth_data([agg['num_runs']             for agg in complete_aggregates], smoothing)

        axis_x = self._create_datetime_axis(period_dates, self.tr("Date"))
        self.chart.addAxis(axis_x, Qt.AlignBottom)

        axis_y_dist = self._create_value_axis(
            self.tr("Distance (km)"),
            min_val=0, max_val=(max(distances) if distances else 10) * 1.1,
        )
        self.chart.addAxis(axis_y_dist, Qt.AlignLeft)

        axis_y_time = self._create_value_axis(
            self.tr("Moving Time (h)"),
            min_val=0, max_val=(max(moving_times) if moving_times else 10) * 1.1,
        )
        self.chart.addAxis(axis_y_time, Qt.AlignRight)

        def _add(name, color, data, axis_y, style=Qt.SolidLine, visible=True):
            s = QLineSeries()
            s.setName(name)
            pen = QPen(QColor(color))
            pen.setWidth(2)
            pen.setStyle(style)
            s.setPen(pen)
            for i, v in enumerate(data):
                s.append(int(period_dates[i].timestamp() * 1000), v)
            s.setVisible(visible)
            self.chart.addSeries(s)
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)

        _add(self.tr("Total Distance"), "#3498db", distances,    axis_y_dist)
        _add(self.tr("Moving Time"),    "#9b59b6", moving_times, axis_y_time,  Qt.DashDotLine, visible=False)
        _add(self.tr("Run Count"),      "#27ae60", run_counts,   axis_y_dist,  Qt.DotLine,     visible=False)

        prev_complete = self._filter_complete_aggregates(prev_year_aggregates or [])
        self._add_previous_year_series(
            axis_x, axis_y_dist,
            self.tr("Total Distance"),
            prev_complete, 'total_distance_km', smoothing,
        )

        self._add_race_markers(axis_x, axis_y_dist)

        if self.roc_checkbox.isChecked():
            roc_built = self._build_roc_series(
                complete_aggregates, 'total_distance_km', period_dates,
                label=self.tr("Distance RoC (km/week)"),
            )
            if roc_built is not None:
                roc_series, valid_roc = roc_built
                self.chart.addSeries(roc_series)
                axis_y_roc = self._create_roc_axis(
                    valid_roc, self.tr("Rate of Change (km/week)"), fmt="%.2f",
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
                prev_year_aggregates=getattr(self, '_last_prev_year', None),
            )
