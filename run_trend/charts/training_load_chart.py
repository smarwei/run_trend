"""
Training Load (ACWR) chart widget with safe zones.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from typing import List, Dict, Any


class TrainingLoadChart(QWidget):
    """Chart displaying Training Load (ACWR) over time."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create chart
        self.chart = QChart()
        self.chart.setTitle(self.tr("Training Load (ACWR)"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(self.chart_view)

    def update_chart(self, aggregates: List[Dict[str, Any]]):
        """
        Update chart with training load data.

        Args:
            aggregates: List of period aggregates with training_load field
        """
        # Remove all series and axes
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if not aggregates:
            return

        # Filter to aggregates with training_load data
        load_aggregates = [
            agg for agg in aggregates
            if agg.get('training_load', {}).get('has_load', False)
        ]

        if len(load_aggregates) < 2:
            self.chart.setTitle(self.tr("Training Load (Need 5+ weeks)"))
            return

        # Extract data
        period_dates = [agg['period_date'] for agg in load_aggregates]
        load_scores = [agg['training_load']['training_load'] for agg in load_aggregates]

        # Create X axis (DateTime)
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            max_date = QDateTime.fromSecsSinceEpoch(int(period_dates[-1].timestamp()))
            axis_x.setRange(min_date, max_date)

        # Y axis for load score
        axis_y = QValueAxis()
        axis_y.setTitleText(self.tr("Training Load Score"))
        axis_y.setLabelFormat("%d")
        axis_y.setRange(0, 100)

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)

        # Safe zone areas (colored backgrounds)
        # Store as instance variables to prevent garbage collection (PYSIDE-1285)

        # Zone 1: Safe (40-65) - Green
        self._safe_lower = QLineSeries()
        self._safe_upper = QLineSeries()
        for date in [period_dates[0], period_dates[-1]]:
            ts = int(date.timestamp() * 1000)
            self._safe_lower.append(ts, 40)
            self._safe_upper.append(ts, 65)
        self._safe_area = QAreaSeries(self._safe_upper, self._safe_lower)
        self._safe_area.setName(self.tr("Safe Zone (40-65)"))
        self._safe_area.setBrush(QBrush(QColor(39, 174, 96, 30)))  # Green transparent
        self._safe_area.setPen(QPen(Qt.NoPen))
        self.chart.addSeries(self._safe_area)
        self._safe_area.attachAxis(axis_x)
        self._safe_area.attachAxis(axis_y)

        # Zone 2: Caution (65-80) - Yellow
        self._caution_lower = QLineSeries()
        self._caution_upper = QLineSeries()
        for date in [period_dates[0], period_dates[-1]]:
            ts = int(date.timestamp() * 1000)
            self._caution_lower.append(ts, 65)
            self._caution_upper.append(ts, 80)
        self._caution_area = QAreaSeries(self._caution_upper, self._caution_lower)
        self._caution_area.setName(self.tr("Caution Zone (65-80)"))
        self._caution_area.setBrush(QBrush(QColor(243, 156, 18, 30)))  # Yellow transparent
        self._caution_area.setPen(QPen(Qt.NoPen))
        self.chart.addSeries(self._caution_area)
        self._caution_area.attachAxis(axis_x)
        self._caution_area.attachAxis(axis_y)

        # Zone 3: Danger (80-100) - Red
        self._danger_lower = QLineSeries()
        self._danger_upper = QLineSeries()
        for date in [period_dates[0], period_dates[-1]]:
            ts = int(date.timestamp() * 1000)
            self._danger_lower.append(ts, 80)
            self._danger_upper.append(ts, 100)
        self._danger_area = QAreaSeries(self._danger_upper, self._danger_lower)
        self._danger_area.setName(self.tr("Danger Zone (80+)"))
        self._danger_area.setBrush(QBrush(QColor(231, 76, 60, 30)))  # Red transparent
        self._danger_area.setPen(QPen(Qt.NoPen))
        self.chart.addSeries(self._danger_area)
        self._danger_area.attachAxis(axis_x)
        self._danger_area.attachAxis(axis_y)

        # Training Load line
        load_series = QLineSeries()
        load_series.setName(self.tr("Training Load"))

        for i, score in enumerate(load_scores):
            timestamp_ms = int(period_dates[i].timestamp() * 1000)
            load_series.append(timestamp_ms, score)

        pen = QPen(QColor("#2c3e50"))  # Dark blue
        pen.setWidth(3)
        load_series.setPen(pen)

        self.chart.addSeries(load_series)
        load_series.attachAxis(axis_x)
        load_series.attachAxis(axis_y)

        # Legend
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        # Connect legend markers
        self._connect_legend_markers()

    def _connect_legend_markers(self):
        """Connect legend markers for interactive toggling."""
        for marker in self.chart.legend().markers():
            marker.clicked.connect(self._on_legend_marker_clicked)

    def _on_legend_marker_clicked(self):
        """Handle legend marker clicks."""
        marker = self.sender()
        if marker:
            series = marker.series()
            series.setVisible(not series.isVisible())
            marker.setVisible(True)
            if series.isVisible():
                marker.setLabelBrush(QBrush(QColor("black")))
            else:
                marker.setLabelBrush(QBrush(QColor("gray")))
