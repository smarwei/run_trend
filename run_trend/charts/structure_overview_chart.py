"""
Training structure overview chart widget.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any

from ..analytics.smoothing import Smoother


class StructureOverviewChart(QWidget):
    """Chart displaying comparative view of training structure metrics."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel(
            self.tr("This chart shows all structure metrics normalized to 0-100% for comparison. "
            "It helps understand HOW your training load is composed.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        layout.addWidget(info_label)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle(self.tr("Training Structure Overview (Normalized)"))
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

        # Extract all metrics
        total_distances = [agg['total_distance_km'] for agg in aggregates]
        num_runs = [agg['num_runs'] for agg in aggregates]
        avg_distances = [agg['avg_distance_per_run_km'] for agg in aggregates]
        longest_runs = [agg['longest_run_km'] for agg in aggregates]

        # Normalize function (0-100 scale)
        def normalize(values):
            if not values:
                return values
            min_val = min(values)
            max_val = max(values)
            if max_val == min_val:
                return [50.0] * len(values)  # All same value
            return [(v - min_val) / (max_val - min_val) * 100 for v in values]

        # Normalize all metrics
        norm_distances = normalize(total_distances)
        norm_runs = normalize(num_runs)
        norm_avg_distances = normalize(avg_distances)
        norm_longest = normalize(longest_runs)

        # Apply smoothing if enabled
        if smoothing != 'off':
            norm_distances = Smoother.smooth_series(norm_distances, 'sma', smoothing)
            norm_runs = Smoother.smooth_series(norm_runs, 'sma', smoothing)
            norm_avg_distances = Smoother.smooth_series(norm_avg_distances, 'sma', smoothing)
            norm_longest = Smoother.smooth_series(norm_longest, 'sma', smoothing)

        # Create series for each metric
        # Total Distance
        distance_series = QLineSeries()
        distance_series.setName(self.tr("Total Distance"))
        for i, value in enumerate(norm_distances):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            distance_series.append(timestamp_ms, value)
        pen_distance = QPen(QColor("#3498db"))
        pen_distance.setWidth(2)
        distance_series.setPen(pen_distance)
        self.chart.addSeries(distance_series)

        # Number of Runs
        runs_series = QLineSeries()
        runs_series.setName(self.tr("Number of Runs"))
        for i, value in enumerate(norm_runs):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            runs_series.append(timestamp_ms, value)
        pen_runs = QPen(QColor("#9b59b6"))
        pen_runs.setWidth(2)
        runs_series.setPen(pen_runs)
        self.chart.addSeries(runs_series)

        # Average Distance per Run
        avg_series = QLineSeries()
        avg_series.setName(self.tr("Avg Distance/Run"))
        for i, value in enumerate(norm_avg_distances):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            avg_series.append(timestamp_ms, value)
        pen_avg = QPen(QColor("#27ae60"))
        pen_avg.setWidth(2)
        avg_series.setPen(pen_avg)
        self.chart.addSeries(avg_series)

        # Longest Run
        longest_series = QLineSeries()
        longest_series.setName(self.tr("Longest Run"))
        for i, value in enumerate(norm_longest):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            longest_series.append(timestamp_ms, value)
        pen_longest = QPen(QColor("#e67e22"))
        pen_longest.setWidth(2)
        longest_series.setPen(pen_longest)
        self.chart.addSeries(longest_series)

        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)

        axis_y = QValueAxis()
        axis_y.setTitleText(self.tr("Normalized Value (%)"))
        axis_y.setLabelFormat("%.0f")
        axis_y.setRange(0, 100)

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)

        # Attach all series to axes
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
