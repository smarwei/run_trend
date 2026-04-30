"""
Main application window.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QPushButton, QLabel, QComboBox, QDateEdit, QCheckBox,
    QStatusBar, QStyle, QTabWidget, QMessageBox, QProgressDialog, QSizePolicy,
    QFileDialog,
)
from PySide6.QtCore import Qt, QDate, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QIcon
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

from ..storage.database import Database
from ..strava.simple_auth import SimpleStravaAuth
from ..strava.client import StravaClient
from ..sync.sync_manager import SyncManager
from ..settings.config import AppSettings
from ..analytics.data_manager import DataManager
from ..analytics.smoothing import Smoother
from ..analytics.race_predictor import RacePredictor
from ..projection.forecaster import Forecaster
from ..io.exporter import export_activities_csv, default_csv_filename

from .summary_panel import SummaryPanel
from .settings_dialog import SettingsDialog
from .manual_dialog import ManualDialog
from .about_dialog import AboutDialog
from .onboarding_wizard import OnboardingWizard
from .race_dialog import RaceDialog
from .race_manager_dialog import RaceManagerDialog
from .goal_manager_dialog import GoalManagerDialog
from ..charts.distance_chart import DistanceChart
from ..charts.pace_chart import PaceChart
from ..charts.frequency_chart import FrequencyChart
from ..charts.score_chart import ScoreChart
from ..charts.projection_chart import ProjectionChart
from ..charts.endurance_chart import EnduranceChart
from ..charts.structure_overview_chart import StructureOverviewChart
from ..charts.heartrate_chart import HeartRateChart
from ..charts.hr_zone_chart import HrZoneChart
from ..analytics.hr_zone_service import HrZoneService
from ..charts.duration_chart import DurationChart
from ..charts.training_load_chart import TrainingLoadChart
from .runs_table import RunsTable
from ..charts.pace_distance_chart import PaceDistanceChart


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


class HrZoneFetchThread(QThread):
    """Fetch HR-streams for a list of activities and cache the resulting zones.

    Runs in its own thread so the UI stays responsive during the (potentially
    many) Strava API calls. Each iteration emits ``progress(current, total)``;
    callers refresh the chart on ``finished_signal``.
    """
    progress = Signal(int, int)
    finished_signal = Signal()

    def __init__(self, db_path, client, settings_snapshot, activity_ids):
        super().__init__()
        self._db_path = db_path
        self._client = client
        self._settings_snapshot = dict(settings_snapshot)
        self._activity_ids = list(activity_ids)
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        from ..storage.database import Database
        from ..analytics.hr_zone_service import HrZoneService

        class _DictSettings:
            def __init__(self, d):
                self._d = d

            def get(self, key, default=None):
                return self._d.get(key, default)

        db = Database(self._db_path)
        try:
            svc = HrZoneService(
                db,
                _DictSettings(self._settings_snapshot),
                lambda aid: self._client.get_activity_streams(aid),
            )
            total = len(self._activity_ids)
            for i, aid in enumerate(self._activity_ids):
                if self._cancel:
                    break
                try:
                    svc.get_zone_seconds(aid)
                except Exception:  # noqa: BLE001 — never let one bad call kill the loop
                    logger.exception("HR-zone fetch failed for activity %s", aid)
                self.progress.emit(i + 1, total)
        finally:
            db.close()
        self.finished_signal.emit()


class _StravaAuthThread(QThread):
    finished = Signal(bool)

    def __init__(self, auth, client_id, client_secret):
        super().__init__()
        self._auth = auth
        self._client_id = client_id
        self._client_secret = client_secret

    def run(self):
        result = self._auth.authorize(self._client_id, self._client_secret)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    """Main application window."""

    # Emitted after every Strava OAuth attempt (success/failure).
    # The onboarding wizard listens to this so it can update its connect
    # page without subscribing directly to the throw-away auth thread.
    auth_finished = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Running Progress Tracker"))
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
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()

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
        self.endurance_chart = EnduranceChart()
        self.structure_overview_chart = StructureOverviewChart()
        self.heartrate_chart = HeartRateChart()
        self.hr_zone_chart = HrZoneChart()
        self.duration_chart = DurationChart()
        self.training_load_chart = TrainingLoadChart()
        self.runs_table = RunsTable()
        self.pace_distance_chart = PaceDistanceChart()

        # Wire empty-state "Connect" buttons to the OAuth flow.
        for chart in self._all_charts():
            chart.connect_requested.connect(self._authenticate_strava)

        # Right-click "Mark as Race…" on a row opens the RaceDialog.
        self.runs_table.race_requested.connect(self._mark_activity_as_race)

        # Tab 1: Overview - Total Load Metrics
        overview_tab = QTabWidget()
        overview_tab.addTab(self.distance_chart, self.tr("Distance"))
        overview_tab.addTab(self.pace_chart, self.tr("Pace/Speed"))
        overview_tab.addTab(self.frequency_chart, self.tr("Frequency"))
        self.tab_widget.addTab(overview_tab, self.tr("Overview"))

        # Tab 2: Heart Rate Analysis
        self.tab_widget.addTab(self.heartrate_chart, self.tr("Heart Rate"))

        # Tab 2b: HR Zones — lazy-fetches streams the first time the user opens it.
        self._hr_zone_tab_index = self.tab_widget.addTab(
            self.hr_zone_chart, self.tr("HR Zones")
        )
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.hr_zone_fetch_thread: Optional[HrZoneFetchThread] = None
        self._hr_zone_autofetch_done = False

        # Tab 3: Endurance - Training Structure Metrics
        self.tab_widget.addTab(self.endurance_chart, self.tr("Endurance"))

        # Tab 4: Duration Analysis
        self.tab_widget.addTab(self.duration_chart, self.tr("Duration"))

        # Tab 5: Structure - Comparative Overview
        self.tab_widget.addTab(self.structure_overview_chart, self.tr("Structure"))

        # Tab 6: Training Score
        self.tab_widget.addTab(self.score_chart, self.tr("Score"))

        # Tab 7: Training Load (ACWR)
        self.tab_widget.addTab(self.training_load_chart, self.tr("Training Load"))

        # Tab 8: Projection
        self.tab_widget.addTab(self.projection_chart, self.tr("Projection"))

        # Tab 9: Runs — individual activity list and scatter plot
        runs_tab = QTabWidget()
        runs_tab.addTab(self.runs_table, self.tr("Tabelle"))
        runs_tab.addTab(self.pace_distance_chart, self.tr("Pace vs. Distanz"))
        self.tab_widget.addTab(runs_tab, self.tr("Runs"))

        main_layout.addWidget(self.tab_widget, stretch=3)

        # Charts open empty until data loads (or auth completes).
        self._show_charts_empty_state()

    def _setup_menu(self):
        """Set up the menubar with File and Help menus."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(self.tr("&File"))

        export_csv_action = QAction(self.tr("Export Data as CSV…"), self)
        export_csv_action.triggered.connect(self._export_activities_csv)
        file_menu.addAction(export_csv_action)
        self.export_csv_action = export_csv_action

        manage_races_action = QAction(self.tr("Manage Races…"), self)
        manage_races_action.triggered.connect(self._show_race_manager)
        file_menu.addAction(manage_races_action)
        self.manage_races_action = manage_races_action

        manage_goals_action = QAction(self.tr("Manage Goals…"), self)
        manage_goals_action.triggered.connect(self._show_goal_manager)
        file_menu.addAction(manage_goals_action)
        self.manage_goals_action = manage_goals_action

        help_menu = menu_bar.addMenu(self.tr("&Help"))
        wizard_action = QAction(self.tr("First-Run Wizard"), self)
        wizard_action.triggered.connect(self._show_onboarding_wizard)
        help_menu.addAction(wizard_action)
        self.wizard_action = wizard_action

    def _export_activities_csv(self):
        """Export the currently filtered activities to a user-chosen CSV file."""
        if not self.activities:
            QMessageBox.information(
                self,
                self.tr("Export Data as CSV"),
                self.tr("There are no activities to export. Sync first."),
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Export Data as CSV"),
            default_csv_filename(),
            self.tr("CSV File (*.csv)"),
        )
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"

        try:
            count = export_activities_csv(self.activities, path)
        except OSError as exc:
            QMessageBox.warning(
                self,
                self.tr("Export failed"),
                self.tr("Could not write CSV file: {}").format(exc),
            )
            return

        self.statusbar.showMessage(
            self.tr("Exported {} activities to {}").format(count, path), 5000
        )

    def _setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = QToolBar(self.tr("Main Toolbar"))
        self.addToolBar(toolbar)

        style = self.style()

        # Settings button (left)
        settings_action = QAction(self.tr("Settings"), self)
        settings_action.setIcon(QIcon.fromTheme(
            "preferences-system",
            style.standardIcon(QStyle.SP_FileDialogDetailedView),
        ))
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)

        # Connect button (visible only while not authenticated; spec §13.1)
        self.connect_action = QAction(self.tr("Connect to Strava"), self)
        self.connect_action.setIcon(QIcon.fromTheme(
            "network-connect",
            style.standardIcon(QStyle.SP_DriveNetIcon),
        ))
        self.connect_action.triggered.connect(self._authenticate_strava)
        toolbar.addAction(self.connect_action)

        # Sync button (manual trigger; spec §13.1).
        # Disabled while a manual sync is in flight to prevent double trigger.
        self.sync_action = QAction(self.tr("Sync"), self)
        self.sync_action.setIcon(QIcon.fromTheme(
            "view-refresh",
            style.standardIcon(QStyle.SP_BrowserReload),
        ))
        self.sync_action.triggered.connect(self._sync_activities)
        toolbar.addAction(self.sync_action)

        toolbar.addSeparator()

        # Start date selector
        toolbar.addWidget(QLabel(self.tr("Start Date:")))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        # Default to a very early date to capture all activities (Strava founded 2009)
        self.start_date_edit.setDate(QDate(2000, 1, 1))
        self.start_date_edit.dateChanged.connect(self._on_start_date_changed)
        toolbar.addWidget(self.start_date_edit)

        toolbar.addSeparator()

        # Period selector
        toolbar.addWidget(QLabel(self.tr("Period:")))
        self.period_combo = QComboBox()
        self.period_combo.addItems([self.tr("Week"), self.tr("Month")])
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        toolbar.addWidget(self.period_combo)

        toolbar.addSeparator()

        # Metric selector
        toolbar.addWidget(QLabel(self.tr("Metric:")))
        self.metric_combo = QComboBox()
        self.metric_combo.addItems([self.tr("Pace"), self.tr("Speed")])
        self.metric_combo.currentTextChanged.connect(self._on_metric_changed)
        toolbar.addWidget(self.metric_combo)

        toolbar.addSeparator()

        # Smoothing selector
        toolbar.addWidget(QLabel(self.tr("Smoothing:")))
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.addItems([self.tr("Off"), self.tr("Light"), self.tr("Medium"), self.tr("Strong")])
        self.smoothing_combo.setCurrentText(self.tr("Medium"))
        self.smoothing_combo.currentTextChanged.connect(self._on_smoothing_changed)
        toolbar.addWidget(self.smoothing_combo)

        toolbar.addSeparator()

        # Year-over-year compare toggle. Disabled until _load_data confirms
        # there's at least a year of historical data to compare against.
        self.compare_prev_year_check = QCheckBox(self.tr("Compare to previous year"))
        self.compare_prev_year_check.setChecked(
            bool(self.settings.get('ui_compare_prev_year', False))
        )
        self.compare_prev_year_check.setToolTip(self.tr(
            "Show a dimmed dashed line for the same metric one year ago. "
            "Requires at least one year of historical data."
        ))
        self.compare_prev_year_check.setEnabled(False)
        self.compare_prev_year_check.toggled.connect(self._on_compare_prev_year_toggled)
        toolbar.addWidget(self.compare_prev_year_check)

        # Spacer to push Help and About to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Help button (right)
        help_action = QAction(self.tr("Help"), self)
        help_action.triggered.connect(self._show_manual)
        toolbar.addAction(help_action)

        # About button (far right)
        about_action = QAction(self.tr("About"), self)
        about_action.triggered.connect(self._show_about)
        toolbar.addAction(about_action)


    def _setup_statusbar(self):
        """Set up the status bar.

        Permanent widgets on the right show auth status and last-sync time
        (spec §13.1). Transient `showMessage()` calls write to the left area
        and never overwrite the permanent widgets.
        """
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.auth_status_label = QLabel()
        self.last_sync_label = QLabel()
        self.statusbar.addPermanentWidget(self.auth_status_label)
        self.statusbar.addPermanentWidget(self.last_sync_label)

        self._update_persistent_status()
        # Refresh "N min ago" once a minute so the label stays accurate.
        self._status_refresh_timer = QTimer(self)
        self._status_refresh_timer.setInterval(60_000)
        self._status_refresh_timer.timeout.connect(self._update_persistent_status)
        self._status_refresh_timer.start()

        self.statusbar.showMessage(self.tr("Ready"))

    def _update_persistent_status(self):
        """Refresh the auth/last-sync labels in the status bar."""
        if getattr(self, 'auth', None) is not None and self.auth.is_authenticated():
            self.auth_status_label.setText(self.tr("● Connected"))
            self.auth_status_label.setToolTip(self.tr("Connected to Strava"))
        else:
            self.auth_status_label.setText(self.tr("○ Not connected"))
            self.auth_status_label.setToolTip(self.tr("Not connected to Strava"))

        last_sync = self.db.get_setting('last_sync')
        if not last_sync:
            self.last_sync_label.setText(self.tr("Never synced"))
        else:
            self.last_sync_label.setText(
                self.tr("Last sync: {}").format(self._format_relative_time(last_sync))
            )

    def _update_toolbar_state(self):
        """Show/hide the Connect button based on current auth state (spec §13.1)."""
        if not hasattr(self, 'connect_action'):
            return  # Toolbar not yet built
        authenticated = (
            getattr(self, 'auth', None) is not None and self.auth.is_authenticated()
        )
        self.connect_action.setVisible(not authenticated)

    def _format_relative_time(self, iso_str: str) -> str:
        """Return a short relative time string for an ISO timestamp."""
        try:
            ts = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return iso_str

        if ts.tzinfo is None:
            # Stored as naive UTC by sync_manager (datetime.utcnow().isoformat()).
            now = datetime.utcnow()
        else:
            from datetime import timezone
            now = datetime.now(timezone.utc)

        delta = now - ts
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return self.tr("just now")
        minutes = seconds // 60
        if minutes < 60:
            return self.tr("{} min ago").format(minutes)
        hours = minutes // 60
        if hours < 24:
            return self.tr("{} hr ago").format(hours)
        days = hours // 24
        return self.tr("{} days ago").format(days)

    def _check_authentication(self):
        """Check if user is already authenticated."""
        # Load access token from settings
        self.auth = SimpleStravaAuth(self.settings)

        if self.auth.is_authenticated():
            self._setup_strava_client()
            self.statusbar.showMessage(self.tr("Connected to Strava"))
            self._load_data()

            # Auto-sync on startup (silent incremental sync)
            activity_count = self.db.get_activity_count()
            if activity_count > 0:
                # Only do incremental sync if we already have data
                self._run_silent_sync()
        else:
            # Not authenticated. First-run (empty DB) gets the onboarding
            # wizard; legacy installs without auth keep the settings shortcut.
            self.statusbar.showMessage(self.tr("Not connected - Please configure Strava connection"))
            if self.db.get_activity_count() == 0:
                QTimer.singleShot(100, self._show_onboarding_wizard)
            else:
                QTimer.singleShot(100, self._show_settings)

        self._update_persistent_status()
        self._update_toolbar_state()

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
                self, self.tr("Disconnect"),
                self.tr("Do you want to disconnect from Strava?"),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.auth.revoke()
                self.auth = None
                self.client = None
                self.sync_manager = None
                self.statusbar.showMessage(self.tr("Disconnected from Strava"))
                self._update_persistent_status()
                self._update_toolbar_state()
            return

        # Start OAuth flow
        client_id = self.settings.get('strava_client_id')
        client_secret = self.settings.get('strava_client_secret')

        if not client_id or not client_secret:
            # Ask user to configure API credentials first
            reply = QMessageBox.information(
                self, self.tr("Strava API Configuration Required"),
                self.tr("To connect to Strava, you first need to configure your API credentials.\n\n"
                "1. Go to Settings\n"
                "2. Enter your Client ID and Client Secret\n"
                "3. Click 'Connect to Strava' again\n\n"
                "Get your credentials from:\n"
                "https://www.strava.com/settings/api"),
                QMessageBox.Ok
            )
            return

        # Create auth instance if not exists
        if not self.auth:
            self.auth = SimpleStravaAuth(self.settings)

        # Show progress message
        self.statusbar.showMessage(self.tr("Opening browser for Strava authorization..."))

        # Run OAuth flow in background thread so the Qt event loop stays alive
        self._auth_thread = _StravaAuthThread(self.auth, client_id, client_secret)
        self._auth_thread.finished.connect(self._on_auth_finished)
        self._auth_thread.finished.connect(self._auth_thread.deleteLater)
        self._auth_thread.start()

    def _on_auth_finished(self, success: bool):
        self._update_persistent_status()
        self._update_toolbar_state()
        # Suppress the follow-up dialogs while the onboarding wizard is in
        # the foreground — the wizard owns the sync trigger and shows its
        # own status, so layering a QMessageBox on top would be jarring.
        wizard_active = getattr(self, '_onboarding_active', False)
        if success:
            self._setup_strava_client()
            self.statusbar.showMessage(self.tr("Successfully connected to Strava!"))
            if not wizard_active:
                reply = QMessageBox.question(
                    self, self.tr("Sync Activities"),
                    self.tr("Successfully connected to Strava!\n\n"
                    "Do you want to sync your activities now?"),
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self._sync_activities()
        else:
            self.statusbar.showMessage(self.tr("Failed to connect to Strava"))
            if not wizard_active:
                QMessageBox.warning(
                    self, self.tr("Authorization Failed"),
                    self.tr("Failed to authorize with Strava.\n\n"
                    "Please try again or check your API credentials in Settings.")
                )
        self.auth_finished.emit(success)

    def _show_onboarding_wizard(self):
        """Show the first-run onboarding wizard (also reachable via Help menu)."""
        self._onboarding_active = True
        try:
            wizard = OnboardingWizard(self, parent=self)
            accepted = bool(wizard.exec())
            chosen_date = wizard.selected_start_date if accepted else None
        finally:
            self._onboarding_active = False

        if not accepted or chosen_date is None:
            return

        self.start_date_edit.setDate(chosen_date)
        date_str = (
            f"{chosen_date.year()}-{chosen_date.month():02d}-{chosen_date.day():02d}"
        )
        self.settings.set('ui_start_date', date_str)

        # Trigger an initial sync if we ended up authenticated and the DB is
        # still empty — that completes the "after Finish: data appears" AC.
        if (
            self.auth and self.auth.is_authenticated()
            and self.db.get_activity_count() == 0
        ):
            if not self.client:
                self._setup_strava_client()
            self._sync_activities()

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
                    self.statusbar.showMessage(self.tr("Reconnected to Strava with new settings"))
        # Refresh persistent status — the dialog may have revoked auth or
        # cleared sync settings.
        self._update_persistent_status()
        self._update_toolbar_state()

    def _show_race_manager(self):
        """Open the Race-Manager dialog."""
        dialog = RaceManagerDialog(self.db, self)
        dialog.exec()
        # Markers may have changed (add/edit/delete); redraw charts.
        if getattr(self, 'aggregates', None):
            self._update_charts()

    def _show_goal_manager(self):
        """Open the Goal-Manager dialog."""
        dialog = GoalManagerDialog(self.db, self)
        dialog.exec()
        if getattr(self, 'aggregates', None):
            self._update_charts()

    def _mark_activity_as_race(self, activity: dict):
        """Open RaceDialog prefilled from an activity and persist on accept."""
        dialog = RaceDialog(self, activity=activity)
        if not dialog.exec():
            return
        data = dialog.get_data()
        try:
            self.db.add_race_marker(
                date=data["date"],
                name=data["name"],
                distance_km=data["distance_km"],
                result_time=data["result_time"],
                notes=data["notes"],
            )
        except Exception as exc:  # pragma: no cover — defensive UI feedback
            QMessageBox.warning(
                self,
                self.tr("Could not save race"),
                self.tr("Failed to save race marker: {}").format(exc),
            )
            return
        self.statusbar.showMessage(
            self.tr("Saved race: {}").format(data["name"]), 5000
        )
        if getattr(self, 'aggregates', None):
            self._update_charts()

    def _show_manual(self):
        """Show manual/help dialog."""
        # Get current language, default to 'de' if not set
        language = getattr(self, 'current_language', 'de')
        dialog = ManualDialog(self, language=language)
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
            QMessageBox.information(
                self, self.tr("Not Connected"),
                self.tr("Please connect to Strava first via Settings.")
            )
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
        self.sync_action.setEnabled(False)

        # Create progress dialog
        self.progress_dialog = QProgressDialog(self.tr("Syncing activities..."), self.tr("Cancel"), 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)

        # Create and start sync thread with db_path instead of sync_manager
        self.sync_thread = SyncThread(self.db.db_path, self.client, sync_type, start_date)
        self.sync_thread.progress.connect(self._on_sync_progress)
        self.sync_thread.finished.connect(self._on_sync_finished)
        self.sync_thread.finished.connect(self.sync_thread.deleteLater)
        self.sync_thread.start()

    def _run_silent_sync(self):
        """Run silent incremental sync in background (no dialogs)."""
        # Create and start sync thread for incremental sync only
        self.silent_sync_thread = SyncThread(self.db.db_path, self.client, 'incremental', None)
        self.silent_sync_thread.finished.connect(self._on_silent_sync_finished)
        self.silent_sync_thread.finished.connect(self.silent_sync_thread.deleteLater)
        self.silent_sync_thread.start()
        self.statusbar.showMessage(self.tr("Checking for new activities..."))

    def _on_sync_progress(self, current, total, message):
        """Handle sync progress updates."""
        if total > 0:
            self.progress_dialog.setMaximum(total)
            self.progress_dialog.setValue(current)
        self.progress_dialog.setLabelText(message)

    def _on_sync_finished(self, stats):
        """Handle sync completion."""
        self.progress_dialog.close()
        self.sync_action.setEnabled(True)

        message = self.tr("Sync completed:\n")
        message += self.tr("Fetched: {}\n").format(stats['fetched'])
        message += self.tr("Imported: {}\n").format(stats['imported'])
        message += self.tr("Updated: {}\n").format(stats['updated'])
        if stats['errors'] > 0:
            message += self.tr("Errors: {}\n").format(stats['errors'])

        QMessageBox.information(self, self.tr("Sync Complete"), message)

        # Refresh data
        self._load_data()
        self._update_persistent_status()

    def _on_silent_sync_finished(self, stats):
        """Handle silent sync completion (no dialog, only status message)."""
        # Only show message if new activities were found or errors occurred
        if stats['imported'] > 0 or stats['updated'] > 0:
            self.statusbar.showMessage(
                self.tr("Sync complete: {} new, {} updated").format(stats['imported'], stats['updated'])
            )
            # Refresh data to show new activities
            self._load_data()
        elif stats['errors'] > 0:
            self.statusbar.showMessage(self.tr("Sync completed with {} errors").format(stats['errors']))
        else:
            self.statusbar.showMessage(self.tr("No new activities found"))
            # Clear message after 3 seconds
            QTimer.singleShot(3000, lambda: self.statusbar.showMessage(self.tr("Connected to Strava")))
        self._update_persistent_status()

    def _load_data(self):
        """Load activities from database and refresh UI."""
        # Get start date from widget
        start_date_q = self.start_date_edit.date()
        start_date_str = f"{start_date_q.year()}-{start_date_q.month():02d}-{start_date_q.day():02d}"

        # Apply spec §11 inclusion filters (treadmill, manual entries)
        include_treadmill = bool(self.settings.get('include_treadmill', True))
        include_manual = bool(self.settings.get('include_manual', True))

        # Load activities from start date onwards
        self.activities = self.db.get_activities_since(
            start_date_str,
            include_treadmill=include_treadmill,
            include_manual=include_manual,
        )

        # Load activities from the year before the visible window for the
        # year-over-year compare toggle. Filtered to strict prev-year window
        # by dropping anything that overlaps the current visible range.
        prev_start_q = start_date_q.addYears(-1)
        prev_start_str = (
            f"{prev_start_q.year()}-{prev_start_q.month():02d}-"
            f"{prev_start_q.day():02d}"
        )
        prev_pool = self.db.get_activities_since(
            prev_start_str,
            include_treadmill=include_treadmill,
            include_manual=include_manual,
        )
        self._prev_year_activities = [
            a for a in prev_pool
            if (a.get('start_date') or '') < start_date_str
        ]

        self._refresh_compare_toggle_state()
        self._refresh_data()

    def _refresh_compare_toggle_state(self):
        """Enable/disable the prev-year toggle based on data availability."""
        if not hasattr(self, 'compare_prev_year_check'):
            return
        has_prev = bool(getattr(self, '_prev_year_activities', None))
        self.compare_prev_year_check.setEnabled(has_prev)
        if not has_prev and self.compare_prev_year_check.isChecked():
            self.compare_prev_year_check.blockSignals(True)
            self.compare_prev_year_check.setChecked(False)
            self.compare_prev_year_check.blockSignals(False)

    def _refresh_data(self):
        """Refresh aggregations and charts."""
        if not self.activities:
            self._show_charts_empty_state()
            return

        self.aggregates = DataManager.build_aggregates(self.activities, self.current_period)

        prev_activities = getattr(self, '_prev_year_activities', None)
        if prev_activities:
            prev_raw = DataManager.build_aggregates(prev_activities, self.current_period)
            self.prev_year_aggregates = DataManager.align_previous_year_aggregates(
                prev_raw, self.current_period
            )
        else:
            self.prev_year_aggregates = []

        # Update summary panel
        self._update_summary()

        # Update charts
        self._update_charts()

    def _all_charts(self):
        """Return every chart widget so we can broadcast empty-state changes."""
        return [
            self.distance_chart, self.pace_chart, self.frequency_chart,
            self.score_chart, self.projection_chart, self.endurance_chart,
            self.structure_overview_chart, self.heartrate_chart,
            self.hr_zone_chart, self.duration_chart, self.training_load_chart,
            self.pace_distance_chart,
        ]

    def _show_charts_empty_state(self):
        """Display a guidance message on every chart when there are no runs."""
        connected = (
            getattr(self, 'auth', None) is not None and self.auth.is_authenticated()
        )
        if not connected:
            message = self.tr(
                "No runs yet.\n"
                "Connect your Strava account to import your activities."
            )
            show_button = True
        else:
            message = self.tr(
                "No runs in the selected date range.\n"
                "Pick an earlier start date or sync to fetch new activities."
            )
            show_button = False

        for chart in self._all_charts():
            chart.show_empty_state(message, show_connect_button=show_button)

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

        # Check if current period is complete
        is_current_period_complete = latest_agg.get('is_complete', True)

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

        # Training Load data
        load_data = latest_agg.get('training_load')

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
            'hrmax_check': hrmax_check,
            'is_current_period_complete': is_current_period_complete,
            'training_load': load_data,
            'active_days': latest_agg.get('active_days'),
            'consistency_ratio': latest_agg.get('consistency_ratio'),
            'score_components': latest_agg.get('score_components'),
        })

    def _apply_race_markers_to_charts(self):
        """Push current race markers from DB into the time-axis charts."""
        races = self.db.get_race_markers()
        for chart in (
            self.distance_chart, self.pace_chart, self.frequency_chart,
            self.duration_chart, self.score_chart, self.training_load_chart,
        ):
            chart.set_race_markers(races)

    def _update_charts(self):
        """Update all charts."""
        self._apply_race_markers_to_charts()

        # Use index instead of localized text so non-English UIs work correctly
        smoothing_levels = ['off', 'light', 'medium', 'strong']
        smoothing_strength = smoothing_levels[self.smoothing_combo.currentIndex()]

        metric_levels = ['pace', 'speed']
        metric = metric_levels[self.metric_combo.currentIndex()]

        prev = (
            getattr(self, 'prev_year_aggregates', None)
            if (
                hasattr(self, 'compare_prev_year_check')
                and self.compare_prev_year_check.isChecked()
            )
            else None
        )

        self.distance_chart.update_chart(
            self.aggregates, smoothing_strength, prev_year_aggregates=prev,
        )
        self.pace_chart.update_chart(
            self.aggregates, smoothing_strength, metric, prev_year_aggregates=prev,
        )
        self.frequency_chart.update_chart(
            self.aggregates, smoothing_strength, prev_year_aggregates=prev,
        )
        self.heartrate_chart.update_chart(self.aggregates, smoothing_strength)
        self.duration_chart.update_chart(
            self.aggregates, smoothing_strength, prev_year_aggregates=prev,
        )
        self.endurance_chart.update_chart(self.aggregates, smoothing_strength)
        self.structure_overview_chart.update_chart(self.aggregates, smoothing_strength)
        self.score_chart.update_chart(self.aggregates, smoothing_strength)
        self.training_load_chart.update_chart(self.aggregates)
        self.projection_chart.set_goals(self.db.get_goals(include_achieved=False))
        self.projection_chart.update_chart(self.aggregates, self.current_period)
        self.runs_table.update_table(self.activities)
        self.pace_distance_chart.update_chart(self.activities)
        self._update_hr_zone_chart()

    def _update_hr_zone_chart(self):
        """Render whatever zone data is already cached for the visible runs.

        The heavy work — fetching streams from Strava — runs lazily in
        ``_maybe_start_hr_zone_fetch`` triggered by tab activation. This
        method is a pure DB-and-render pass so it's cheap to call from
        ``_update_charts``.
        """
        hr_max_configured = int(self.settings.get('manual_hrmax', 0) or 0) > 0
        hr_activities = [a for a in self.activities if a.get('has_heartrate')]
        any_hr_activities = bool(hr_activities)

        per_activity = []
        for a in hr_activities:
            cached = self.db.get_activity_hr_zones(a['strava_id'])
            if not cached:
                continue
            try:
                start = datetime.fromisoformat(a['start_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError, KeyError):
                continue
            per_activity.append({
                'date': start.replace(tzinfo=None),
                'activity_id': a['strava_id'],
                'zone_seconds': [
                    int(cached['z1_seconds']), int(cached['z2_seconds']),
                    int(cached['z3_seconds']), int(cached['z4_seconds']),
                    int(cached['z5_seconds']),
                ],
                'name': a.get('name', ''),
            })

        self.hr_zone_chart.update_chart(
            per_activity,
            period_type=self.current_period,
            hr_max_configured=hr_max_configured,
            any_hr_activities=any_hr_activities,
        )

    def _on_tab_changed(self, index):
        """Trigger a lazy stream-fetch the first time the user opens HR Zones."""
        if index != getattr(self, '_hr_zone_tab_index', -1):
            return
        if self._hr_zone_autofetch_done:
            return
        self._maybe_start_hr_zone_fetch()

    def _maybe_start_hr_zone_fetch(self):
        """Spawn a worker that fills the HR-zone cache for visible activities."""
        if self.hr_zone_fetch_thread and self.hr_zone_fetch_thread.isRunning():
            return
        if int(self.settings.get('manual_hrmax', 0) or 0) <= 0:
            return  # nothing to compute without HR-Max
        if not self.client or not self.activities:
            return

        targets = []
        for a in self.activities:
            if not a.get('has_heartrate'):
                continue
            if self.db.get_activity_hr_zones(a['strava_id']) is None:
                targets.append(a['strava_id'])
        if not targets:
            self._hr_zone_autofetch_done = True
            return

        snapshot = {
            'manual_hrmax': self.settings.get('manual_hrmax', 0),
            'hr_rest': self.settings.get('hr_rest', 0),
            'hr_zone_scheme': self.settings.get('hr_zone_scheme', 'classic'),
        }
        self.hr_zone_fetch_thread = HrZoneFetchThread(
            self.db.db_path, self.client, snapshot, targets,
        )
        self.hr_zone_fetch_thread.progress.connect(self._on_hr_zone_progress)
        self.hr_zone_fetch_thread.finished_signal.connect(self._on_hr_zone_fetch_done)
        self.hr_zone_fetch_thread.finished.connect(
            self.hr_zone_fetch_thread.deleteLater
        )
        self.statusbar.showMessage(
            self.tr("Fetching heart-rate zones (0/{})…").format(len(targets))
        )
        self.hr_zone_fetch_thread.start()

    def _on_hr_zone_progress(self, current, total):
        self.statusbar.showMessage(
            self.tr("Fetching heart-rate zones ({}/{})…").format(current, total)
        )

    def _on_hr_zone_fetch_done(self):
        self._hr_zone_autofetch_done = True
        self.statusbar.showMessage(self.tr("Heart-rate zones updated"), 4000)
        self._update_hr_zone_chart()

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

        # Use index instead of localized text to determine period
        self.current_period = 'week' if self.period_combo.currentIndex() == 0 else 'month'
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

    def _on_compare_prev_year_toggled(self, checked: bool):
        """Toggle the year-over-year compare line on the supported charts."""
        self.settings.set('ui_compare_prev_year', bool(checked))
        self._update_charts()
