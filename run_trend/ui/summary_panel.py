"""
Summary panel widget showing key performance indicators.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QFrame
from PySide6.QtCore import Qt
from datetime import datetime


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

        current_layout.addWidget(self.current_distance_label)
        current_layout.addWidget(self.current_pace_label)
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
        hr_layout.addWidget(self.efficiency_label)
        hr_layout.addWidget(self.hrmax_suggestion_label)
        hr_group.setLayout(hr_layout)
        layout.addWidget(hr_group)

        # Training score group
        score_group = QGroupBox(self.tr("Training Status"))
        score_layout = QVBoxLayout()

        self.score_label = QLabel(self.tr("Score: -"))
        self.score_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        score_layout.addWidget(self.score_label)
        score_group.setLayout(score_layout)
        layout.addWidget(score_group)

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

        race_layout.addWidget(self.race_5k_label)
        race_layout.addWidget(self.race_10k_label)
        race_layout.addWidget(self.race_half_label)
        race_layout.addWidget(self.race_marathon_label)
        race_layout.addWidget(self.race_info_label)
        race_group.setLayout(race_layout)
        layout.addWidget(race_group)

        # Add stretch to push everything to the top
        layout.addStretch()

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

        self.current_distance_label.setText(self.tr("Period Distance: {:.1f} km").format(current_distance))

        if current_pace > 0:
            pace_min = int(current_pace)
            pace_sec = int((current_pace - pace_min) * 60)
            self.current_pace_label.setText(self.tr("Avg Pace: {}:{:02d} min/km").format(pace_min, pace_sec))
        else:
            self.current_pace_label.setText(self.tr("Avg Pace: -"))

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

        # Training score
        score = data.get('current_score', 0)
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
