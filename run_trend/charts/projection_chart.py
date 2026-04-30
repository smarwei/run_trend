"""
Projection/forecast chart widget.
"""
from datetime import datetime, timedelta
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QScatterSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from typing import List, Dict, Any

from .base_chart import BaseChart
from ..projection.forecaster import Forecaster


class ProjectionChart(BaseChart):
    """Chart displaying historical data and future projections."""

    LONG_RUN_MILESTONES = {
        '10K Run': 10.0,
        '15K Run': 15.0,
        'Half Marathon': 21.1,
        '30K Run': 30.0,
        'Marathon Ready': 32.0,
    }

    def __init__(self):
        super().__init__()
        self.projection_mode  = 'volume'
        self.periods_ahead    = 12
        self.settings_callback = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel(self.tr("Projection Mode:")))

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([self.tr("Volume (Total Distance)"), self.tr("Long Run")])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        mode_layout.addSpacing(20)
        mode_layout.addWidget(QLabel(self.tr("Periods Ahead:")))

        self.periods_spinbox = QSpinBox()
        self.periods_spinbox.setMinimum(1)
        self.periods_spinbox.setMaximum(104)
        self.periods_spinbox.setValue(12)
        self.periods_spinbox.valueChanged.connect(self._on_periods_changed)
        mode_layout.addWidget(self.periods_spinbox)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        self.chart = QChart()
        self.chart.setTitle(self.tr("Volume Projection"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

    def _on_mode_changed(self, index):
        self.projection_mode = 'volume' if index == 0 else 'long_run'
        if self.settings_callback:
            self.settings_callback('ui_projection_mode', self.mode_combo.currentText())
        if hasattr(self, '_last_aggregates'):
            self.update_chart(self._last_aggregates, self._last_period_type)

    def _on_periods_changed(self, value):
        self.periods_ahead = value
        if self.settings_callback:
            self.settings_callback('ui_projection_periods', value)
        if hasattr(self, '_last_aggregates'):
            self.update_chart(self._last_aggregates, self._last_period_type)

    def update_chart(self, aggregates: List[Dict[str, Any]], period_type: str = 'week'):
        self._last_aggregates  = aggregates
        self._last_period_type = period_type

        if period_type == 'week':
            self.periods_spinbox.setMaximum(104)
        else:
            self.periods_spinbox.setMaximum(24)
        if self.periods_ahead > self.periods_spinbox.maximum():
            self.periods_spinbox.setValue(self.periods_spinbox.maximum())

        self._clear_chart()
        if not aggregates or len(aggregates) < 2:
            return

        complete_aggregates = self._filter_complete_aggregates(aggregates)
        if not complete_aggregates or len(complete_aggregates) < 2:
            return

        period_dates = [agg['period_date'] for agg in complete_aggregates]

        if self.projection_mode == 'volume':
            metric_key       = 'total_distance_km'
            chart_title      = self.tr("Volume Projection")
            historical_label = self.tr("Historical Volume")
            milestones       = Forecaster.MILESTONES
        else:
            metric_key       = 'longest_run_km'
            chart_title      = self.tr("Long Run Projection")
            historical_label = self.tr("Historical Long Run")
            milestones       = self.LONG_RUN_MILESTONES

        self.chart.setTitle(chart_title)
        historical_data = [agg[metric_key] for agg in complete_aggregates]

        historical_series = QLineSeries()
        historical_series.setName(historical_label)
        for i, v in enumerate(historical_data):
            historical_series.append(int(period_dates[i].timestamp() * 1000), v)
        pen = QPen(QColor("#3498db"))
        pen.setWidth(2)
        historical_series.setPen(pen)
        self.chart.addSeries(historical_series)

        now = datetime.now()
        if period_type == 'week':
            anchor_date = (now - timedelta(days=now.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            anchor_date = datetime(now.year, now.month, 1)

        if period_type == 'week':
            gap_periods = max(0, round((anchor_date - period_dates[-1]).days / 7))
        else:
            gap_periods = max(0, (anchor_date.year - period_dates[-1].year) * 12
                             + (anchor_date.month - period_dates[-1].month))

        total_periods_needed = gap_periods + self.periods_ahead
        projection = Forecaster.project_trend(
            aggregates, metric_key,
            periods_ahead=total_periods_needed,
            use_recent_periods=min(12, len(aggregates)),
        )

        if projection.get('has_projection'):
            projection_series = QLineSeries()
            projection_series.setName(self.tr("Projected Trend"))

            if gap_periods == 0:
                anchor_value    = historical_data[-1]
                proj_start_date = period_dates[-1]
            elif gap_periods <= len(projection['projected_periods']):
                anchor_value    = projection['projected_periods'][gap_periods - 1]['projected_value']
                proj_start_date = anchor_date
            else:
                anchor_value    = historical_data[-1]
                proj_start_date = anchor_date

            projection_series.append(int(proj_start_date.timestamp() * 1000), anchor_value)

            for proj_point in projection['projected_periods']:
                offset = proj_point['period_offset']
                if offset <= gap_periods:
                    continue
                periods_from_anchor = offset - gap_periods
                if period_type == 'week':
                    future_date = anchor_date + timedelta(weeks=periods_from_anchor)
                else:
                    future_date = anchor_date + timedelta(days=30 * periods_from_anchor)
                projection_series.append(
                    int(future_date.timestamp() * 1000),
                    proj_point['projected_value'],
                )

            pen = QPen(QColor("#e74c3c"))
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            projection_series.setPen(pen)
            self.chart.addSeries(projection_series)

            for milestone_name, milestone_value in milestones.items():
                for proj_point in projection['projected_periods']:
                    if proj_point['period_offset'] <= gap_periods:
                        continue
                    if abs(proj_point['projected_value'] - milestone_value) < 2.0:
                        ms = QScatterSeries()
                        ms.setName(self.tr(milestone_name))
                        ms.setMarkerSize(12)
                        ms.setColor(QColor("#f39c12"))
                        periods_from_anchor = proj_point['period_offset'] - gap_periods
                        if period_type == 'week':
                            future_date = anchor_date + timedelta(weeks=periods_from_anchor)
                        else:
                            future_date = anchor_date + timedelta(days=30 * periods_from_anchor)
                        ms.append(int(future_date.timestamp() * 1000), milestone_value)
                        self.chart.addSeries(ms)
                        break

        # Axes — custom x range to include future window
        from PySide6.QtCharts import QDateTimeAxis
        from PySide6.QtCore import QDateTime
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.tr("Date"))
        axis_x.setFormat("MMM yyyy")
        if period_dates:
            min_date = QDateTime.fromSecsSinceEpoch(int(period_dates[0].timestamp()))
            if period_type == 'week':
                max_future = anchor_date + timedelta(weeks=self.periods_ahead)
            else:
                max_future = anchor_date + timedelta(days=30 * self.periods_ahead)
            axis_x.setRange(min_date, QDateTime.fromSecsSinceEpoch(int(max_future.timestamp())))

        max_dist = max(historical_data) if historical_data else 10
        if projection.get('has_projection'):
            max_dist = max(max_dist, max(p['projected_value'] for p in projection['projected_periods']))
        axis_y = self._create_value_axis(
            self.tr("Distance (km)"), min_val=0, max_val=max_dist * 1.2
        )

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        for s in self.chart.series():
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self._connect_legend_markers()
