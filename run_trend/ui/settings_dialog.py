"""
Settings dialog for application configuration.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QGroupBox, QMessageBox, QSpinBox, QComboBox,
    QCheckBox, QTabWidget, QWidget, QDateEdit,
)
from PySide6.QtCore import Qt, QDate


class SettingsDialog(QDialog):
    """Settings dialog window."""

    def __init__(self, settings, parent=None, main_window=None):
        super().__init__(parent)
        self.settings = settings
        self.main_window = main_window
        self.setWindowTitle(self.tr("Settings"))
        self.setMinimumWidth(500)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        tabs.addTab(self._build_general_tab(), self.tr("General"))
        tabs.addTab(self._build_connection_tab(), self.tr("Connection"))
        tabs.addTab(self._build_sync_tab(), self.tr("Sync"))
        tabs.addTab(self._build_data_tab(), self.tr("Data"))
        layout.addWidget(tabs)

        # Update button states based on auth status
        self._update_auth_status()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton(self.tr("Save"))
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    # ------------------------------------------------------------------ #
    # Tabs                                                                #
    # ------------------------------------------------------------------ #

    def _build_general_tab(self) -> QWidget:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Language Settings Group
        language_group = QGroupBox(self.tr("Language / Sprache"))
        language_layout = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.addItems([
            self.tr("Auto-detect"),
            self.tr("Deutsch"),
            self.tr("English")
        ])
        language_layout.addRow(self.tr("Language:"), self.language_combo)

        language_info_label = QLabel(
            self.tr("Language changes take effect after restarting the application.")
        )
        language_info_label.setWordWrap(True)
        language_info_label.setStyleSheet("color: gray; font-size: 10px;")
        language_layout.addRow("", language_info_label)

        language_group.setLayout(language_layout)
        tab_layout.addWidget(language_group)

        # Profile (Ticket 37 — age-graded performance needs date of birth + gender)
        profile_group = QGroupBox(self.tr("Profile"))
        profile_layout = QFormLayout()

        # Sentinel for "unset" birth date — 1900-01-01 paired with
        # setSpecialValueText shows "Not set" instead of the date.
        self._birth_date_unset = QDate(1900, 1, 1)

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDisplayFormat("yyyy-MM-dd")
        self.birth_date_input.setMinimumDate(self._birth_date_unset)
        self.birth_date_input.setMaximumDate(QDate.currentDate())
        self.birth_date_input.setSpecialValueText(self.tr("Not set"))
        self.birth_date_input.setDate(self._birth_date_unset)
        self.birth_date_input.setToolTip(self.tr(
            "Date of birth — used to compute your age for the Performance "
            "tab (age-graded race percentage and personal-peak EF decline)."
        ))
        profile_layout.addRow(self.tr("Date of Birth:"), self.birth_date_input)

        self.gender_combo = QComboBox()
        self.gender_combo.addItem(self.tr("Prefer not to say"), userData='')
        self.gender_combo.addItem(self.tr("Male"), userData='male')
        self.gender_combo.addItem(self.tr("Female"), userData='female')
        self.gender_combo.setToolTip(self.tr(
            "Required for WMA age-graded performance — the tables are "
            "gender-specific. The HF-physiology variant does not need it."
        ))
        profile_layout.addRow(self.tr("Gender:"), self.gender_combo)

        profile_group.setLayout(profile_layout)
        tab_layout.addWidget(profile_group)

        # Heart Rate Settings Group
        hr_group = QGroupBox(self.tr("Heart Rate Configuration"))
        hr_layout = QFormLayout()

        self.hrmax_input = QSpinBox()
        self.hrmax_input.setRange(0, 220)  # 0 = auto-detect
        self.hrmax_input.setSuffix(self.tr(" bpm"))
        self.hrmax_input.setSpecialValueText(self.tr("Auto-detect from activities"))
        self.hrmax_input.setToolTip(
            self.tr("Set your maximum heart rate manually if known.\n"
            "Set to 0 to auto-detect from your activity data.\n"
            "Typical values: 180-200 bpm for younger athletes, 160-180 for older.")
        )
        hr_layout.addRow(self.tr("Max Heart Rate:"), self.hrmax_input)

        self.hr_rest_input = QSpinBox()
        self.hr_rest_input.setRange(0, 200)  # 0 = unset
        self.hr_rest_input.setSuffix(self.tr(" bpm"))
        self.hr_rest_input.setSpecialValueText(self.tr("Not set"))
        self.hr_rest_input.setToolTip(
            self.tr("Resting heart rate. Required for the Karvonen zone scheme.\n"
            "Typical values: 50–70 bpm.")
        )
        hr_layout.addRow(self.tr("Resting Heart Rate:"), self.hr_rest_input)

        self.hr_zone_scheme_combo = QComboBox()
        self.hr_zone_scheme_combo.addItem(
            self.tr("Classic (% of HR-Max)"), userData='classic',
        )
        self.hr_zone_scheme_combo.addItem(
            self.tr("Karvonen (HR-Reserve)"), userData='karvonen',
        )
        self.hr_zone_scheme_combo.setToolTip(
            self.tr("Classic uses fixed percentages of HR-Max.\n"
            "Karvonen uses HR-Reserve = (HR-Max − HR-Rest) and shifts zones up.")
        )
        hr_layout.addRow(self.tr("Zone Scheme:"), self.hr_zone_scheme_combo)

        hr_info_label = QLabel(
            self.tr("Manual HRmax improves race time predictions.\n"
            "If unsure, leave at 'Auto-detect'.")
        )
        hr_info_label.setWordWrap(True)
        hr_info_label.setStyleSheet("color: gray; font-size: 10px;")
        hr_layout.addRow("", hr_info_label)

        hr_group.setLayout(hr_layout)
        tab_layout.addWidget(hr_group)

        tab_layout.addStretch()
        return tab

    def _build_connection_tab(self) -> QWidget:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Strava Settings Group
        strava_group = QGroupBox(self.tr("Strava API Configuration"))
        strava_layout = QFormLayout()

        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText(self.tr("Your Strava API Client ID"))
        strava_layout.addRow(self.tr("Client ID:"), self.client_id_input)

        self.client_secret_input = QLineEdit()
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        self.client_secret_input.setPlaceholderText(self.tr("Your Strava API Client Secret"))

        show_secret_btn = QPushButton(self.tr("Show"))
        show_secret_btn.setMaximumWidth(60)
        show_secret_btn.clicked.connect(self._toggle_secret_visibility)

        secret_layout = QHBoxLayout()
        secret_layout.addWidget(self.client_secret_input)
        secret_layout.addWidget(show_secret_btn)

        strava_layout.addRow(self.tr("Client Secret:"), secret_layout)

        info_label = QLabel(
            self.tr("Get your API credentials from:\n"
            "https://www.strava.com/settings/api\n\n"
            "After saving, use 'Connect to Strava' below to authorize.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        strava_layout.addRow("", info_label)

        strava_group.setLayout(strava_layout)
        tab_layout.addWidget(strava_group)

        # Connect button + status (no nested GroupBox — the tab itself frames this)
        self.connect_btn = QPushButton(self.tr("Connect to Strava"))
        self.connect_btn.clicked.connect(self._handle_connect)
        tab_layout.addWidget(self.connect_btn)

        self.status_label = QLabel(self.tr("Not connected"))
        self.status_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        tab_layout.addWidget(self.status_label)

        tab_layout.addStretch()
        return tab

    def _build_sync_tab(self) -> QWidget:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Activity Filters Group (spec §11)
        filters_group = QGroupBox(self.tr("Activity Filters"))
        filters_layout = QVBoxLayout()

        self.include_treadmill_checkbox = QCheckBox(
            self.tr("Include treadmill / indoor runs")
        )
        self.include_treadmill_checkbox.setToolTip(
            self.tr("Strava marks indoor/treadmill runs with the 'trainer' flag.")
        )
        filters_layout.addWidget(self.include_treadmill_checkbox)

        self.include_manual_checkbox = QCheckBox(
            self.tr("Include manually entered activities")
        )
        self.include_manual_checkbox.setToolTip(
            self.tr("Activities entered by hand instead of recorded by a device.")
        )
        filters_layout.addWidget(self.include_manual_checkbox)

        filters_info = QLabel(
            self.tr("Filters apply when loading existing data; changes refresh charts immediately.")
        )
        filters_info.setWordWrap(True)
        filters_info.setStyleSheet("color: gray; font-size: 10px;")
        filters_layout.addWidget(filters_info)

        filters_group.setLayout(filters_layout)
        tab_layout.addWidget(filters_group)

        # Manual sync action
        sync_group = QGroupBox(self.tr("Manual Sync"))
        sync_layout = QVBoxLayout()

        self.sync_btn = QPushButton(self.tr("Sync Activities"))
        self.sync_btn.setEnabled(False)
        self.sync_btn.clicked.connect(self._handle_sync)
        sync_layout.addWidget(self.sync_btn)

        sync_group.setLayout(sync_layout)
        tab_layout.addWidget(sync_group)

        tab_layout.addStretch()
        return tab

    def _build_data_tab(self) -> QWidget:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        danger_group = QGroupBox(self.tr("Disconnect & Delete"))
        danger_layout = QVBoxLayout()

        self.delete_data_btn = QPushButton(self.tr("Disconnect Strava & Delete All Data"))
        self.delete_data_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #9e9e9e;
            }
        """)
        self.delete_data_btn.clicked.connect(self._handle_delete_data)
        self.delete_data_btn.setEnabled(False)  # Disabled when not connected
        danger_layout.addWidget(self.delete_data_btn)

        danger_info = QLabel(
            self.tr("Removes the Strava authorization for RunTrend and erases "
            "all locally stored activities. This cannot be undone.")
        )
        danger_info.setWordWrap(True)
        danger_info.setStyleSheet("color: gray; font-size: 10px;")
        danger_layout.addWidget(danger_info)

        danger_group.setLayout(danger_layout)
        tab_layout.addWidget(danger_group)

        tab_layout.addStretch()
        return tab

    # ------------------------------------------------------------------ #
    # Behaviour (unchanged from pre-tab layout)                            #
    # ------------------------------------------------------------------ #

    def _toggle_secret_visibility(self):
        """Toggle client secret visibility."""
        if self.client_secret_input.echoMode() == QLineEdit.Password:
            self.client_secret_input.setEchoMode(QLineEdit.Normal)
        else:
            self.client_secret_input.setEchoMode(QLineEdit.Password)

    def _load_settings(self):
        """Load current settings into form."""
        client_id = self.settings.get('strava_client_id', '')
        client_secret = self.settings.get('strava_client_secret', '')
        manual_hrmax = self.settings.get('manual_hrmax', 0)
        hr_rest = self.settings.get('hr_rest', 0)
        hr_zone_scheme = self.settings.get('hr_zone_scheme', 'classic')
        language = self.settings.get('language', 'auto')
        include_treadmill = bool(self.settings.get('include_treadmill', True))
        include_manual = bool(self.settings.get('include_manual', True))
        birth_date_iso = self.settings.get('birth_date', '') or ''
        gender = self.settings.get('gender', '') or ''

        self.client_id_input.setText(client_id)
        self.client_secret_input.setText(client_secret)
        self.hrmax_input.setValue(manual_hrmax)
        self.hr_rest_input.setValue(hr_rest)
        scheme_idx = self.hr_zone_scheme_combo.findData(hr_zone_scheme)
        self.hr_zone_scheme_combo.setCurrentIndex(scheme_idx if scheme_idx >= 0 else 0)
        self.include_treadmill_checkbox.setChecked(include_treadmill)
        self.include_manual_checkbox.setChecked(include_manual)

        # Profile fields — empty string => "Not set" sentinel date.
        if birth_date_iso:
            parsed = QDate.fromString(birth_date_iso, "yyyy-MM-dd")
            if parsed.isValid() and parsed >= self._birth_date_unset:
                self.birth_date_input.setDate(parsed)
            else:
                self.birth_date_input.setDate(self._birth_date_unset)
        else:
            self.birth_date_input.setDate(self._birth_date_unset)
        gender_idx = self.gender_combo.findData(gender)
        self.gender_combo.setCurrentIndex(gender_idx if gender_idx >= 0 else 0)

        # Set language combo box
        language_map = {'auto': 0, 'de': 1, 'en': 2}
        self.language_combo.setCurrentIndex(language_map.get(language, 0))

    def _save_settings(self):
        """Save settings and close dialog."""
        # Check what changed
        old_client_id = self.settings.get('strava_client_id', '')
        old_client_secret = self.settings.get('strava_client_secret', '')
        old_hrmax = self.settings.get('manual_hrmax', 0)
        old_hr_rest = self.settings.get('hr_rest', 0)
        old_hr_zone_scheme = self.settings.get('hr_zone_scheme', 'classic')
        old_include_treadmill = bool(self.settings.get('include_treadmill', True))
        old_include_manual = bool(self.settings.get('include_manual', True))
        old_birth_date = self.settings.get('birth_date', '') or ''
        old_gender = self.settings.get('gender', '') or ''

        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        manual_hrmax = self.hrmax_input.value()
        hr_rest = self.hr_rest_input.value()
        hr_zone_scheme = (
            self.hr_zone_scheme_combo.currentData() or 'classic'
        )
        include_treadmill = self.include_treadmill_checkbox.isChecked()
        include_manual = self.include_manual_checkbox.isChecked()

        # Profile (T37): empty string == unset (sentinel date 1900-01-01).
        bd = self.birth_date_input.date()
        birth_date_iso = '' if bd == self._birth_date_unset else bd.toString("yyyy-MM-dd")
        gender = self.gender_combo.currentData() or ''

        # Validate Karvonen requirements before persisting.
        if hr_zone_scheme == 'karvonen':
            if hr_rest <= 0 or manual_hrmax <= 0 or hr_rest >= manual_hrmax:
                QMessageBox.warning(
                    self,
                    self.tr("Invalid Karvonen settings"),
                    self.tr(
                        "Karvonen zones need both Max Heart Rate and Resting "
                        "Heart Rate set, with HR-Rest below HR-Max."
                    ),
                )
                return

        # Get language selection
        language_index = self.language_combo.currentIndex()
        language_map = {0: 'auto', 1: 'de', 2: 'en'}
        language = language_map.get(language_index, 'auto')

        strava_changed = (client_id != old_client_id or client_secret != old_client_secret)
        hrmax_changed = (manual_hrmax != old_hrmax)
        hr_zone_config_changed = (
            manual_hrmax != old_hrmax
            or hr_rest != old_hr_rest
            or hr_zone_scheme != old_hr_zone_scheme
        )
        filters_changed = (
            include_treadmill != old_include_treadmill
            or include_manual != old_include_manual
        )
        profile_changed = (
            birth_date_iso != old_birth_date or gender != old_gender
        )

        if not client_id or not client_secret:
            reply = QMessageBox.question(
                self, self.tr("Missing Credentials"),
                self.tr("Client ID and Secret are required. Do you want to save anyway?"),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Save credentials
        self.settings.set('strava_client_id', client_id)
        self.settings.set('strava_client_secret', client_secret)

        # Save profile (T37)
        self.settings.set('birth_date', birth_date_iso)
        self.settings.set('gender', gender)

        # Save manual HRmax + HR-zone config
        self.settings.set('manual_hrmax', manual_hrmax)
        self.settings.set('hr_rest', hr_rest)
        self.settings.set('hr_zone_scheme', hr_zone_scheme)

        # Drop stale HR-zone cache rows when the inputs change. The cache
        # lazily refills on next view; no recompute here.
        if hr_zone_config_changed and self.main_window and getattr(
            self.main_window, 'db', None,
        ):
            self.main_window.db.invalidate_activity_hr_zones(
                hr_max=manual_hrmax if manual_hrmax > 0 else None,
                hr_rest=hr_rest if hr_rest > 0 else None,
                scheme=hr_zone_scheme,
            )
            # Also re-arm the auto-fetch trigger so reopening the HR-Zone
            # tab picks up the now-stale rows.
            if hasattr(self.main_window, '_hr_zone_autofetch_done'):
                self.main_window._hr_zone_autofetch_done = False

        # Save activity filters
        self.settings.set('include_treadmill', include_treadmill)
        self.settings.set('include_manual', include_manual)

        # Save language
        self.settings.set('language', language)

        # Build appropriate success message
        if strava_changed and hrmax_changed:
            if manual_hrmax > 0:
                message = self.tr(
                    "Settings saved successfully!\n\n"
                    "API credentials updated. Click 'Connect to Strava' to authorize.\n"
                    "Manual HRmax set to {0} bpm."
                ).format(manual_hrmax)
            else:
                message = self.tr(
                    "Settings saved successfully!\n\n"
                    "API credentials updated. Click 'Connect to Strava' to authorize.\n"
                    "Manual HRmax set to auto-detect."
                )
        elif strava_changed:
            message = self.tr(
                "API credentials saved successfully!\n\n"
                "Now click 'Connect to Strava' to authorize the application."
            )
        elif hrmax_changed:
            if manual_hrmax > 0:
                message = self.tr("Manual HRmax set to {0} bpm.\n\nRace predictions will be updated.").format(manual_hrmax)
            else:
                message = self.tr("Manual HRmax set to auto-detect.\n\nRace predictions will be updated.")
        else:
            message = self.tr("Settings saved successfully!")

        QMessageBox.information(self, self.tr("Settings Saved"), message)

        # Trigger data refresh in main window
        if self.main_window:
            if filters_changed:
                # Filters affect the DB query — reload activities, not just charts
                self.main_window._load_data()
            elif hr_zone_config_changed or profile_changed:
                # HR-zone config (HRmax / HR-Rest / scheme) feeds race
                # predictions, TRIMP, daily ACWR, and the CTL/Form readout.
                # Profile changes (birth_date/gender) drive the Performance
                # tab and Tanaka HRmax fallback. Either way, re-render
                # charts and summary without re-fetching activities.
                self.main_window._refresh_data()

        self.accept()

    def _update_auth_status(self):
        """Update UI based on authentication status."""
        if not self.main_window:
            return

        if self.main_window.auth and self.main_window.auth.is_authenticated():
            self.connect_btn.setText(self.tr("Disconnect from Strava"))
            self.sync_btn.setEnabled(True)
            self.delete_data_btn.setEnabled(True)
            self.status_label.setText(self.tr("Connected to Strava"))
            self.status_label.setStyleSheet("color: green; font-size: 10px; padding: 5px;")
        else:
            self.connect_btn.setText(self.tr("Connect to Strava"))
            self.sync_btn.setEnabled(False)
            self.delete_data_btn.setEnabled(False)
            self.status_label.setText(self.tr("Not connected"))
            self.status_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")

    def _handle_connect(self):
        """Handle connect/disconnect button click."""
        if not self.main_window:
            return

        # First save the credentials from the form (if not already saved)
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()

        if client_id and client_secret:
            # Save credentials before connecting
            self.settings.set('strava_client_id', client_id)
            self.settings.set('strava_client_secret', client_secret)

        self.main_window._authenticate_strava()
        self._update_auth_status()

    def _handle_sync(self):
        """Handle sync button click."""
        if not self.main_window:
            return

        self.main_window._sync_activities()

    def _handle_delete_data(self):
        """Handle complete disconnection and data deletion."""
        if not self.main_window or not self.main_window.auth:
            return

        # Confirmation dialog with strong warning
        reply = QMessageBox.warning(
            self,
            self.tr("Delete All Data"),
            self.tr(
                "This will:\n\n"
                "• Disconnect your Strava account\n"
                "• Delete all synced activities from this device\n"
                "• Remove RunTrend from your Strava authorized apps\n\n"
                "This action cannot be undone.\n\n"
                "Continue?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Perform deletion
        activity_count = 0
        if self.main_window.db:
            activity_count = self.main_window.db.delete_all_activities()
            self.main_window.db.clear_sync_settings()

        # Revoke Strava auth
        deauth_success = self.main_window.auth.revoke()

        # Clear references
        self.main_window.auth = None
        self.main_window.client = None
        self.main_window.sync_manager = None

        # Update UI
        self._update_auth_status()

        # Show completion message
        QMessageBox.information(
            self,
            self.tr("Data Deleted"),
            self.tr(
                "Successfully deleted {0} activities.\n\n"
                "RunTrend has been disconnected from your Strava account."
            ).format(activity_count)
        )
