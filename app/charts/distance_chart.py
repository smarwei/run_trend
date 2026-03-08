"""
Distance progress chart widget.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any

from ..analytics.smoothing import Smoother


class DistanceChart(QWidget):
    """Chart displaying distance progress over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle("Distance Progress")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(self.chart_view)

    def update_chart(self, aggregates: List[Dict[str, Any]], smoothing: str = 'off'):
        """
        Update chart with new data.

        Args:
            aggregates: List of period aggregates
            smoothing: Smoothing level ('off', 'light', 'medium', 'strong')
        """
        # Remove all series and axes
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if not aggregates:
            return

        # Extract data
        distances = [agg['total_distance_km'] for agg in aggregates]
        moving_times = [agg['total_moving_time_h'] for agg in aggregates]
        run_counts = [agg['num_runs'] for agg in aggregates]
        period_dates = [agg['period_date'] for agg in aggregates]

        # Create primary X axis (DateTime)
        axis_x = QDateTimeAxis()
        axis_x.setTitleText("Date")
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)
        self.chart.addAxis(axis_x, Qt.AlignBottom)

        # Primary Y axis for distance
        axis_y_distance = QValueAxis()
        axis_y_distance.setTitleText("Distance (km)")
        axis_y_distance.setLabelFormat("%.1f")
        max_distance = max(distances) if distances else 10
        axis_y_distance.setRange(0, max_distance * 1.1)
        self.chart.addAxis(axis_y_distance, Qt.AlignLeft)

        # Distance series
        raw_series = QLineSeries()
        raw_series.setName("Distance")
        for i, value in enumerate(distances):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            raw_series.append(timestamp_ms, value)
        pen = QPen(QColor("#3498db"))
        pen.setWidth(2)
        raw_series.setPen(pen)
        self.chart.addSeries(raw_series)
        raw_series.attachAxis(axis_x)
        raw_series.attachAxis(axis_y_distance)

        # Smoothed distance series if enabled
        if smoothing != 'off':
            smoothed_distances = Smoother.smooth_series(distances, 'sma', smoothing)
            smoothed_series = QLineSeries()
            smoothed_series.setName("Smoothed Distance")
            for i, value in enumerate(smoothed_distances):
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                smoothed_series.append(timestamp_ms, value)
            smooth_pen = QPen(QColor("#e74c3c"))
            smooth_pen.setWidth(3)
            smoothed_series.setPen(smooth_pen)
            self.chart.addSeries(smoothed_series)
            smoothed_series.attachAxis(axis_x)
            smoothed_series.attachAxis(axis_y_distance)

        # Secondary Y axis for time
        axis_y_time = QValueAxis()
        axis_y_time.setTitleText("Moving Time (h)")
        axis_y_time.setLabelFormat("%.1f")
        max_time = max(moving_times) if moving_times else 10
        axis_y_time.setRange(0, max_time * 1.1)
        self.chart.addAxis(axis_y_time, Qt.AlignRight)

        # Moving time series (initially hidden)
        time_series = QLineSeries()
        time_series.setName("Moving Time")
        for i, value in enumerate(moving_times):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            time_series.append(timestamp_ms, value)
        time_pen = QPen(QColor("#9b59b6"))
        time_pen.setWidth(2)
        time_pen.setStyle(Qt.DashDotLine)
        time_series.setPen(time_pen)
        self.chart.addSeries(time_series)
        time_series.attachAxis(axis_x)
        time_series.attachAxis(axis_y_time)
        time_series.setVisible(False)  # Initially hidden

        # Run count series (initially hidden, uses distance axis for simplicity)
        count_series = QLineSeries()
        count_series.setName("Run Count")
        for i, value in enumerate(run_counts):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            count_series.append(timestamp_ms, value)
        count_pen = QPen(QColor("#27ae60"))
        count_pen.setWidth(2)
        count_pen.setStyle(Qt.DotLine)
        count_series.setPen(count_pen)
        self.chart.addSeries(count_series)
        count_series.attachAxis(axis_x)
        count_series.attachAxis(axis_y_distance)  # Use distance axis
        count_series.setVisible(False)  # Initially hidden

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
