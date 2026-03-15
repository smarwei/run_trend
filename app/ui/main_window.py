"""
Main application window.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QPushButton, QLabel, QComboBox, QDateEdit,
    QStatusBar, QTabWidget, QMessageBox, QProgressDialog, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, QThread, QTimer, Signal
from PySide6.QtGui import QAction
from datetime import datetime
from typing import Optional

from ..storage.database import Database
from ..strava.simple_auth import SimpleStravaAuth
from ..strava.client import StravaClient
from ..sync.sync_manager import SyncManager
from ..settings.config import AppSettings
from ..analytics.aggregator import ActivityAggregator
from ..analytics.training_score import TrainingScoreCalculator
from ..analytics.smoothing import Smoother
from ..analytics.race_predictor import RacePredictor
from ..projection.forecaster import Forecaster

from .summary_panel import SummaryPanel
from .settings_dialog import SettingsDialog
from .manual_dialog import ManualDialog
from .about_dialog import AboutDialog
from ..charts.distance_chart import DistanceChart
from ..charts.pace_chart import PaceChart
from ..charts.frequency_chart import FrequencyChart
from ..charts.score_chart import ScoreChart
from ..charts.projection_chart import ProjectionChart
from ..charts.longest_run_chart import LongestRunChart
from ..charts.avg_distance_chart import AvgDistanceChart
from ..charts.structure_overview_chart import StructureOverviewChart
from ..charts.heartrate_chart import HeartRateChart


class SyncThread(QThread):
    """Thread for running sync operations."""
    progress = Signal(int, int, str)
    finished = Signal(dict)

    def __init__(self, db_path, client, sync_type, start_date=None):
        super().__init__()
        self.db_path = db_path
        self.client = client
        self.sync_type = sync_type
        self.start_date = start_date

    def run(self):
        # Create database connection in this thread
        from ..storage.database import Database
        from ..sync.sync_manager import SyncManager

        db = Database(self.db_path)
        sync_manager = SyncManager(db, self.client)

        try:
            if self.sync_type == 'initial':
                stats = sync_manager.initial_sync(
                    self.start_date,
                    progress_callback=self.progress.emit
                )
            else:
                stats = sync_manager.incremental_sync(
                    progress_callback=self.progress.emit
                )
            self.finished.emit(stats)
        finally:
            db.close()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Running Progress Tracker")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize components
        self.settings = AppSettings()
        self.db = Database()
        self.auth: Optional[SimpleStravaAuth] = None
        self.client: Optional[StravaClient] = None
        self.sync_manager: Optional[SyncManager] = None

        # Data
        self.activities = []
        self.aggregates = []
        self.current_period = 'week'

        # Setup UI
        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        # Set up projection chart settings callback
        self.projection_chart.settings_callback = self.settings.set

        # Check authentication
        self._check_authentication()

        # Restore UI settings
        self._restore_ui_settings()

    def _setup_ui(self):
        """Set up the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Left panel - Summary
        self.summary_panel = SummaryPanel()
        main_layout.addWidget(self.summary_panel, stretch=1)

        # Right panel - Charts
        self.tab_widget = QTabWidget()

        # Create charts
        self.distance_chart = DistanceChart()
        self.pace_chart = PaceChart()
        self.frequency_chart = FrequencyChart()
        self.score_chart = ScoreChart()
        self.projection_chart = ProjectionChart()
        self.longest_run_chart = LongestRunChart()
        self.avg_distance_chart = AvgDistanceChart()
        self.structure_overview_chart = StructureOverviewChart()
        self.heartrate_chart = HeartRateChart()

        # Tab 1: Overview - Total Load Metrics
        overview_tab = QTabWidget()
        overview_tab.addTab(self.distance_chart, "Distance")
        overview_tab.addTab(self.pace_chart, "Pace/Speed")
        overview_tab.addTab(self.frequency_chart, "Frequency")
        self.tab_widget.addTab(overview_tab, "Overview")

        # Tab 2: Heart Rate Analysis
        self.tab_widget.addTab(self.heartrate_chart, "Heart Rate")

        # Tab 3: Endurance - Training Structure Metrics
        endurance_tab = QTabWidget()
        endurance_tab.addTab(self.longest_run_chart, "Longest Run")
        endurance_tab.addTab(self.avg_distance_chart, "Avg Distance/Run")
        self.tab_widget.addTab(endurance_tab, "Endurance")

        # Tab 4: Structure - Comparative Overview
        self.tab_widget.addTab(self.structure_overview_chart, "Structure")

        # Tab 5: Training Score
        self.tab_widget.addTab(self.score_chart, "Score")

        # Tab 6: Projection
        self.tab_widget.addTab(self.projection_chart, "Projection")

        main_layout.addWidget(self.tab_widget, stretch=3)

    def _setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Settings button (left)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)

        toolbar.addSeparator()

        # Start date selector
        toolbar.addWidget(QLabel("Start Date:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        # Default to a very early date to capture all activities (Strava founded 2009)
        self.start_date_edit.setDate(QDate(2000, 1, 1))
        self.start_date_edit.dateChanged.connect(self._on_start_date_changed)
        toolbar.addWidget(self.start_date_edit)

        toolbar.addSeparator()

        # Period selector
        toolbar.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Week", "Month"])
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        toolbar.addWidget(self.period_combo)

        toolbar.addSeparator()

        # Metric selector
        toolbar.addWidget(QLabel("Metric:"))
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["Pace", "Speed"])
        self.metric_combo.currentTextChanged.connect(self._on_metric_changed)
        toolbar.addWidget(self.metric_combo)

        toolbar.addSeparator()

        # Smoothing selector
        toolbar.addWidget(QLabel("Smoothing:"))
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.addItems(["Off", "Light", "Medium", "Strong"])
        self.smoothing_combo.setCurrentText("Medium")
        self.smoothing_combo.currentTextChanged.connect(self._on_smoothing_changed)
        toolbar.addWidget(self.smoothing_combo)

        # Spacer to push Help and About to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Help button (right)
        help_action = QAction("Help", self)
        help_action.triggered.connect(self._show_manual)
        toolbar.addAction(help_action)

        # About button (far right)
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        toolbar.addAction(about_action)


    def _setup_statusbar(self):
        """Set up the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    def _connect_signals(self):
        """Connect signals and slots."""
        pass

    def _check_authentication(self):
        """Check if user is already authenticated."""
        # Load access token from settings
        self.auth = SimpleStravaAuth(self.settings)

        if self.auth.is_authenticated():
            self._setup_strava_client()
            self.statusbar.showMessage("Connected to Strava")
            self._load_data()

            # Auto-sync on startup (silent incremental sync)
            activity_count = self.db.get_activity_count()
            if activity_count > 0:
                # Only do incremental sync if we already have data
                self._run_silent_sync()
        else:
            # Not authenticated - open settings dialog on first start
            self.statusbar.showMessage("Not connected - Please configure Strava connection")
            # Use QTimer to open settings after main window is shown
            QTimer.singleShot(100, self._show_settings)

    def _restore_ui_settings(self):
        """Restore UI settings from previous session."""
        # Restore start date
        start_date_str = self.settings.get('ui_start_date')
        if start_date_str:
            try:
                year, month, day = map(int, start_date_str.split('-'))
                self.start_date_edit.setDate(QDate(year, month, day))
            except (ValueError, AttributeError):
                pass  # Use default if parsing fails

        # Restore period
        period = self.settings.get('ui_period', 'Week')
        index = self.period_combo.findText(period, Qt.MatchFixedString)
        if index >= 0:
            self.period_combo.setCurrentIndex(index)

        # Restore metric
        metric = self.settings.get('ui_metric', 'Pace')
        index = self.metric_combo.findText(metric, Qt.MatchFixedString)
        if index >= 0:
            self.metric_combo.setCurrentIndex(index)

        # Restore smoothing
        smoothing = self.settings.get('ui_smoothing', 'Medium')
        index = self.smoothing_combo.findText(smoothing, Qt.MatchFixedString)
        if index >= 0:
            self.smoothing_combo.setCurrentIndex(index)

        # Restore projection settings
        projection_mode = self.settings.get('ui_projection_mode', 'Volume (Total Distance)')
        index = self.projection_chart.mode_combo.findText(projection_mode, Qt.MatchFixedString)
        if index >= 0:
            self.projection_chart.mode_combo.setCurrentIndex(index)

        projection_periods = self.settings.get('ui_projection_periods', 12)
        self.projection_chart.periods_spinbox.setValue(projection_periods)

    def _authenticate_strava(self):
        """Authenticate with Strava."""
        if self.auth and self.auth.is_authenticated():
            # Disconnect
            reply = QMessageBox.question(
                self, "Disconnect",
                "Do you want to disconnect from Strava?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.auth.revoke()
                self.auth = None
                self.client = None
                self.sync_manager = None
                self.statusbar.showMessage("Disconnected from Strava")
            return

        # Start OAuth flow
        client_id = self.settings.get('strava_client_id')
        client_secret = self.settings.get('strava_client_secret')

        if not client_id or not client_secret:
            # Ask user to configure API credentials first
            reply = QMessageBox.information(
                self, "Strava API Configuration Required",
                "To connect to Strava, you first need to configure your API credentials.\n\n"
                "1. Go to Settings\n"
                "2. Enter your Client ID and Client Secret\n"
                "3. Click 'Connect to Strava' again\n\n"
                "Get your credentials from:\n"
                "https://www.strava.com/settings/api",
                QMessageBox.Ok
            )
            return

        # Create auth instance if not exists
        if not self.auth:
            self.auth = SimpleStravaAuth(self.settings)

        # Show progress message
        self.statusbar.showMessage("Opening browser for Strava authorization...")

        # Start OAuth flow (this will block until complete)
        if self.auth.authorize(client_id, client_secret):
            self._setup_strava_client()
            self.statusbar.showMessage("Successfully connected to Strava!")

            # Auto-sync after successful connection
            reply = QMessageBox.question(
                self, "Sync Activities",
                "Successfully connected to Strava!\n\n"
                "Do you want to sync your activities now?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self._sync_activities()
        else:
            self.statusbar.showMessage("Failed to connect to Strava")
            QMessageBox.warning(
                self, "Authorization Failed",
                "Failed to authorize with Strava.\n\n"
                "Please try again or check your API credentials in Settings."
            )

    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.settings, self, main_window=self)
        if dialog.exec():
            # Settings were saved, check if we should reconnect
            if self.auth:
                # Reload token from settings
                self.auth._load_token()
                if self.auth.is_authenticated():
                    self._setup_strava_client()
                    self.statusbar.showMessage("Reconnected to Strava with new settings")

    def _show_manual(self):
        """Show manual/help dialog."""
        dialog = ManualDialog(self)
        dialog.exec()

    def _show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _setup_strava_client(self):
        """Set up Strava client and sync manager."""
        self.client = StravaClient(self.auth)
        self.sync_manager = SyncManager(self.db, self.client)

    def _sync_activities(self):
        """Sync activities from Strava."""
        if not self.sync_manager:
            return

        # Check if this is initial sync
        activity_count = self.db.get_activity_count()

        if activity_count == 0:
            # Initial sync
            start_date_q = self.start_date_edit.date()
            start_date = datetime(start_date_q.year(), start_date_q.month(), start_date_q.day())

            self._run_sync('initial', start_date)
        else:
            # Incremental sync
            self._run_sync('incremental')

    def _run_sync(self, sync_type, start_date=None):
        """Run sync in background thread."""
        # Create progress dialog
        self.progress_dialog = QProgressDialog("Syncing activities...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)

        # Create and start sync thread with db_path instead of sync_manager
        self.sync_thread = SyncThread(self.db.db_path, self.client, sync_type, start_date)
        self.sync_thread.progress.connect(self._on_sync_progress)
        self.sync_thread.finished.connect(self._on_sync_finished)
        self.sync_thread.start()

    def _run_silent_sync(self):
        """Run silent incremental sync in background (no dialogs)."""
        # Create and start sync thread for incremental sync only
        self.silent_sync_thread = SyncThread(self.db.db_path, self.client, 'incremental', None)
        self.silent_sync_thread.finished.connect(self._on_silent_sync_finished)
        self.silent_sync_thread.start()
        self.statusbar.showMessage("Checking for new activities...")

    def _on_sync_progress(self, current, total, message):
        """Handle sync progress updates."""
        if total > 0:
            self.progress_dialog.setMaximum(total)
            self.progress_dialog.setValue(current)
        self.progress_dialog.setLabelText(message)

    def _on_sync_finished(self, stats):
        """Handle sync completion."""
        self.progress_dialog.close()

        message = f"Sync completed:\n"
        message += f"Fetched: {stats['fetched']}\n"
        message += f"Imported: {stats['imported']}\n"
        message += f"Updated: {stats['updated']}\n"
        if stats['errors'] > 0:
            message += f"Errors: {stats['errors']}\n"

        QMessageBox.information(self, "Sync Complete", message)

        # Refresh data
        self._load_data()

    def _on_silent_sync_finished(self, stats):
        """Handle silent sync completion (no dialog, only status message)."""
        # Only show message if new activities were found or errors occurred
        if stats['imported'] > 0 or stats['updated'] > 0:
            self.statusbar.showMessage(
                f"Sync complete: {stats['imported']} new, {stats['updated']} updated"
            )
            # Refresh data to show new activities
            self._load_data()
        elif stats['errors'] > 0:
            self.statusbar.showMessage(f"Sync completed with {stats['errors']} errors")
        else:
            self.statusbar.showMessage("No new activities found")
            # Clear message after 3 seconds
            QTimer.singleShot(3000, lambda: self.statusbar.showMessage("Connected to Strava"))

    def _load_data(self):
        """Load activities from database and refresh UI."""
        # Get start date from widget
        start_date_q = self.start_date_edit.date()
        start_date_str = f"{start_date_q.year()}-{start_date_q.month():02d}-{start_date_q.day():02d}"

        # Load activities from start date onwards
        self.activities = self.db.get_activities_since(start_date_str)

        # Aggregate data
        self._refresh_data()

    def _refresh_data(self):
        """Refresh aggregations and charts."""
        if not self.activities:
            return

        # Aggregate by current period
        if self.current_period == 'week':
            self.aggregates = ActivityAggregator.aggregate_by_week(self.activities)
        else:
            self.aggregates = ActivityAggregator.aggregate_by_month(self.activities)

        # Calculate training scores
        self.aggregates = TrainingScoreCalculator.calculate_scores(self.aggregates)

        # Update summary panel
        self._update_summary()

        # Update charts
        self._update_charts()

    def _update_summary(self):
        """Update summary panel with current data."""
        if not self.aggregates:
            return

        total_runs = sum(a['num_runs'] for a in self.aggregates)
        total_distance = sum(a['total_distance_km'] for a in self.aggregates)

        latest_agg = self.aggregates[-1]
        current_avg_distance = latest_agg['total_distance_km']
        current_avg_pace = latest_agg['weighted_avg_pace_min_per_km']
        current_score = latest_agg.get('training_score', 0)

        # Heart rate metrics
        current_avg_hr = latest_agg.get('avg_heartrate', 0)
        current_efficiency = latest_agg.get('efficiency_factor', 0)

        # Lifetime max HR across all aggregates
        max_hr_values = [a.get('max_heartrate', 0) for a in self.aggregates if a.get('max_heartrate', 0) > 0]
        lifetime_max_hr = max(max_hr_values) if max_hr_values else 0

        # Get milestone estimate (Long Run based, not volume based)
        milestone_estimates = Forecaster.get_milestone_estimates(
            self.aggregates,
            self.current_period,
            metric_key='longest_run_km'  # Use Long Run progression, not volume
        )
        marathon_estimate = milestone_estimates.get('Marathon Ready')

        # Get manual HRmax from settings (if configured)
        manual_hrmax = self.settings.get('manual_hrmax', 0)

        # Determine which HRmax to display (manual takes priority)
        display_max_hr = manual_hrmax if manual_hrmax > 0 else lifetime_max_hr

        # Convert activities to format expected by RacePredictor
        converted_activities = []
        if self.activities:
            for activity in self.activities:
                distance_m = activity.get('distance', 0)
                moving_time_s = activity.get('moving_time', 0)

                if distance_m > 0 and moving_time_s > 0:
                    distance_km = distance_m / 1000
                    pace_s_per_m = moving_time_s / distance_m
                    pace_min_per_km = pace_s_per_m * 1000 / 60

                    converted_activities.append({
                        'distance_km': distance_km,
                        'pace_min_per_km': pace_min_per_km,
                        'average_heartrate': activity.get('average_heartrate'),
                        'start_date': activity.get('start_date')
                    })

        # Check HRmax plausibility (only if manual HRmax not set)
        hrmax_check = None
        if manual_hrmax == 0 and lifetime_max_hr > 0 and self.activities:
            # Only check plausibility if using auto-detected HRmax
            hrmax_check = RacePredictor.check_hrmax_plausibility(
                lifetime_max_hr,
                self.activities,
                converted_activities
            )

        # Estimate race times based on HR zones and training pace
        race_predictions = None
        if lifetime_max_hr > 0 and converted_activities:

            race_predictions = RacePredictor.estimate_race_times(
                converted_activities,
                lifetime_max_hr,
                current_efficiency,
                manual_hrmax=manual_hrmax
            )

        self.summary_panel.update_summary({
            'total_runs': total_runs,
            'total_distance': total_distance,
            'current_avg_distance': current_avg_distance,
            'current_avg_pace': current_avg_pace,
            'current_score': current_score,
            'current_avg_hr': current_avg_hr,
            'lifetime_max_hr': display_max_hr,  # Use manual if set, else detected
            'current_efficiency': current_efficiency,
            'marathon_estimate': marathon_estimate,
            'race_predictions': race_predictions,
            'hrmax_check': hrmax_check
        })

    def _update_charts(self):
        """Update all charts."""
        smoothing_strength = self.smoothing_combo.currentText().lower()

        self.distance_chart.update_chart(self.aggregates, smoothing_strength)
        self.pace_chart.update_chart(self.aggregates, smoothing_strength,
                                     self.metric_combo.currentText().lower())
        self.frequency_chart.update_chart(self.aggregates, smoothing_strength)
        self.heartrate_chart.update_chart(self.aggregates, smoothing_strength)
        self.longest_run_chart.update_chart(self.aggregates, smoothing_strength)
        self.avg_distance_chart.update_chart(self.aggregates, smoothing_strength)
        self.structure_overview_chart.update_chart(self.aggregates, smoothing_strength)
        self.score_chart.update_chart(self.aggregates, smoothing_strength)
        self.projection_chart.update_chart(self.aggregates, self.current_period)

    def _on_start_date_changed(self):
        """Handle start date change."""
        # Save to settings
        date = self.start_date_edit.date()
        date_str = f"{date.year()}-{date.month():02d}-{date.day():02d}"
        self.settings.set('ui_start_date', date_str)

        self._load_data()

    def _on_period_changed(self, text):
        """Handle period selection change."""
        # Save to settings
        self.settings.set('ui_period', text)

        self.current_period = text.lower()
        self._refresh_data()

    def _on_metric_changed(self, text):
        """Handle metric selection change."""
        # Save to settings
        self.settings.set('ui_metric', text)

        self._update_charts()

    def _on_smoothing_changed(self, text):
        """Handle smoothing selection change."""
        # Save to settings
        self.settings.set('ui_smoothing', text)

        self._update_charts()
