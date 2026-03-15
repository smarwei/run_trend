"""
Pace/Speed progress chart widget.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any

from ..analytics.smoothing import Smoother


class PaceChart(QWidget):
    """Chart displaying pace or speed progress over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle("Pace/Speed Progress")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(self.chart_view)

    def update_chart(
        self,
        aggregates: List[Dict[str, Any]],
        smoothing: str = 'off',
        metric: str = 'pace'
    ):
        """
        Update chart with new data.

        Args:
            aggregates: List of period aggregates
            smoothing: Smoothing level ('off', 'light', 'medium', 'strong')
            metric: 'pace' or 'speed'
        """
        # Remove all series and axes
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if not aggregates:
            return

        # Extract period dates
        period_dates = [agg['period_date'] for agg in aggregates]

        # Extract data based on metric
        if metric == 'pace':
            data = [agg['weighted_avg_pace_min_per_km'] for agg in aggregates]
            title = "Pace Progress"
            y_label = "Pace (min/km)"
            series_name = "Pace"
        else:  # speed
            data = [agg['avg_speed_kmh'] for agg in aggregates]
            title = "Speed Progress"
            y_label = "Speed (km/h)"
            series_name = "Speed"

        self.chart.setTitle(title)

        # Apply smoothing if enabled
        if smoothing != 'off':
            data = Smoother.smooth_series(data, 'sma', smoothing)

        # Create series (smoothing already applied if enabled)
        series = QLineSeries()
        series.setName(series_name)

        for i, value in enumerate(data):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            series.append(timestamp_ms, value)

        # Set pen
        pen = QPen(QColor("#3498db"))
        pen.setWidth(2)
        series.setPen(pen)

        self.chart.addSeries(series)

        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setTitleText("Date")
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)

        axis_y = QValueAxis()
        axis_y.setTitleText(y_label)
        axis_y.setLabelFormat("%.2f")

        if data:
            valid_data = [d for d in data if d > 0]
            if valid_data:
                min_val = min(valid_data)
                max_val = max(valid_data)
                margin = (max_val - min_val) * 0.1
                axis_y.setRange(max(0, min_val - margin), max_val + margin)

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)

        for series in self.chart.series():
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        # Connect legend markers for interactive toggling
        self._connect_legend_markers()

    def _connect_legend_markers(self):
        """Connect legend markers to enable interactive series toggling."""
        for marker in self.chart.legend().markers():
            marker.clicked.connect(self._on_legend_marker_clicked)

    def _on_legend_marker_clicked(self):
        """Handle legend marker clicks to toggle series visibility."""
        marker = self.sender()
        if marker:
            series = marker.series()
            # Toggle series visibility
            series.setVisible(not series.isVisible())
            # Keep marker visible in legend
            marker.setVisible(True)
            # Update marker label color to reflect state
            if series.isVisible():
                marker.setLabelBrush(QBrush(QColor("black")))
            else:
                marker.setLabelBrush(QBrush(QColor("gray")))
