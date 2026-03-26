"""
Heart rate analysis chart widget with efficiency factor.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any
import math

from ..analytics.smoothing import Smoother


class HeartRateChart(QWidget):
    """Chart displaying heart rate metrics and efficiency factor."""

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
        self.chart.setTitle(self.tr("Heart Rate Analysis"))
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
        # Store for RoC toggle re-rendering
        self._last_aggregates = aggregates
        self._last_smoothing = smoothing

        # Remove all series and axes
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if not aggregates:
            return

        # Filter to complete periods only, AND periods with HR data
        complete_aggregates = [agg for agg in aggregates if agg.get('is_complete', True)]
        hr_aggregates = [agg for agg in complete_aggregates if agg.get('num_hr_activities', 0) > 0]

        if not hr_aggregates:
            self.chart.setTitle(self.tr("Heart Rate Analysis (No HR data available)"))
            return

        # Extract period dates
        period_dates = [agg['period_date'] for agg in hr_aggregates]

        # Extract heart rate data
        avg_hr_data = [agg['avg_heartrate'] for agg in hr_aggregates]
        min_hr_data = [agg['min_avg_heartrate'] for agg in hr_aggregates]
        max_hr_data = [agg['max_heartrate'] for agg in hr_aggregates]
        ef_data = [agg['efficiency_factor'] * 1000 for agg in hr_aggregates]  # Scale EF for better visualization

        # Apply smoothing if enabled (before creating series)
        if smoothing != 'off':
            avg_hr_data = Smoother.smooth_series(avg_hr_data, 'sma', smoothing)
            min_hr_data = Smoother.smooth_series(min_hr_data, 'sma', smoothing)
            max_hr_data = Smoother.smooth_series(max_hr_data, 'sma', smoothing)
            ef_data = Smoother.smooth_series(ef_data, 'sma', smoothing)

        # Create area series for HR range (min to max)
        # Build lists of valid data points where both min and max exist
        valid_area_points = []
        for i in range(len(hr_aggregates)):
            min_val = min_hr_data[i]
            max_val = max_hr_data[i]
            if (min_val is not None and min_val > 0 and
                max_val is not None and max_val > 0):
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                valid_area_points.append((timestamp_ms, min_val, max_val))

        # Only create area series if we have valid data
        if len(valid_area_points) > 0:
            # IMPORTANT: Store as instance variables to prevent garbage collection (PYSIDE-1285)
            self._hr_lower_series = QLineSeries()
            self._hr_upper_series = QLineSeries()

            for timestamp_ms, min_val, max_val in valid_area_points:
                self._hr_lower_series.append(timestamp_ms, min_val)
                self._hr_upper_series.append(timestamp_ms, max_val)

            # Create area series - keep reference as instance variable
            self._hr_area = QAreaSeries(self._hr_upper_series, self._hr_lower_series)
            self._hr_area.setName(self.tr("HR Range (Min-Max)"))

            # Style the area with semi-transparent blue
            area_color = QColor(52, 152, 219, 60)  # Blue with alpha
            self._hr_area.setBrush(QBrush(area_color))

            # Subtle border
            border_pen = QPen(QColor(41, 128, 185))
            border_pen.setWidth(1)
            self._hr_area.setPen(border_pen)

            self.chart.addSeries(self._hr_area)

        # Create average HR series
        avg_hr_series = QLineSeries()
        avg_hr_series.setName(self.tr("Average HR"))

        for i, value in enumerate(avg_hr_data):
            if value is not None and value > 0:
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                avg_hr_series.append(timestamp_ms, value)

        if avg_hr_series.count() > 0:
            pen = QPen(QColor("#e74c3c"))
            pen.setWidth(2)
            avg_hr_series.setPen(pen)
            self.chart.addSeries(avg_hr_series)

        # Create efficiency factor series
        ef_series = QLineSeries()
        ef_series.setName(self.tr("Efficiency Factor (×1000)"))

        for i, value in enumerate(ef_data):
            if value is not None and value > 0:
                timestamp_ms = int(period_dates[i].timestamp() * 1000)
                ef_series.append(timestamp_ms, value)

        if ef_series.count() > 0:
            ef_pen = QPen(QColor("#2ecc71"))
            ef_pen.setWidth(2)
            ef_series.setPen(ef_pen)
            self.chart.addSeries(ef_series)

        # Rate of Change overlay (if enabled)
        roc_series = None
        if self.roc_checkbox.isChecked():
            # Calculate RoC for average HR
            roc_data = self._calculate_rate_of_change(hr_aggregates, 'avg_heartrate')

            # Create RoC series
            roc_series = QLineSeries()
            roc_series.setName(self.tr("HR RoC (bpm/week)"))

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
            else:
                roc_series = None

        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)

        # Y-axis for heart rate
        axis_y_hr = QValueAxis()
        axis_y_hr.setTitleText(self.tr("Heart Rate (bpm)"))
        axis_y_hr.setLabelFormat("%d")

        # Calculate range for HR axis
        all_hr_values = [v for v in (min_hr_data + avg_hr_data + max_hr_data) if v is not None and v > 0]
        if all_hr_values:
            min_hr = min(all_hr_values)
            max_hr = max(all_hr_values)
            hr_margin = (max_hr - min_hr) * 0.1 if max_hr > min_hr else 10
            axis_y_hr.setRange(max(0, min_hr - hr_margin), max_hr + hr_margin)

        # Y-axis for efficiency factor
        axis_y_ef = QValueAxis()
        axis_y_ef.setTitleText(self.tr("Efficiency Factor (m/s per bpm ×1000)"))
        axis_y_ef.setLabelFormat("%.2f")

        valid_ef_data = [v for v in ef_data if v is not None and v > 0]
        if valid_ef_data:
            min_ef = min(valid_ef_data)
            max_ef = max(valid_ef_data)
            ef_margin = (max_ef - min_ef) * 0.1 if max_ef > min_ef else 1
            axis_y_ef.setRange(max(0, min_ef - ef_margin), max_ef + ef_margin)

        # Y-axis for RoC (if enabled)
        axis_y_roc = None
        if roc_series is not None:
            axis_y_roc = QValueAxis()
            axis_y_roc.setTitleText(self.tr("HR Rate of Change (bpm/week)"))
            axis_y_roc.setLabelFormat("%.2f")

            # Auto-range based on RoC values
            roc_data = self._calculate_rate_of_change(hr_aggregates, 'avg_heartrate')
            valid_roc = [v for v in roc_data if not math.isnan(v)]
            if valid_roc:
                min_roc = min(valid_roc)
                max_roc = max(valid_roc)
                margin = (max_roc - min_roc) * 0.2 if max_roc != min_roc else 0.1
                axis_y_roc.setRange(min_roc - margin, max_roc + margin)

        # Only add axes if we have series to display
        if len(self.chart.series()) > 0:
            # Add axes to chart
            self.chart.addAxis(axis_x, Qt.AlignBottom)
            self.chart.addAxis(axis_y_hr, Qt.AlignLeft)

            # Add right axis: EF if no RoC, or RoC if enabled (EF hidden when RoC shown)
            if axis_y_roc is not None:
                self.chart.addAxis(axis_y_roc, Qt.AlignRight)
            else:
                self.chart.addAxis(axis_y_ef, Qt.AlignRight)

            # Attach series to axes
            for series in self.chart.series():
                # Special handling for QAreaSeries
                if isinstance(series, QAreaSeries):
                    try:
                        series.attachAxis(axis_x)
                        series.attachAxis(axis_y_hr)
                    except Exception as e:
                        print(f"Warning: Could not attach area series: {e}")
                        continue
                else:
                    series.attachAxis(axis_x)
                    # Attach to appropriate Y axis based on series name
                    if "RoC" in series.name():
                        # RoC series goes to RoC axis if available
                        if axis_y_roc is not None:
                            series.attachAxis(axis_y_roc)
                        else:
                            series.attachAxis(axis_y_hr)
                    elif "EF" in series.name() or "Efficiency" in series.name():
                        # EF goes to right axis if no RoC, otherwise left HR axis
                        if axis_y_roc is None:
                            series.attachAxis(axis_y_ef)
                        else:
                            series.attachAxis(axis_y_hr)
                    else:
                        # All HR-related series (bars, average) go to left axis
                        series.attachAxis(axis_y_hr)

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
