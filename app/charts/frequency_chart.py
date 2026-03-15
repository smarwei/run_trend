"""
Training frequency chart widget.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any

from ..analytics.smoothing import Smoother


class FrequencyChart(QWidget):
    """Chart displaying training frequency over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle(self.tr("Training Frequency"))
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

        # Extract frequency data
        num_runs = [agg['num_runs'] for agg in aggregates]

        # Apply smoothing if enabled
        if smoothing != 'off':
            num_runs = Smoother.smooth_series(num_runs, 'sma', smoothing)

        # Create series (smoothing already applied if enabled)
        series = QLineSeries()
        series.setName(self.tr("Runs per Period"))

        for i, value in enumerate(num_runs):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            series.append(timestamp_ms, value)

        # Set pen
        pen = QPen(QColor("#9b59b6"))
        pen.setWidth(2)
        series.setPen(pen)

        self.chart.addSeries(series)

        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)

        axis_y = QValueAxis()
        axis_y.setTitleText(self.tr("Number of Runs"))
        axis_y.setLabelFormat("%d")

        max_runs = max(num_runs) if num_runs else 10
        axis_y.setRange(0, max_runs * 1.2)

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
