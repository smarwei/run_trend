"""
Endurance chart combining longest run and average distance per run.
"""
from PySide6.QtCharts import QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor
from typing import List, Dict, Any

from .base_chart import BaseChart


class EnduranceChart(BaseChart):
    """Chart displaying longest run and average distance per run over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self._setup_chart_view(self.tr("Endurance"))

    def update_chart(self, aggregates: List[Dict[str, Any]], smoothing: str = 'off'):
        self._clear_chart()
        if not aggregates:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        if not complete_aggregates:
            return

        period_dates = [agg['period_date'] for agg in complete_aggregates]
        longest_runs = self._smooth_data(
            [agg['longest_run_km'] for agg in complete_aggregates], smoothing
        )
        avg_distances = self._smooth_data(
            [agg['avg_distance_per_run_km'] for agg in complete_aggregates], smoothing
        )

        longest_series = QLineSeries()
        longest_series.setName(self.tr("Longest Run"))
        pen = QPen(QColor("#e67e22"))
        pen.setWidth(2)
        longest_series.setPen(pen)

        avg_series = QLineSeries()
        avg_series.setName(self.tr("Avg Distance per Run"))
        pen = QPen(QColor("#27ae60"))
        pen.setWidth(2)
        avg_series.setPen(pen)

        for i, date in enumerate(period_dates):
            ts = int(date.timestamp() * 1000)
            longest_series.append(ts, longest_runs[i])
            avg_series.append(ts, avg_distances[i])

        self.chart.addSeries(longest_series)
        self.chart.addSeries(avg_series)

        max_val = max(max(longest_runs), max(avg_distances))
        axis_x = self._create_datetime_axis(period_dates, self.tr("Date"))
        axis_y = self._create_value_axis(
            self.tr("Distance (km)"), min_val=0, max_val=max_val * 1.1
        )

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        for s in self.chart.series():
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()
