"""
Training Load (ACWR) chart widget with safe zones.
"""
from PySide6.QtCharts import QLineSeries, QAreaSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor, QBrush
from typing import List, Dict, Any

from .base_chart import BaseChart


class TrainingLoadChart(BaseChart):
    """Chart displaying Training Load (ACWR) over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self._setup_chart_view(self.tr("Training Load (ACWR)"))

    def update_chart(self, aggregates: List[Dict[str, Any]]):
        self._clear_chart()
        if not aggregates:
            return

        # Custom filter: only periods that have training_load data
        load_aggregates = [
            agg for agg in aggregates
            if agg.get('training_load', {}).get('has_load', False)
        ]

        if len(load_aggregates) < 2:
            self.chart.setTitle(self.tr("Training Load (Need 5+ weeks)"))
            return

        period_dates = [agg['period_date'] for agg in load_aggregates]
        load_scores  = [agg['training_load']['training_load'] for agg in load_aggregates]

        axis_x = self._create_datetime_axis(period_dates, self.tr("Date"))
        axis_y = self._create_value_axis(
            self.tr("Training Load Score"), fmt="%d", min_val=0, max_val=100
        )
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)

        # Zone backgrounds — instance vars required to prevent GC (PYSIDE-1285)
        def _zone(lo, hi, color_rgba, name):
            lower = QLineSeries()
            upper = QLineSeries()
            for date in [period_dates[0], period_dates[-1]]:
                ts = int(date.timestamp() * 1000)
                lower.append(ts, lo)
                upper.append(ts, hi)
            area = QAreaSeries(upper, lower)
            area.setName(self.tr(name))
            area.setBrush(QBrush(QColor(*color_rgba)))
            area.setPen(QPen(Qt.NoPen))
            self.chart.addSeries(area)
            area.attachAxis(axis_x)
            area.attachAxis(axis_y)
            return lower, upper, area

        self._safe_lower,    self._safe_upper,    self._safe_area    = _zone(40, 65,  (39, 174,  96, 30), "Safe Zone (40-65)")
        self._caution_lower, self._caution_upper, self._caution_area = _zone(65, 80,  (243, 156, 18, 30), "Caution Zone (65-80)")
        self._danger_lower,  self._danger_upper,  self._danger_area  = _zone(80, 100, (231,  76, 60, 30), "Danger Zone (80+)")

        # Load line
        load_series = QLineSeries()
        load_series.setName(self.tr("Training Load"))
        for i, score in enumerate(load_scores):
            load_series.append(int(period_dates[i].timestamp() * 1000), score)
        pen = QPen(QColor("#2c3e50"))
        pen.setWidth(3)
        load_series.setPen(pen)
        self.chart.addSeries(load_series)
        load_series.attachAxis(axis_x)
        load_series.attachAxis(axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()
