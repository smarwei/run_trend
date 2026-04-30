"""
Training frequency chart widget.
"""
from PySide6.QtCharts import QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor
from typing import List, Dict, Any

from .base_chart import BaseChart


class FrequencyChart(BaseChart):
    """Chart displaying training frequency over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self._setup_chart_view(self.tr("Training Frequency"))

    def update_chart(self, aggregates: List[Dict[str, Any]], smoothing: str = 'off'):
        self._clear_chart()
        if not aggregates:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        if not complete_aggregates:
            return

        period_dates = [agg['period_date'] for agg in complete_aggregates]
        num_runs = self._smooth_data(
            [agg['num_runs'] for agg in complete_aggregates], smoothing
        )

        series = QLineSeries()
        series.setName(self.tr("Runs per Period"))
        pen = QPen(QColor("#9b59b6"))
        pen.setWidth(2)
        series.setPen(pen)
        for i, value in enumerate(num_runs):
            series.append(int(period_dates[i].timestamp() * 1000), value)
        self.chart.addSeries(series)

        axis_x = self._create_datetime_axis(period_dates, self.tr("Date"))
        axis_y = self._create_value_axis(
            self.tr("Number of Runs"), fmt="%d",
            min_val=0, max_val=(max(num_runs) if num_runs else 10) * 1.2,
        )

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        for s in self.chart.series():
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()
