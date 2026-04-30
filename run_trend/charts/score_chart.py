"""
Training status score chart widget.
"""
from PySide6.QtCharts import QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor
from typing import List, Dict, Any

from .base_chart import BaseChart


class ScoreChart(BaseChart):
    """Chart displaying training status score over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self._setup_chart_view(
            self.tr("Training Status Score"),
            help_tooltip=self.tr(
                "Training Score (0-100): a composite of recent training "
                "consistency, weekly distance, and aerobic efficiency.\n\n"
                "Typical ranges:\n"
                "  • 0-29  red   – minimal training\n"
                "  • 30-59 amber – building up\n"
                "  • 60-79 green – good\n"
                "  • 80+   green – strong\n\n"
                "Source: RunTrend specification §6 Training Score."
            ),
        )

    def update_chart(self, aggregates: List[Dict[str, Any]], smoothing: str = 'off'):
        self._clear_chart()
        if not aggregates:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        if not complete_aggregates:
            return

        period_dates = [agg['period_date'] for agg in complete_aggregates]
        scores = self._smooth_data(
            [agg.get('training_score', 0) for agg in complete_aggregates], smoothing
        )

        series = QLineSeries()
        series.setName(self.tr("Training Score"))
        pen = QPen(QColor("#16a085"))
        pen.setWidth(2)
        series.setPen(pen)
        for i, value in enumerate(scores):
            series.append(int(period_dates[i].timestamp() * 1000), value)
        self.chart.addSeries(series)

        axis_x = self._create_datetime_axis(period_dates, self.tr("Date"))
        axis_y = self._create_value_axis(self.tr("Score (0-100)"), min_val=0, max_val=100)

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        for s in self.chart.series():
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)

        self._add_race_markers(axis_x, axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()
