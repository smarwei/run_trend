"""
Base chart widget with shared functionality for all chart classes.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QValueAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QBrush, QColor
from typing import Any, Dict, List, Optional

from ..analytics.smoothing import Smoother
from ..projection.forecaster import Forecaster


class BaseChart(QWidget):
    """Base class for all chart widgets. Provides shared helper methods."""

    def _setup_chart_view(self, title: str) -> None:
        """Create self.chart and self.chart_view. Call from subclass _setup_ui()."""
        layout = QVBoxLayout(self)

        self.chart = QChart()
        self.chart.setTitle(title)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(self.chart_view)

    # ------------------------------------------------------------------ #
    # Chart lifecycle helpers                                              #
    # ------------------------------------------------------------------ #

    def _clear_chart(self) -> None:
        """Remove all series and axes from the chart."""
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

    def _filter_complete_aggregates(
        self, aggregates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Return only periods marked as complete (default: True)."""
        return [agg for agg in aggregates if agg.get('is_complete', True)]

    # ------------------------------------------------------------------ #
    # Data helpers                                                         #
    # ------------------------------------------------------------------ #

    def _smooth_data(self, data: List[float], smoothing: str) -> List[float]:
        """Apply SMA smoothing if smoothing != 'off'."""
        if smoothing == 'off':
            return data
        return Smoother.smooth_series(data, 'sma', smoothing)

    def _calculate_rate_of_change(
        self,
        aggregates: List[Dict[str, Any]],
        metric_key: str,
    ) -> List[float]:
        """Rolling 8-period linear-regression slope for the given metric."""
        window_size = 8
        roc_values: List[float] = []

        for i in range(len(aggregates)):
            if i < window_size - 1:
                roc_values.append(float('nan'))
            else:
                window = aggregates[i - window_size + 1:i + 1]
                x_values = list(range(len(window)))
                y_values = [agg.get(metric_key, 0.0) for agg in window]
                slope, _ = Forecaster.linear_regression(x_values, y_values)
                roc_values.append(slope)

        return roc_values

    # ------------------------------------------------------------------ #
    # Axis factory helpers                                                 #
    # ------------------------------------------------------------------ #

    def _create_datetime_axis(
        self,
        dates: List,
        title: str,
        fmt: str = "MMM yyyy",
    ) -> QDateTimeAxis:
        """Create a configured QDateTimeAxis.

        Args:
            dates: List of datetime objects for range calculation.
            title: Already-translated axis label (call self.tr() in the subclass).
            fmt:   Qt date format string.
        """
        axis = QDateTimeAxis()
        axis.setTitleText(title)
        axis.setFormat(fmt)
        if dates:
            axis.setRange(
                QDateTime.fromSecsSinceEpoch(int(dates[0].timestamp())),
                QDateTime.fromSecsSinceEpoch(int(dates[-1].timestamp())),
            )
        return axis

    def _create_value_axis(
        self,
        title: str,
        fmt: str = "%.1f",
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> QValueAxis:
        """Create a configured QValueAxis.

        Args:
            title:   Already-translated axis label.
            fmt:     Label format string.
            min_val: Axis minimum (omit to leave auto).
            max_val: Axis maximum (omit to leave auto).
        """
        axis = QValueAxis()
        axis.setTitleText(title)
        axis.setLabelFormat(fmt)
        if min_val is not None and max_val is not None:
            axis.setRange(min_val, max_val)
        return axis

    # ------------------------------------------------------------------ #
    # Legend interaction                                                   #
    # ------------------------------------------------------------------ #

    def _connect_legend_markers(self) -> None:
        """Wire up legend markers for interactive series toggling."""
        for marker in self.chart.legend().markers():
            marker.clicked.connect(self._on_legend_marker_clicked)

    def _on_legend_marker_clicked(self) -> None:
        """Toggle visibility of a series when its legend marker is clicked."""
        marker = self.sender()
        if marker:
            series = marker.series()
            series.setVisible(not series.isVisible())
            marker.setVisible(True)
            if series.isVisible():
                marker.setLabelBrush(QBrush(QColor("black")))
            else:
                marker.setLabelBrush(QBrush(QColor("gray")))
