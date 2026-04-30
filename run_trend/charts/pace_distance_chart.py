"""
Scatter chart: pace (min/km) vs. distance (km) for individual runs.
"""
from PySide6.QtCharts import QScatterSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from typing import List, Dict, Any

from .base_chart import BaseChart


class PaceDistanceChart(BaseChart):
    """Scatter plot of pace vs. distance for individual runs."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self._setup_chart_view(self.tr("Pace vs. Distance"))

    def update_chart(self, activities: List[Dict[str, Any]]):
        self._clear_chart()
        if not activities:
            return

        series = QScatterSeries()
        series.setName(self.tr("Runs"))
        series.setMarkerSize(8)
        series.setColor(QColor("#3498db"))
        series.setBorderColor(QColor("#2980b9"))

        distances = []
        paces = []

        for act in activities:
            dist_m = act.get("distance", 0) or 0
            moving_time = act.get("moving_time", 0) or 0
            if dist_m <= 0 or moving_time <= 0:
                continue

            dist_km = dist_m / 1000.0
            pace_min_per_km = (moving_time / dist_m) * 1000.0 / 60.0

            series.append(dist_km, pace_min_per_km)
            distances.append(dist_km)
            paces.append(pace_min_per_km)

        if not distances:
            return

        self.chart.addSeries(series)

        axis_x = self._create_value_axis(
            self.tr("Distance (km)"),
            min_val=0, max_val=max(distances) * 1.1,
        )

        margin = max((max(paces) - min(paces)) * 0.1, 0.5)
        axis_y = self._create_pace_axis(
            self.tr("Pace (min/km)"),
            min_val=min(paces) - margin,
            max_val=max(paces) + margin,
            reverse=True,  # Faster pace (lower value) appears at top
        )

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
