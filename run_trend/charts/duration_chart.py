"""
Duration analysis chart widget.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any

from ..analytics.smoothing import Smoother


class DurationChart(QWidget):
    """Chart displaying training duration metrics."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle(self.tr("Training Duration Analysis"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(self.chart_view)

    def update_chart(
        self,
        aggregates: List[Dict[str, Any]],
        smoothing: str = 'off'
    ):
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

        # Filter to complete periods only
        complete_aggregates = [agg for agg in aggregates if agg.get('is_complete', True)]

        if not complete_aggregates:
            return

        # Extract period dates
        period_dates = [agg['period_date'] for agg in complete_aggregates]

        # Extract duration data
        total_time_h = [agg.get('total_moving_time_h', 0.0) for agg in complete_aggregates]
        avg_duration_min = [agg.get('avg_duration_per_run_min', 0.0) for agg in complete_aggregates]
        longest_duration_h = [agg.get('longest_duration_h', 0.0) for agg in complete_aggregates]
        avg_long_run_min = [agg.get('avg_long_run_duration_min', 0.0) for agg in complete_aggregates]

        # Apply smoothing if enabled
        if smoothing != 'off':
            total_time_h = Smoother.smooth_series(total_time_h, 'sma', smoothing)
            avg_duration_min = Smoother.smooth_series(avg_duration_min, 'sma', smoothing)
            longest_duration_h = Smoother.smooth_series(longest_duration_h, 'sma', smoothing)
            avg_long_run_min = Smoother.smooth_series(avg_long_run_min, 'sma', smoothing)

        # Create series for total training time (hours, left axis)
        total_time_series = QLineSeries()
        total_time_series.setName(self.tr("Total Training Time"))

        for i, value in enumerate(total_time_h):
            if value is not None and value >= 0:
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                total_time_series.append(timestamp_ms, value)

        if total_time_series.count() > 0:
            pen = QPen(QColor("#9b59b6"))  # Purple
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            total_time_series.setPen(pen)
            self.chart.addSeries(total_time_series)

        # Create series for longest duration (hours, left axis)
        longest_duration_series = QLineSeries()
        longest_duration_series.setName(self.tr("Longest Duration"))

        for i, value in enumerate(longest_duration_h):
            if value is not None and value >= 0:
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                longest_duration_series.append(timestamp_ms, value)

        if longest_duration_series.count() > 0:
            pen = QPen(QColor("#e74c3c"))  # Red
            pen.setWidth(2)
            pen.setStyle(Qt.DotLine)
            longest_duration_series.setPen(pen)
            self.chart.addSeries(longest_duration_series)

        # Create series for avg duration per run (minutes, right axis)
        avg_duration_series = QLineSeries()
        avg_duration_series.setName(self.tr("Avg Duration per Run"))

        for i, value in enumerate(avg_duration_min):
            if value is not None and value >= 0:
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                avg_duration_series.append(timestamp_ms, value)

        if avg_duration_series.count() > 0:
            pen = QPen(QColor("#3498db"))  # Blue
            pen.setWidth(2)
            avg_duration_series.setPen(pen)
            self.chart.addSeries(avg_duration_series)

        # Create series for avg long run duration (minutes, right axis)
        avg_long_run_series = QLineSeries()
        avg_long_run_series.setName(self.tr("Avg Long Run Duration"))

        for i, value in enumerate(avg_long_run_min):
            if value is not None and value >= 0:
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                avg_long_run_series.append(timestamp_ms, value)

        if avg_long_run_series.count() > 0:
            pen = QPen(QColor("#f39c12"))  # Orange
            pen.setWidth(2)
            avg_long_run_series.setPen(pen)
            self.chart.addSeries(avg_long_run_series)

        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)

        # Left Y-axis for hours (total time and longest duration)
        axis_y_hours = QValueAxis()
        axis_y_hours.setTitleText(self.tr("Duration (hours)"))
        axis_y_hours.setLabelFormat("%.1f")

        # Calculate range for hours axis
        all_hours_values = [v for v in (total_time_h + longest_duration_h) if v is not None and v >= 0]
        if all_hours_values:
            max_hours = max(all_hours_values)
            axis_y_hours.setRange(0, max_hours * 1.1)
        else:
            axis_y_hours.setRange(0, 10)

        # Right Y-axis for minutes (avg duration per run and avg long run duration)
        axis_y_minutes = QValueAxis()
        axis_y_minutes.setTitleText(self.tr("Duration (minutes)"))
        axis_y_minutes.setLabelFormat("%.0f")

        # Calculate range for minutes axis
        all_minutes_values = [v for v in (avg_duration_min + avg_long_run_min) if v is not None and v >= 0]
        if all_minutes_values:
            max_minutes = max(all_minutes_values)
            axis_y_minutes.setRange(0, max_minutes * 1.1)
        else:
            axis_y_minutes.setRange(0, 60)

        # Only add axes if we have series to display
        if len(self.chart.series()) > 0:
            # Add axes to chart
            self.chart.addAxis(axis_x, Qt.AlignBottom)
            self.chart.addAxis(axis_y_hours, Qt.AlignLeft)
            self.chart.addAxis(axis_y_minutes, Qt.AlignRight)

            # Attach series to axes
            for series in self.chart.series():
                series.attachAxis(axis_x)
                # Attach to appropriate Y axis based on series name
                if "Total Training Time" in series.name() or "Longest Duration" in series.name():
                    series.attachAxis(axis_y_hours)
                else:
                    # Avg Duration per Run and Avg Long Run Duration go to right axis (minutes)
                    series.attachAxis(axis_y_minutes)

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
