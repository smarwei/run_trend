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
        title = QLabel("Training Summary")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Overall stats group
        overall_group = QGroupBox("Overall Statistics")
        overall_layout = QVBoxLayout()

        self.total_runs_label = QLabel("Total Runs: -")
        self.total_distance_label = QLabel("Total Distance: -")

        overall_layout.addWidget(self.total_runs_label)
        overall_layout.addWidget(self.total_distance_label)
        overall_group.setLayout(overall_layout)
        layout.addWidget(overall_group)

        # Current period group
        current_group = QGroupBox("Current Period")
        current_layout = QVBoxLayout()

        self.current_distance_label = QLabel("Avg Distance: -")
        self.current_pace_label = QLabel("Avg Pace: -")

        current_layout.addWidget(self.current_distance_label)
        current_layout.addWidget(self.current_pace_label)
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Training score group
        score_group = QGroupBox("Training Status")
        score_layout = QVBoxLayout()

        self.score_label = QLabel("Score: -")
        self.score_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        score_layout.addWidget(self.score_label)
        score_group.setLayout(score_layout)
        layout.addWidget(score_group)

        # Projection group
        projection_group = QGroupBox("Marathon Milestone")
        projection_layout = QVBoxLayout()

        self.milestone_label = QLabel("Estimated Date: -")

        projection_layout.addWidget(self.milestone_label)
        projection_group.setLayout(projection_layout)
        layout.addWidget(projection_group)

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

        self.total_runs_label.setText(f"Total Runs: {total_runs}")
        self.total_distance_label.setText(f"Total Distance: {total_distance:.1f} km")

        # Current period
        current_distance = data.get('current_avg_distance', 0)
        current_pace = data.get('current_avg_pace', 0)

        self.current_distance_label.setText(f"Period Distance: {current_distance:.1f} km")

        if current_pace > 0:
            pace_min = int(current_pace)
            pace_sec = int((current_pace - pace_min) * 60)
            self.current_pace_label.setText(f"Avg Pace: {pace_min}:{pace_sec:02d} min/km")
        else:
            self.current_pace_label.setText("Avg Pace: -")

        # Training score
        score = data.get('current_score', 0)
        self.score_label.setText(f"Score: {score:.1f}")

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
                self.milestone_label.setText("Milestone Reached!")
            else:
                est_date = marathon_estimate.get('estimated_date')
                if est_date:
                    date_obj = datetime.fromisoformat(est_date)
                    self.milestone_label.setText(f"Estimated: {date_obj.strftime('%Y-%m-%d')}")
                else:
                    self.milestone_label.setText("Calculating...")
        else:
            self.milestone_label.setText("Keep training!")
