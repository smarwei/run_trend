"""
Training structure overview chart widget.
"""
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCharts import QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor, QPainter
from typing import List, Dict, Any

from .base_chart import BaseChart


class StructureOverviewChart(BaseChart):
    """Chart displaying comparative view of training structure metrics."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        from PySide6.QtCharts import QChart
        from PySide6.QtCharts import QChartView

        layout = QVBoxLayout(self)

        info_label = QLabel(
            self.tr("This chart shows all structure metrics normalized to 0-100% for comparison. "
                    "It helps understand HOW your training load is composed.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        layout.addWidget(info_label)

        from PySide6.QtCharts import QChart, QChartView
        self.chart = QChart()
        self.chart.setTitle(self.tr("Training Structure Overview (Normalized)"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

    def update_chart(self, aggregates: List[Dict[str, Any]], smoothing: str = 'off'):
        self._clear_chart()
        if not aggregates:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        if not complete_aggregates:
            return

        period_dates = [agg['period_date'] for agg in complete_aggregates]

        def normalize(values):
            if not values:
                return values
            lo, hi = min(values), max(values)
            if hi == lo:
                return [50.0] * len(values)
            return [(v - lo) / (hi - lo) * 100 for v in values]

        norm_distances = self._smooth_data(
            normalize([agg['total_distance_km'] for agg in complete_aggregates]), smoothing
        )
        norm_runs = self._smooth_data(
            normalize([agg['num_runs'] for agg in complete_aggregates]), smoothing
        )
        norm_avg = self._smooth_data(
            normalize([agg['avg_distance_per_run_km'] for agg in complete_aggregates]), smoothing
        )
        norm_longest = self._smooth_data(
            normalize([agg['longest_run_km'] for agg in complete_aggregates]), smoothing
        )

        def _make_series(name, color, data):
            s = QLineSeries()
            s.setName(name)
            pen = QPen(QColor(color))
            pen.setWidth(2)
            s.setPen(pen)
            for i, v in enumerate(data):
                s.append(int(period_dates[i].timestamp() * 1000), v)
            self.chart.addSeries(s)

        _make_series(self.tr("Total Distance"),    "#3498db", norm_distances)
        _make_series(self.tr("Number of Runs"),    "#9b59b6", norm_runs)
        _make_series(self.tr("Avg Distance/Run"),  "#27ae60", norm_avg)
        _make_series(self.tr("Longest Run"),       "#e67e22", norm_longest)

        axis_x = self._create_datetime_axis(period_dates, self.tr("Date"))
        axis_y = self._create_value_axis(
            self.tr("Normalized Value (%)"), fmt="%.0f", min_val=0, max_val=100
        )

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        for s in self.chart.series():
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()
