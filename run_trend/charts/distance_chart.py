"""
Distance progress chart widget.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any
import math

from ..analytics.smoothing import Smoother


class DistanceChart(QWidget):
    """Chart displaying distance progress over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # RoC toggle checkbox
        toggle_layout = QHBoxLayout()
        self.roc_checkbox = QCheckBox(self.tr("Show Rate of Change"))
        self.roc_checkbox.setChecked(False)
        self.roc_checkbox.stateChanged.connect(self._on_roc_toggle)
        toggle_layout.addWidget(self.roc_checkbox)
        toggle_layout.addStretch()
        layout.addLayout(toggle_layout)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle(self.tr("Distance Progress"))
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
        # Store for RoC toggle re-rendering
        self._last_aggregates = aggregates
        self._last_smoothing = smoothing

        # Remove all series and axes
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if not aggregates:
            return

        # Filter to complete periods only
        # This prevents incomplete periods from showing as a misleading drop
        complete_aggregates = [agg for agg in aggregates if agg.get('is_complete', True)]

        if not complete_aggregates:
            return

        # Extract data
        distances = [agg['total_distance_km'] for agg in complete_aggregates]
        moving_times = [agg['total_moving_time_h'] for agg in complete_aggregates]
        run_counts = [agg['num_runs'] for agg in complete_aggregates]
        period_dates = [agg['period_date'] for agg in complete_aggregates]

        # Apply smoothing to all data
        if smoothing != 'off':
            distances = Smoother.smooth_series(distances, 'sma', smoothing)
            moving_times = Smoother.smooth_series(moving_times, 'sma', smoothing)
            run_counts = Smoother.smooth_series(run_counts, 'sma', smoothing)

        # Create primary X axis (DateTime)
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)
        self.chart.addAxis(axis_x, Qt.AlignBottom)

        # Primary Y axis for distance
        axis_y_distance = QValueAxis()
        axis_y_distance.setTitleText(self.tr("Distance (km)"))
        axis_y_distance.setLabelFormat("%.1f")
        max_distance = max(distances) if distances else 10
        axis_y_distance.setRange(0, max_distance * 1.1)
        self.chart.addAxis(axis_y_distance, Qt.AlignLeft)

        # Distance series (smoothing already applied if enabled)
        distance_series = QLineSeries()
        distance_series.setName(self.tr("Total Distance"))
        for i, value in enumerate(distances):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            distance_series.append(timestamp_ms, value)
        pen = QPen(QColor("#3498db"))
        pen.setWidth(2)
        distance_series.setPen(pen)
        self.chart.addSeries(distance_series)
        distance_series.attachAxis(axis_x)
        distance_series.attachAxis(axis_y_distance)

        # Secondary Y axis for time
        axis_y_time = QValueAxis()
        axis_y_time.setTitleText(self.tr("Moving Time (h)"))
        axis_y_time.setLabelFormat("%.1f")
        max_time = max(moving_times) if moving_times else 10
        axis_y_time.setRange(0, max_time * 1.1)
        self.chart.addAxis(axis_y_time, Qt.AlignRight)

        # Moving time series (initially hidden)
        time_series = QLineSeries()
        time_series.setName(self.tr("Moving Time"))
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
        count_series.setName(self.tr("Run Count"))
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

        # Rate of Change overlay (if enabled)
        if self.roc_checkbox.isChecked():
            # Calculate RoC
            roc_data = self._calculate_rate_of_change(complete_aggregates, 'total_distance_km')

            # Create RoC series
            roc_series = QLineSeries()
            roc_series.setName(self.tr("Distance RoC (km/week)"))

            for i, value in enumerate(roc_data):
                if not math.isnan(value):
                    timestamp_ms = int(period_dates[i].timestamp() * 1000)
                    roc_series.append(timestamp_ms, value)

            if roc_series.count() > 0:
                pen = QPen(QColor("#9b59b6"))  # Purple
                pen.setWidth(2)
                pen.setStyle(Qt.DashLine)
                roc_series.setPen(pen)
                self.chart.addSeries(roc_series)

                # Create RIGHT Y-axis for RoC
                axis_y_roc = QValueAxis()
                axis_y_roc.setTitleText(self.tr("Rate of Change (km/week)"))
                axis_y_roc.setLabelFormat("%.2f")

                # Auto-range based on RoC values
                valid_roc = [v for v in roc_data if not math.isnan(v)]
                if valid_roc:
                    min_roc = min(valid_roc)
                    max_roc = max(valid_roc)
                    margin = (max_roc - min_roc) * 0.2
                    axis_y_roc.setRange(min_roc - margin, max_roc + margin)

                self.chart.addAxis(axis_y_roc, Qt.AlignRight)
                roc_series.attachAxis(axis_x)
                roc_series.attachAxis(axis_y_roc)

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

    def _on_roc_toggle(self):
        """Handle RoC checkbox toggle - trigger chart update."""
        # We need to re-render the chart with/without RoC
        # Store aggregates and smoothing for re-rendering
        if hasattr(self, '_last_aggregates'):
            self.update_chart(self._last_aggregates, self._last_smoothing)

    def _calculate_rate_of_change(
        self,
        aggregates: List[Dict[str, Any]],
        metric_key: str
    ) -> List[float]:
        """
        Calculate rate of change using rolling 8-period linear regression.

        Args:
            aggregates: Complete period aggregates
            metric_key: Metric to calculate RoC for

        Returns:
            List of RoC values (same length as aggregates)
        """
        from ..projection.forecaster import Forecaster

        roc_values = []
        window_size = 8

        for i in range(len(aggregates)):
            if i < window_size - 1:
                # Not enough data for window, use NaN
                roc_values.append(float('nan'))
            else:
                # Get window of last 8 periods
                window = aggregates[i - window_size + 1:i + 1]
                x_values = list(range(len(window)))
                y_values = [agg.get(metric_key, 0.0) for agg in window]

                # Calculate slope
                slope, _ = Forecaster.linear_regression(x_values, y_values)
                roc_values.append(slope)

        return roc_values
