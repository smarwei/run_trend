"""
Base chart widget with shared functionality for all chart classes.
"""
import math
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel, QPushButton,
    QMenu, QFileDialog, QMessageBox,
)
from PySide6.QtCharts import (
    QChart, QChartView, QCategoryAxis, QDateTimeAxis, QValueAxis,
)
from PySide6.QtCore import Qt, QDateTime, QCoreApplication, Signal
from PySide6.QtGui import QPainter, QBrush, QColor
from typing import Any, Dict, List, Optional

from ..analytics.smoothing import Smoother
from ..projection.forecaster import Forecaster
from ..ui.help_label import make_help_icon


def format_pace_minutes(value: float) -> str:
    """Format pace given in min/km decimal as MM:SS (e.g. 5.5 -> "5:30").

    Rounds to the nearest whole second so floating-point tick values like
    4.9999 don't render as "4:59" when 5.0 was intended.
    """
    total_seconds = max(0, int(round(value * 60)))
    mins, secs = divmod(total_seconds, 60)
    return f"{mins}:{secs:02d}"


class BaseChart(QWidget):
    """Base class for all chart widgets. Provides shared helper methods."""

    # Emitted when the user clicks the empty-state "Connect" button.
    # MainWindow connects this to the OAuth flow so users can authorize
    # without leaving the chart they were looking at.
    connect_requested = Signal()

    def _setup_chart_view(self, title: str, help_tooltip: Optional[str] = None) -> None:
        """Create self.chart and self.chart_view. Call from subclass _setup_ui().

        If help_tooltip is given, a small '?' badge is placed in a header row
        above the chart so users can hover to read what the metric means.
        """
        layout = QVBoxLayout(self)

        if help_tooltip:
            header = QHBoxLayout()
            header.addStretch()
            header.addWidget(make_help_icon(help_tooltip))
            layout.addLayout(header)

        self.chart = QChart()
        self.chart.setTitle(title)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(self._wrap_chart_view_with_empty_state(self.chart_view))

    # ------------------------------------------------------------------ #
    # Chart export                                                         #
    # ------------------------------------------------------------------ #

    def _on_chart_context_menu(self, position) -> None:
        """Show a right-click menu on the chart with an Export-as-PNG action."""
        menu = QMenu(self.chart_view)
        export_action = menu.addAction(
            QCoreApplication.translate("BaseChart", "Export Chart as PNG…")
        )
        chosen = menu.exec(self.chart_view.mapToGlobal(position))
        if chosen is export_action:
            self._export_chart_png()

    def _export_chart_png(self) -> None:
        """Save the current chart to a PNG file chosen by the user."""
        title = self.chart.title() or "chart"
        # Filename-safe slug from the chart title.
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in title).strip("_") or "chart"
        date = datetime.now().date().isoformat()
        default_name = f"runtrend_{slug.lower()}_{date}.png"

        path, _ = QFileDialog.getSaveFileName(
            self,
            QCoreApplication.translate("BaseChart", "Export Chart as PNG"),
            default_name,
            QCoreApplication.translate("BaseChart", "PNG Image (*.png)"),
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"

        pixmap = self.chart_view.grab()
        if not pixmap.save(path, "PNG"):
            QMessageBox.warning(
                self,
                QCoreApplication.translate("BaseChart", "Export failed"),
                QCoreApplication.translate(
                    "BaseChart", "Could not write the chart image to disk."
                ),
            )

    # ------------------------------------------------------------------ #
    # Empty-state overlay                                                  #
    # ------------------------------------------------------------------ #

    def _wrap_chart_view_with_empty_state(self, chart_view: QChartView) -> QStackedWidget:
        """Wrap a QChartView in a QStackedWidget that can swap to an empty-state page.

        Returns the stack (page 0 = chart_view, page 1 = empty state) — add the
        return value to your subclass layout instead of `chart_view` directly.

        The empty-state page contains a centred message label and an optional
        "Connect to Strava" button that emits self.connect_requested when clicked.

        Right-click on the chart opens an Export-as-PNG action; we wire it
        here because every chart goes through this helper, so the menu is
        available on the legacy charts that build their own QChartView too.
        """
        chart_view.setContextMenuPolicy(Qt.CustomContextMenu)
        chart_view.customContextMenuRequested.connect(self._on_chart_context_menu)

        stack = QStackedWidget()
        stack.addWidget(chart_view)

        empty_widget = QWidget()
        el = QVBoxLayout(empty_widget)
        el.addStretch()

        self._empty_label = QLabel("")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setWordWrap(True)
        self._empty_label.setStyleSheet(
            "color: gray; font-size: 13px; padding: 20px;"
        )
        el.addWidget(self._empty_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._connect_button = QPushButton(
            QCoreApplication.translate("BaseChart", "Connect to Strava")
        )
        self._connect_button.clicked.connect(self.connect_requested.emit)
        self._connect_button.setVisible(False)
        btn_row.addWidget(self._connect_button)
        btn_row.addStretch()
        el.addLayout(btn_row)
        el.addStretch()

        stack.addWidget(empty_widget)
        self._chart_stack = stack
        return stack

    def show_empty_state(self, message: str, show_connect_button: bool = False) -> None:
        """Replace the chart with a centred message (and optional Connect button)."""
        if not hasattr(self, "_chart_stack"):
            return  # No empty-state overlay installed (custom layout opted out)
        self._empty_label.setText(message)
        self._connect_button.setVisible(show_connect_button)
        self._chart_stack.setCurrentIndex(1)

    def _hide_empty_state(self) -> None:
        """Show the chart again, hiding any empty-state overlay."""
        if hasattr(self, "_chart_stack"):
            self._chart_stack.setCurrentIndex(0)

    # ------------------------------------------------------------------ #
    # Chart lifecycle helpers                                              #
    # ------------------------------------------------------------------ #

    def _clear_chart(self) -> None:
        """Remove all series and axes from the chart, and hide the empty-state overlay.

        Charts call this at the top of update_chart, so the chart_view is
        always restored before plotting fresh data; subclasses that determine
        the data is empty can call show_empty_state() afterwards.
        """
        self._hide_empty_state()
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

    def _create_pace_axis(
        self,
        title: str,
        min_val: float,
        max_val: float,
        reverse: bool = False,
    ) -> QCategoryAxis:
        """Create a pace axis whose tick labels read as MM:SS instead of decimal.

        The axis range and ticks are aligned to clean pace boundaries (every
        15 s, 30 s, or full minute depending on span) so labels never end up
        like "5:17" — they always sit on natural pace marks.

        Args:
            title:   Already-translated axis label.
            min_val: Lower bound of the data (in min/km).
            max_val: Upper bound of the data (in min/km).
            reverse: Set True to put faster pace (lower values) at the top.
        """
        axis = QCategoryAxis()
        axis.setTitleText(title)
        axis.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)

        span = max(max_val - min_val, 1e-6)
        if span <= 1.5:
            step = 0.25  # 15 s ticks for narrow ranges
        elif span <= 4.0:
            step = 0.5   # 30 s ticks
        else:
            step = 1.0   # full-minute ticks

        start = math.floor(min_val / step) * step
        end = math.ceil(max_val / step) * step
        if end <= start:
            end = start + step

        axis.setRange(start, end)

        eps = step * 1e-3
        v = start
        while v <= end + eps:
            axis.append(format_pace_minutes(v), v)
            v += step

        if reverse:
            axis.setReverse(True)
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
