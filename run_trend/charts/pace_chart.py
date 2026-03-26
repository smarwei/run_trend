"""
Pace/Speed progress chart widget.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any
import math

from ..analytics.smoothing import Smoother


class PaceChart(QWidget):
    """Chart displaying pace or speed progress over time."""

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
        self.chart.setTitle(self.tr("Pace/Speed Progress"))
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
        # Store for RoC toggle re-rendering
        self._last_aggregates = aggregates
        self._last_smoothing = smoothing
        self._last_metric = metric

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

        # Extract period dates
        period_dates = [agg['period_date'] for agg in complete_aggregates]

        # Extract data based on metric
        if metric == 'pace':
            data = [agg['weighted_avg_pace_min_per_km'] for agg in complete_aggregates]
            title = self.tr("Pace Progress")
            y_label = self.tr("Pace (min/km)")
            series_name = self.tr("Pace")
        else:  # speed
            data = [agg['avg_speed_kmh'] for agg in complete_aggregates]
            title = self.tr("Speed Progress")
            y_label = self.tr("Speed (km/h)")
            series_name = self.tr("Speed")

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
        axis_x.setTitleText(self.tr("Date"))
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

        # Rate of Change overlay (if enabled)
        if self.roc_checkbox.isChecked():
            # Calculate RoC based on current metric
            if metric == 'pace':
                # For pace: lower is better, but RoC should show change magnitude
                # We'll show the raw pace change (negative = getting faster)
                roc_data = self._calculate_rate_of_change(complete_aggregates, 'weighted_avg_pace_min_per_km')
                roc_label = self.tr("Pace RoC (min/km per week)")
            else:  # speed
                roc_data = self._calculate_rate_of_change(complete_aggregates, 'avg_speed_kmh')
                roc_label = self.tr("Speed RoC (km/h per week)")

            # Create RoC series
            roc_series = QLineSeries()
            roc_series.setName(roc_label)

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
                axis_y_roc.setTitleText(roc_label)
                axis_y_roc.setLabelFormat("%.3f")

                # Auto-range based on RoC values
                valid_roc = [v for v in roc_data if not math.isnan(v)]
                if valid_roc:
                    min_roc = min(valid_roc)
                    max_roc = max(valid_roc)
                    margin = (max_roc - min_roc) * 0.2 if max_roc != min_roc else 0.1
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
            self.update_chart(self._last_aggregates, self._last_smoothing, self._last_metric)

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
