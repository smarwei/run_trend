"""
Average distance per run chart widget.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any

from ..analytics.smoothing import Smoother


class AvgDistanceChart(QWidget):
    """Chart displaying average distance per run over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle("Average Distance per Run")
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

        # Extract period dates
        period_dates = [agg['period_date'] for agg in aggregates]

        # Extract average distance per run data
        avg_distances = [agg['avg_distance_per_run_km'] for agg in aggregates]

        # Create raw series
        raw_series = QLineSeries()
        raw_series.setName("Avg Distance per Run")

        for i, agg in enumerate(aggregates):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            raw_series.append(timestamp_ms, agg['avg_distance_per_run_km'])

        # Set pen for raw series
        pen = QPen(QColor("#27ae60"))
        pen.setWidth(2)
        raw_series.setPen(pen)

        self.chart.addSeries(raw_series)

        # Add smoothed series if enabled
        if smoothing != 'off':
            smoothed_distances = Smoother.smooth_series(avg_distances, 'sma', smoothing)

            smoothed_series = QLineSeries()
            smoothed_series.setName("Smoothed")

            for i, value in enumerate(smoothed_distances):
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                smoothed_series.append(timestamp_ms, value)

            # Set pen for smoothed series
            smooth_pen = QPen(QColor("#e74c3c"))
            smooth_pen.setWidth(3)
            smoothed_series.setPen(smooth_pen)

            self.chart.addSeries(smoothed_series)

        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setTitleText("Date")
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)

        axis_y = QValueAxis()
        axis_y.setTitleText("Distance (km)")
        axis_y.setLabelFormat("%.1f")

        max_distance = max(avg_distances) if avg_distances else 10
        axis_y.setRange(0, max_distance * 1.1)

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
