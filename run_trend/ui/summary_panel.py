"""
Summary panel widget showing key performance indicators.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFrame
from PySide6.QtCore import Qt
from datetime import datetime

from .help_label import make_help_icon
from ..analytics.training_score import TrainingScoreCalculator


def _row_with_help(label: QLabel, tooltip: str) -> QHBoxLayout:
    """Wrap a metric label with a trailing '?' help-icon in a horizontal row."""
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.addWidget(label)
    row.addWidget(make_help_icon(tooltip))
    row.addStretch()
    return row


class SummaryPanel(QWidget):
    """Summary panel widget displaying KPIs."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title = QLabel(self.tr("Training Summary"))
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Overall stats group
        overall_group = QGroupBox(self.tr("Overall Statistics"))
        overall_layout = QVBoxLayout()

        self.total_runs_label = QLabel(self.tr("Total Runs: -"))
        self.total_distance_label = QLabel(self.tr("Total Distance: -"))

        overall_layout.addWidget(self.total_runs_label)
        overall_layout.addWidget(self.total_distance_label)
        overall_group.setLayout(overall_layout)
        layout.addWidget(overall_group)

        # Current period group
        current_group = QGroupBox(self.tr("Current Period"))
        current_layout = QVBoxLayout()

        self.current_distance_label = QLabel(self.tr("Avg Distance: -"))
        self.current_pace_label = QLabel(self.tr("Avg Pace: -"))
        self.consistency_label = QLabel(self.tr("Active Days: -"))

        current_layout.addWidget(self.current_distance_label)
        current_layout.addLayout(_row_with_help(
            self.current_pace_label,
            self.tr(
                "Pace = minutes per kilometre.\n\n"
                "Distance-weighted average across this period: longer runs "
                "count more than short ones. Lower pace = faster running."
            ),
        ))
        current_layout.addLayout(_row_with_help(
            self.consistency_label,
            self.tr(
                "Active Days / Consistency Ratio.\n\n"
                "Number of distinct days with at least one run, divided by "
                "the days in this period. 50% means you ran on half the "
                "days — higher = more regular training."
            ),
        ))
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Heart rate group
        hr_group = QGroupBox(self.tr("Heart Rate"))
        hr_layout = QVBoxLayout()

        self.avg_hr_label = QLabel(self.tr("Avg HR: -"))
        self.max_hr_label = QLabel(self.tr("Max HR: -"))
        self.efficiency_label = QLabel(self.tr("Efficiency: -"))

        # HRmax suggestion (hidden by default)
        self.hrmax_suggestion_label = QLabel("")
        self.hrmax_suggestion_label.setWordWrap(True)
        self.hrmax_suggestion_label.setStyleSheet("color: orange; font-size: 10px; margin-top: 5px;")
        self.hrmax_suggestion_label.setVisible(False)

        hr_layout.addWidget(self.avg_hr_label)
        hr_layout.addWidget(self.max_hr_label)
        hr_layout.addLayout(_row_with_help(
            self.efficiency_label,
            self.tr(
                "Efficiency Factor (EF).\n\n"
                "Formula: pace (m/s) ÷ heart-rate (bpm), shown ×1000.\n"
                "Higher EF = same pace at lower HR = better aerobic fitness.\n"
                "Needs HR-sensor data."
            ),
        ))
        hr_layout.addWidget(self.hrmax_suggestion_label)
        hr_group.setLayout(hr_layout)
        layout.addWidget(hr_group)

        # Training score group
        score_group = QGroupBox(self.tr("Training Status"))
        score_layout = QVBoxLayout()

        self.score_label = QLabel(self.tr("Score: -"))
        self.score_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        score_layout.addLayout(_row_with_help(
            self.score_label,
            self.tr(
                "Training Score (0-100).\n\n"
                "Composite of recent training consistency, weekly distance, "
                "and aerobic efficiency.\n\n"
                "Typical ranges:\n"
                "  • 0-29  red   – minimal training\n"
                "  • 30-59 amber – building up\n"
                "  • 60-79 green – good\n"
                "  • 80+   green – strong"
            ),
        ))

        # Score breakdown — shows how each weighted component contributes
        # so users can see what to improve to raise the score.
        breakdown_label = QLabel(self.tr("Breakdown:"))
        breakdown_label.setStyleSheet("font-size: 10px; color: gray; margin-top: 4px;")
        score_layout.addWidget(breakdown_label)

        self.score_distance_label = QLabel(self.tr("Distance: -"))
        self.score_distance_label.setStyleSheet("font-size: 11px;")
        score_layout.addLayout(_row_with_help(
            self.score_distance_label,
            self.tr(
                "Distance contribution to the training score.\n\n"
                "Compares your period distance to a rolling baseline.\n"
                "Increase weekly distance sustainably to raise this value."
            ),
        ))

        self.score_frequency_label = QLabel(self.tr("Frequency: -"))
        self.score_frequency_label.setStyleSheet("font-size: 11px;")
        score_layout.addLayout(_row_with_help(
            self.score_frequency_label,
            self.tr(
                "Frequency contribution to the training score.\n\n"
                "Compares the number of runs in this period to a rolling baseline.\n"
                "Run more often to raise this value."
            ),
        ))

        self.score_pace_label = QLabel(self.tr("Pace: -"))
        self.score_pace_label.setStyleSheet("font-size: 11px;")
        score_layout.addLayout(_row_with_help(
            self.score_pace_label,
            self.tr(
                "Pace contribution to the training score.\n\n"
                "Compares your weighted average pace to a rolling baseline.\n"
                "Faster pace at the same effort raises this value."
            ),
        ))

        self.score_efficiency_label = QLabel(self.tr("Efficiency: -"))
        self.score_efficiency_label.setStyleSheet("font-size: 11px;")
        score_layout.addLayout(_row_with_help(
            self.score_efficiency_label,
            self.tr(
                "Efficiency contribution to the training score.\n\n"
                "Based on Efficiency Factor (pace ÷ HR). Needs heart-rate data.\n"
                "Same pace at lower HR = better aerobic fitness raises this value."
            ),
        ))

        score_group.setLayout(score_layout)
        layout.addWidget(score_group)

        # Training Load group (ACWR)
        load_group = QGroupBox(self.tr("Training Load (ACWR)"))
        load_layout = QVBoxLayout()

        self.load_score_label = QLabel(self.tr("Load: -"))
        self.load_score_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.load_status_label = QLabel(self.tr("Status: -"))
        self.load_status_label.setStyleSheet("font-size: 10px;")

        # Warning label (hidden by default)
        self.load_warning_label = QLabel("")
        self.load_warning_label.setWordWrap(True)
        self.load_warning_label.setStyleSheet("color: orange; font-size: 10px; margin-top: 5px;")
        self.load_warning_label.setVisible(False)

        load_layout.addLayout(_row_with_help(
            self.load_score_label,
            self.tr(
                "ACWR — Acute:Chronic Workload Ratio.\n\n"
                "Formula: TRIMP of last 7 days ÷ average TRIMP of last 28 days.\n"
                "TRIMP (Banister, 1991) = duration × HR-zone intensity.\n\n"
                "Sweet-spot: 0.8–1.3 (sustainable progression).\n"
                "Caution:    1.3–1.5 (monitor recovery).\n"
                "Danger:     ≥1.5    (elevated injury risk)."
            ),
        ))
        load_layout.addWidget(self.load_status_label)
        load_layout.addWidget(self.load_warning_label)
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)

        # Projection group
        projection_group = QGroupBox(self.tr("Marathon Milestone"))
        projection_layout = QVBoxLayout()

        self.milestone_label = QLabel(self.tr("Estimated Date: -"))

        projection_layout.addWidget(self.milestone_label)
        projection_group.setLayout(projection_layout)
        layout.addWidget(projection_group)

        # Race predictions group
        race_group = QGroupBox(self.tr("Race Time Predictions ⚠️"))
        race_layout = QVBoxLayout()

        self.race_5k_label = QLabel(self.tr("5K: -"))
        self.race_10k_label = QLabel(self.tr("10K: -"))
        self.race_half_label = QLabel(self.tr("Half: -"))
        self.race_marathon_label = QLabel(self.tr("Marathon: -"))

        self.race_info_label = QLabel(self.tr("Based on Easy Run pace (HR zones)"))
        self.race_info_label.setStyleSheet("color: gray; font-size: 9px;")
        self.race_info_label.setWordWrap(True)

        race_layout.addLayout(_row_with_help(
            self.race_5k_label,
            self.tr(
                "Race-Time Predictor.\n\n"
                "Predicts 5K / 10K / Half / Marathon times from your easy-run "
                "pace using the McMillan formula and your HR zones.\n\n"
                "⚠ Only an estimate — actual race performance depends on "
                "tapering, course, weather, and pacing strategy."
            ),
        ))
        race_layout.addWidget(self.race_10k_label)
        race_layout.addWidget(self.race_half_label)
        race_layout.addWidget(self.race_marathon_label)
        race_layout.addWidget(self.race_info_label)
        race_group.setLayout(race_layout)
        layout.addWidget(race_group)

        # Add stretch to push everything to the top
        layout.addStretch()

    def _set_breakdown_label(self, label: QLabel, name: str, contribution: dict):
        """Render one breakdown row as 'Name: contribution / max'."""
        if not contribution.get('has_data', False):
            label.setText(self.tr("{}: not available").format(name))
            return
        label.setText(
            self.tr("{}: {:.1f} / {:.0f}").format(
                name, contribution['contribution'], contribution['max']
            )
        )

    def update_summary(self, data: dict):
        """
        Update summary panel with new data.

        Args:
            data: Dictionary with summary statistics
        """
        # Overall stats
        total_runs = data.get('total_runs', 0)
        total_distance = data.get('total_distance', 0)

        self.total_runs_label.setText(self.tr("Total Runs: {}").format(total_runs))
        self.total_distance_label.setText(self.tr("Total Distance: {:.1f} km").format(total_distance))

        # Current period
        current_distance = data.get('current_avg_distance', 0)
        current_pace = data.get('current_avg_pace', 0)
        is_complete = data.get('is_current_period_complete', True)

        # Add "(so far)" if period is incomplete
        if is_complete:
            self.current_distance_label.setText(self.tr("Period Distance: {:.1f} km").format(current_distance))
        else:
            self.current_distance_label.setText(self.tr("Period Distance: {:.1f} km (so far)").format(current_distance))

        if current_pace > 0:
            pace_min = int(current_pace)
            pace_sec = int((current_pace - pace_min) * 60)
            self.current_pace_label.setText(self.tr("Avg Pace: {}:{:02d} min/km").format(pace_min, pace_sec))
        else:
            self.current_pace_label.setText(self.tr("Avg Pace: -"))

        # Consistency (active days / days in period) — spec §6.2.
        # When the period is in progress, the consistency_ratio uses
        # full-period days as the denominator, which under-reports.
        # Tag the value as "(so far)" so it isn't misread.
        active_days = data.get('active_days')
        consistency = data.get('consistency_ratio')
        if active_days is not None and consistency is not None:
            if is_complete:
                self.consistency_label.setText(
                    self.tr("Active Days: {} ({:.0%})").format(active_days, consistency)
                )
            else:
                self.consistency_label.setText(
                    self.tr("Active Days: {} ({:.0%} so far)").format(active_days, consistency)
                )
        else:
            self.consistency_label.setText(self.tr("Active Days: -"))

        # Heart rate metrics
        avg_hr = data.get('current_avg_hr', 0)
        max_hr = data.get('lifetime_max_hr', 0)
        efficiency = data.get('current_efficiency', 0)

        if avg_hr > 0:
            self.avg_hr_label.setText(self.tr("Avg HR: {:.0f} bpm").format(avg_hr))
        else:
            self.avg_hr_label.setText(self.tr("Avg HR: No data"))

        if max_hr > 0:
            self.max_hr_label.setText(self.tr("Max HR: {:.0f} bpm").format(max_hr))
        else:
            self.max_hr_label.setText(self.tr("Max HR: No data"))

        if efficiency > 0:
            # Display efficiency factor in a readable format
            self.efficiency_label.setText(self.tr("Efficiency: {:.2f}").format(efficiency*1000))
        else:
            self.efficiency_label.setText(self.tr("Efficiency: No data"))

        # HRmax plausibility check
        hrmax_check = data.get('hrmax_check')
        if hrmax_check and not hrmax_check.get('is_plausible', True):
            suggested = hrmax_check.get('suggested_hrmax', 0)
            detected = hrmax_check.get('detected_hrmax', 0)
            self.hrmax_suggestion_label.setText(
                self.tr("⚠ Detected HRmax ({:.0f} bpm) may be too low. "
                        "Consider setting manual HRmax to ~{} bpm in Settings.").format(detected, suggested)
            )
            self.hrmax_suggestion_label.setVisible(True)
        else:
            self.hrmax_suggestion_label.setVisible(False)

        # Training score. If main_window fell back to the last complete
        # period (so an in-progress current period doesn't drag the
        # breakdown), tell the user — otherwise "Frequency 3.7/20" reads
        # like an error rather than "your current week isn't finished yet".
        score = data.get('current_score', 0)
        uses_last_complete = bool(data.get('score_uses_last_complete', False))
        if uses_last_complete:
            self.score_label.setText(
                self.tr("Score: {:.1f}  (last complete period)").format(score)
            )
        else:
            self.score_label.setText(self.tr("Score: {:.1f}").format(score))

        # Set color based on score
        if score < 30:
            color = "#e74c3c"  # Red
        elif score < 60:
            color = "#f39c12"  # Orange
        elif score < 80:
            color = "#27ae60"  # Green
        else:
            color = "#2ecc71"  # Bright green

        self.score_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")

        # Score breakdown
        components = data.get('score_components')
        contributions = TrainingScoreCalculator.get_score_contributions(components or {})
        if contributions:
            self._set_breakdown_label(self.score_distance_label, self.tr("Distance"),
                                      contributions['distance'])
            self._set_breakdown_label(self.score_frequency_label, self.tr("Frequency"),
                                      contributions['frequency'])
            self._set_breakdown_label(self.score_pace_label, self.tr("Pace"),
                                      contributions['pace'])
            self._set_breakdown_label(self.score_efficiency_label, self.tr("Efficiency"),
                                      contributions['efficiency'])
        else:
            self.score_distance_label.setText(self.tr("Distance: -"))
            self.score_frequency_label.setText(self.tr("Frequency: -"))
            self.score_pace_label.setText(self.tr("Pace: -"))
            self.score_efficiency_label.setText(self.tr("Efficiency: -"))

        # Marathon milestone
        marathon_estimate = data.get('marathon_estimate')
        if marathon_estimate and marathon_estimate.get('reachable'):
            if marathon_estimate.get('reached'):
                self.milestone_label.setText(self.tr("Milestone Reached!"))
            else:
                est_date = marathon_estimate.get('estimated_date')
                if est_date:
                    date_obj = datetime.fromisoformat(est_date)
                    self.milestone_label.setText(self.tr("Estimated: {}").format(date_obj.strftime('%Y-%m-%d')))
                else:
                    self.milestone_label.setText(self.tr("Calculating..."))
        else:
            self.milestone_label.setText(self.tr("Keep training!"))

        # Race predictions
        race_predictions = data.get('race_predictions')
        if race_predictions and race_predictions.get('has_prediction'):
            predictions = race_predictions['predictions']

            # 5K
            pred_5k = predictions.get('5K', {})
            time_5k = pred_5k.get('total_time_formatted', '-')
            pace_5k = pred_5k.get('pace_min_per_km', 0)
            if pace_5k > 0:
                pace_min = int(pace_5k)
                pace_sec = int((pace_5k - pace_min) * 60)
                self.race_5k_label.setText(self.tr("5K: {} ({}:{:02d}/km)").format(time_5k, pace_min, pace_sec))
            else:
                self.race_5k_label.setText(self.tr("5K: {}").format(time_5k))

            # 10K
            pred_10k = predictions.get('10K', {})
            time_10k = pred_10k.get('total_time_formatted', '-')
            pace_10k = pred_10k.get('pace_min_per_km', 0)
            if pace_10k > 0:
                pace_min = int(pace_10k)
                pace_sec = int((pace_10k - pace_min) * 60)
                self.race_10k_label.setText(self.tr("10K: {} ({}:{:02d}/km)").format(time_10k, pace_min, pace_sec))
            else:
                self.race_10k_label.setText(self.tr("10K: {}").format(time_10k))

            # Half Marathon
            pred_half = predictions.get('Half Marathon', {})
            time_half = pred_half.get('total_time_formatted', '-')
            pace_half = pred_half.get('pace_min_per_km', 0)
            if pace_half > 0:
                pace_min = int(pace_half)
                pace_sec = int((pace_half - pace_min) * 60)
                self.race_half_label.setText(self.tr("Half: {} ({}:{:02d}/km)").format(time_half, pace_min, pace_sec))
            else:
                self.race_half_label.setText(self.tr("Half: {}").format(time_half))

            # Marathon
            pred_marathon = predictions.get('Marathon', {})
            time_marathon = pred_marathon.get('total_time_formatted', '-')
            pace_marathon = pred_marathon.get('pace_min_per_km', 0)
            if pace_marathon > 0:
                pace_min = int(pace_marathon)
                pace_sec = int((pace_marathon - pace_min) * 60)
                self.race_marathon_label.setText(self.tr("Marathon: {} ({}:{:02d}/km)").format(time_marathon, pace_min, pace_sec))
            else:
                self.race_marathon_label.setText(self.tr("Marathon: {}").format(time_marathon))

            # Update info text
            easy_runs = race_predictions.get('easy_runs_count', 0)
            easy_pace = race_predictions.get('median_easy_pace_formatted', '-')
            self.race_info_label.setText(
                self.tr("Based on {} easy runs (pace: {}/km). "
                        "McMillan formula with HR zones.").format(easy_runs, easy_pace)
            )
        else:
            # No predictions available
            self.race_5k_label.setText(self.tr("5K: Need HR data"))
            self.race_10k_label.setText(self.tr("10K: Need HR data"))
            self.race_half_label.setText(self.tr("Half: Need HR data"))
            self.race_marathon_label.setText(self.tr("Marathon: Need HR data"))

            reason = race_predictions.get('message', self.tr('Insufficient data')) if race_predictions else self.tr('No data')
            self.race_info_label.setText(self.tr("⚠️ {}").format(reason))

        # Training Load (ACWR)
        load_data = data.get('training_load')
        if load_data and load_data.get('has_load'):
            load_score = load_data['training_load']
            status = load_data.get('status', 'unknown')
            message = load_data.get('message', '')

            self.load_score_label.setText(self.tr("Load: {:.0f}").format(load_score))

            # Color coding
            if load_score >= 90:
                color = "#e74c3c"  # Red
                status_text = self.tr("DANGER")
            elif load_score >= 80:
                color = "#e67e22"  # Orange
                status_text = self.tr("WARNING")
            elif load_score >= 70:
                color = "#f39c12"  # Yellow
                status_text = self.tr("CAUTION")
            elif load_score >= 40:
                color = "#27ae60"  # Green
                status_text = self.tr("SAFE")
            else:
                color = "#3498db"  # Blue
                status_text = self.tr("LOW")

            self.load_score_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
            self.load_status_label.setText(self.tr("Status: {}").format(status_text))

            # Show warning if score >= 80
            if load_score >= 80:
                self.load_warning_label.setText(message)
                self.load_warning_label.setVisible(True)
            else:
                self.load_warning_label.setVisible(False)
        else:
            self.load_score_label.setText(self.tr("Load: -"))
            self.load_status_label.setText(self.tr("Status: Need 5+ weeks"))
            self.load_warning_label.setVisible(False)
