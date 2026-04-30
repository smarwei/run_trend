"""
Duration analysis chart widget.
"""
from PySide6.QtCharts import QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor
from typing import List, Dict, Any

from .base_chart import BaseChart


class DurationChart(BaseChart):
    """Chart displaying training duration metrics."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self._setup_chart_view(self.tr("Training Duration Analysis"))

    def update_chart(self, aggregates: List[Dict[str, Any]], smoothing: str = 'off'):
        self._clear_chart()
        if not aggregates:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        if not complete_aggregates:
            return

        period_dates = [agg['period_date'] for agg in complete_aggregates]

        total_time_h      = self._smooth_data([agg.get('total_moving_time_h', 0.0)         for agg in complete_aggregates], smoothing)
        longest_h         = self._smooth_data([agg.get('longest_duration_h', 0.0)          for agg in complete_aggregates], smoothing)
        avg_duration_min  = self._smooth_data([agg.get('avg_duration_per_run_min', 0.0)    for agg in complete_aggregates], smoothing)
        avg_long_run_min  = self._smooth_data([agg.get('avg_long_run_duration_min', 0.0)   for agg in complete_aggregates], smoothing)

        def _make_series(name, color, data, style=Qt.SolidLine):
            s = QLineSeries()
            s.setName(name)
            pen = QPen(QColor(color))
            pen.setWidth(2)
            pen.setStyle(style)
            s.setPen(pen)
            for i, v in enumerate(data):
                if v is not None and v >= 0:
                    s.append(int(period_dates[i].timestamp() * 1000), v)
            return s

        total_time_series    = _make_series(self.tr("Total Training Time"),    "#9b59b6", total_time_h,     Qt.DashLine)
        longest_series       = _make_series(self.tr("Longest Duration"),       "#e74c3c", longest_h,        Qt.DotLine)
        avg_duration_series  = _make_series(self.tr("Avg Duration per Run"),   "#3498db", avg_duration_min)
        avg_long_run_series  = _make_series(self.tr("Avg Long Run Duration"),  "#f39c12", avg_long_run_min)

        hour_series   = [total_time_series, longest_series]
        minute_series = [avg_duration_series, avg_long_run_series]

        for s in hour_series + minute_series:
            if s.count() > 0:
                self.chart.addSeries(s)

        if not self.chart.series():
            return

        all_hours   = [v for v in total_time_h + longest_h         if v is not None and v >= 0]
        all_minutes = [v for v in avg_duration_min + avg_long_run_min if v is not None and v >= 0]

        axis_x       = self._create_datetime_axis(period_dates, self.tr("Date"))
        axis_y_hours = self._create_value_axis(
            self.tr("Duration (hours)"), min_val=0,
            max_val=(max(all_hours) * 1.1) if all_hours else 10,
        )
        axis_y_min   = self._create_value_axis(
            self.tr("Duration (minutes)"), fmt="%.0f", min_val=0,
            max_val=(max(all_minutes) * 1.1) if all_minutes else 60,
        )

        self.chart.addAxis(axis_x,       Qt.AlignBottom)
        self.chart.addAxis(axis_y_hours, Qt.AlignLeft)
        self.chart.addAxis(axis_y_min,   Qt.AlignRight)

        for s in self.chart.series():
            s.attachAxis(axis_x)
            if s in hour_series:
                s.attachAxis(axis_y_hours)
            else:
                s.attachAxis(axis_y_min)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()
