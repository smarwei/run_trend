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

    def _tr_milestone(self, name: str) -> str:
        """Translate a milestone name.

        pylupdate6 only extracts static literals, so each known milestone
        from ``Forecaster.MILESTONES`` and ``LONG_RUN_MILESTONES`` must
        appear here as a static ``self.tr("…")`` literal. Unknown names
        fall through untranslated.
        """
        table = {
            '5K': self.tr('5K'),
            '10K': self.tr('10K'),
            '10K Run': self.tr('10K Run'),
            '15K Run': self.tr('15K Run'),
            'Half Marathon': self.tr('Half Marathon'),
            '30K Run': self.tr('30K Run'),
            'Marathon Ready': self.tr('Marathon Ready'),
        }
        return table.get(name, name)

    def __init__(self):
        super().__init__()
        self.projection_mode  = 'volume'
        self.periods_ahead    = 12
        self.settings_callback = None
        self._goals: List[Dict[str, Any]] = []
        self._setup_ui()

    def set_goals(self, goals: List[Dict[str, Any]]) -> None:
        """Stash active goals; the next update_chart() draws them as targets."""
        self._goals = [
            g for g in (goals or []) if not g.get('achieved')
        ]

    def _render_goals(self, now, historical_value, projection,
                      anchor_date, gap_periods, period_type):
        """Overlay user-set targets on the long-run projection.

        Returns a list of (target_datetime, target_distance_km) for axis
        extension. Goals are skipped silently in volume mode because
        target_distance_km is a race distance, not a weekly volume budget.
        """
        rendered: List[tuple] = []
        if not self._goals or self.projection_mode != 'long_run':
            return rendered

        today_ms = int(now.timestamp() * 1000)
        for goal in self._goals:
            target_date_str = goal.get('target_date')
            target_distance = goal.get('target_distance_km')
            if not target_date_str or target_distance is None:
                continue
            try:
                target_dt = datetime.strptime(target_date_str, '%Y-%m-%d')
            except (TypeError, ValueError):
                continue
            if target_dt < now:
                continue
            target_ms = int(target_dt.timestamp() * 1000)

            projected_at_target = historical_value
            if projection.get('has_projection'):
                proj_periods = projection.get('projected_periods') or []
                matched = False
                for proj_point in proj_periods:
                    periods_from_anchor = proj_point['period_offset'] - gap_periods
                    if periods_from_anchor < 0:
                        continue
                    if period_type == 'week':
                        pdt = anchor_date + timedelta(weeks=periods_from_anchor)
                    else:
                        pdt = anchor_date + timedelta(days=30 * periods_from_anchor)
                    if pdt >= target_dt:
                        projected_at_target = proj_point['projected_value']
                        matched = True
                        break
                if not matched and proj_periods:
                    projected_at_target = proj_periods[-1]['projected_value']

            on_track = projected_at_target >= target_distance
            color = QColor("#27ae60") if on_track else QColor("#e74c3c")

            line = QLineSeries()
            line.setName(self.tr("Goal target ({} km)").format(round(target_distance, 1)))
            line.append(today_ms, historical_value)
            line.append(target_ms, target_distance)
            line_pen = QPen(color)
            line_pen.setWidth(2)
            line_pen.setStyle(Qt.DotLine)
            line.setPen(line_pen)
            self.chart.addSeries(line)

            marker = QScatterSeries()
            status = self.tr("on track") if on_track else self.tr("off track")
            marker.setName(self.tr("Goal {} km — {}").format(
                round(target_distance, 1), status,
            ))
            marker.setMarkerSize(14)
            marker.setColor(color)
            marker.append(target_ms, target_distance)
            self.chart.addSeries(marker)

            rendered.append((target_dt, target_distance))

        return rendered

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
        layout.addWidget(self._wrap_chart_view_with_empty_state(self.chart_view))

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

            # Skip milestones the runner has already achieved. Use ALL
            # aggregates (including the in-progress current period) so a
            # PR set today still suppresses the "you'll reach NN km"
            # marker even though the current period isn't yet in the
            # complete-only history line. Without this guard, a user
            # whose past complete weeks max out at e.g. 13 km but who
            # just ran 17 km today sees a misleading "15K Run" target
            # hovering on the projection.
            historical_max = max(
                (agg.get(metric_key, 0.0) for agg in aggregates),
                default=0.0,
            )

            for milestone_name, milestone_value in milestones.items():
                if milestone_value <= historical_max:
                    continue
                for proj_point in projection['projected_periods']:
                    if proj_point['period_offset'] <= gap_periods:
                        continue
                    if abs(proj_point['projected_value'] - milestone_value) < 2.0:
                        ms = QScatterSeries()
                        ms.setName(self._tr_milestone(milestone_name))
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

        goal_targets = self._render_goals(
            now=now,
            historical_value=historical_data[-1],
            projection=projection,
            anchor_date=anchor_date,
            gap_periods=gap_periods,
            period_type=period_type,
        )

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
            for target_dt, _ in goal_targets:
                if target_dt > max_future:
                    max_future = target_dt
            axis_x.setRange(min_date, QDateTime.fromSecsSinceEpoch(int(max_future.timestamp())))

        max_dist = max(historical_data) if historical_data else 10
        if projection.get('has_projection'):
            max_dist = max(max_dist, max(p['projected_value'] for p in projection['projected_periods']))
        if goal_targets:
            max_dist = max(max_dist, *(g[1] for g in goal_targets))
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
