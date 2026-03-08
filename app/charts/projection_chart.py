"""
Projection/forecast chart widget.
"""
from datetime import timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QScatterSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any

from ..projection.forecaster import Forecaster


class ProjectionChart(QWidget):
    """Chart displaying historical data and future projections."""

    # Long run milestones (in km)
    LONG_RUN_MILESTONES = {
        '10K Run': 10.0,
        '15K Run': 15.0,
        'Half Marathon': 21.1,
        '30K Run': 30.0,
        'Marathon': 42.195
    }

    def __init__(self):
        super().__init__()
        self.projection_mode = 'volume'  # 'volume' or 'long_run'
        self.periods_ahead = 12  # Default projection length
        self.settings_callback = None  # Callback to save settings
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Mode selector and periods ahead control
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Projection Mode:"))

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Volume (Total Distance)", "Long Run"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        mode_layout.addSpacing(20)
        mode_layout.addWidget(QLabel("Periods Ahead:"))

        self.periods_spinbox = QSpinBox()
        self.periods_spinbox.setMinimum(1)
        self.periods_spinbox.setMaximum(104)  # 104 weeks or 24 months = ~2 years
        self.periods_spinbox.setValue(12)
        self.periods_spinbox.valueChanged.connect(self._on_periods_changed)
        mode_layout.addWidget(self.periods_spinbox)

        mode_layout.addStretch()

        layout.addLayout(mode_layout)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle("Volume Projection")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(self.chart_view)

    def _on_mode_changed(self, index):
        """Handle projection mode change."""
        self.projection_mode = 'volume' if index == 0 else 'long_run'
        # Save to settings if callback is set
        if self.settings_callback:
            self.settings_callback('ui_projection_mode', self.mode_combo.currentText())
        # Trigger chart update if we have data
        if hasattr(self, '_last_aggregates'):
            self.update_chart(self._last_aggregates, self._last_period_type)

    def _on_periods_changed(self, value):
        """Handle projection length change."""
        self.periods_ahead = value
        # Save to settings if callback is set
        if self.settings_callback:
            self.settings_callback('ui_projection_periods', value)
        # Trigger chart update if we have data
        if hasattr(self, '_last_aggregates'):
            self.update_chart(self._last_aggregates, self._last_period_type)

    def update_chart(self, aggregates: List[Dict[str, Any]], period_type: str = 'week'):
        """
        Update chart with historical and projected data.

        Args:
            aggregates: List of period aggregates
            period_type: 'week' or 'month'
        """
        # Store for mode switching
        self._last_aggregates = aggregates
        self._last_period_type = period_type

        # Adjust maximum based on period type (2 years forward)
        if period_type == 'week':
            self.periods_spinbox.setMaximum(104)  # 104 weeks = 2 years
        else:  # month
            self.periods_spinbox.setMaximum(24)   # 24 months = 2 years

        # Adjust current value if it exceeds new maximum
        if self.periods_ahead > self.periods_spinbox.maximum():
            self.periods_spinbox.setValue(self.periods_spinbox.maximum())

        # Remove all series and axes
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if not aggregates or len(aggregates) < 2:
            return

        # Extract period dates
        period_dates = [agg['period_date'] for agg in aggregates]

        # Choose metric and milestones based on mode
        if self.projection_mode == 'volume':
            metric_key = 'total_distance_km'
            chart_title = "Volume Projection"
            historical_label = "Historical Volume"
            milestones = Forecaster.MILESTONES
        else:  # long_run
            metric_key = 'longest_run_km'
            chart_title = "Long Run Projection"
            historical_label = "Historical Long Run"
            milestones = self.LONG_RUN_MILESTONES

        self.chart.setTitle(chart_title)

        # Extract historical data
        historical_data = [agg[metric_key] for agg in aggregates]

        # Create historical series
        historical_series = QLineSeries()
        historical_series.setName(historical_label)

        for i, value in enumerate(historical_data):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            historical_series.append(timestamp_ms, value)

        # Set pen for historical series
        hist_pen = QPen(QColor("#3498db"))
        hist_pen.setWidth(2)
        historical_series.setPen(hist_pen)

        self.chart.addSeries(historical_series)

        # Generate projection
        projection = Forecaster.project_trend(
            aggregates,
            metric_key,
            periods_ahead=self.periods_ahead,
            use_recent_periods=min(12, len(aggregates))
        )

        if projection.get('has_projection'):
            # Create projection series
            projection_series = QLineSeries()
            projection_series.setName("Projected Trend")

            # Start from last historical point
            last_timestamp_ms = int(period_dates[-1].timestamp() * 1000)
            projection_series.append(last_timestamp_ms, historical_data[-1])

            # Add projected points
            for proj_point in projection['projected_periods']:
                periods_ahead = proj_point['period_offset']
                if period_type == 'week':
                    future_date = period_dates[-1] + timedelta(weeks=periods_ahead)
                else:  # month
                    # Add months (approximation using 30 days)
                    future_date = period_dates[-1] + timedelta(days=30 * periods_ahead)
                timestamp_ms = int(future_date.timestamp() * 1000)
                projection_series.append(timestamp_ms, proj_point['projected_value'])

            # Set pen for projection series
            proj_pen = QPen(QColor("#e74c3c"))
            proj_pen.setWidth(2)
            proj_pen.setStyle(Qt.DashLine)
            projection_series.setPen(proj_pen)

            self.chart.addSeries(projection_series)

            # Add milestone markers
            for milestone_name, milestone_value in milestones.items():
                for proj_point in projection['projected_periods']:
                    if abs(proj_point['projected_value'] - milestone_value) < 2.0:
                        milestone_series = QScatterSeries()
                        milestone_series.setName(milestone_name)
                        milestone_series.setMarkerSize(12)
                        milestone_series.setColor(QColor("#f39c12"))

                        periods_ahead = proj_point['period_offset']
                        if period_type == 'week':
                            future_date = period_dates[-1] + timedelta(weeks=periods_ahead)
                        else:  # month
                            future_date = period_dates[-1] + timedelta(days=30 * periods_ahead)
                        timestamp_ms = int(future_date.timestamp() * 1000)
                        milestone_series.append(timestamp_ms, milestone_value)
                        self.chart.addSeries(milestone_series)
                        break

        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setTitleText("Date")
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            # Calculate max date including projections
            if period_type == 'week':
                max_future_date = period_dates[-1] + timedelta(weeks=self.periods_ahead)
            else:  # month
                max_future_date = period_dates[-1] + timedelta(days=30 * self.periods_ahead)
            max_date = QDateTime.fromSecsSinceEpoch(int(max_future_date.timestamp()))
            axis_x.setRange(min_date, max_date)

        axis_y = QValueAxis()
        axis_y.setTitleText("Distance (km)")
        axis_y.setLabelFormat("%.1f")

        max_distance = max(historical_data) if historical_data else 10
        if projection.get('has_projection'):
            projected_max = max(p['projected_value'] for p in projection['projected_periods'])
            max_distance = max(max_distance, projected_max)

        axis_y.setRange(0, max_distance * 1.2)

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
