"""
Settings dialog for application configuration.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QGroupBox, QMessageBox, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt


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

        # Language Settings Group
        language_group = QGroupBox(self.tr("Language / Sprache"))
        language_layout = QFormLayout()

        # Language selector
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            self.tr("Auto-detect"),
            self.tr("Deutsch"),
            self.tr("English")
        ])
        language_layout.addRow(self.tr("Language:"), self.language_combo)

        # Info label
        language_info_label = QLabel(
            self.tr("Language changes take effect after restarting the application.")
        )
        language_info_label.setWordWrap(True)
        language_info_label.setStyleSheet("color: gray; font-size: 10px;")
        language_layout.addRow("", language_info_label)

        language_group.setLayout(language_layout)
        layout.addWidget(language_group)

        # Strava Settings Group
        strava_group = QGroupBox(self.tr("Strava API Configuration"))
        strava_layout = QFormLayout()

        # Client ID
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText(self.tr("Your Strava API Client ID"))
        strava_layout.addRow(self.tr("Client ID:"), self.client_id_input)

        # Client Secret
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

        # Info label
        info_label = QLabel(
            self.tr("Get your API credentials from:\n"
            "https://www.strava.com/settings/api\n\n"
            "After saving, use 'Connect to Strava' below to authorize.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        strava_layout.addRow("", info_label)

        strava_group.setLayout(strava_layout)
        layout.addWidget(strava_group)

        # Heart Rate Settings Group
        hr_group = QGroupBox(self.tr("Heart Rate Configuration"))
        hr_layout = QFormLayout()

        # Manual HRmax input
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

        # Info label
        hr_info_label = QLabel(
            self.tr("Manual HRmax improves race time predictions.\n"
            "If unsure, leave at 'Auto-detect'.")
        )
        hr_info_label.setWordWrap(True)
        hr_info_label.setStyleSheet("color: gray; font-size: 10px;")
        hr_layout.addRow("", hr_info_label)

        hr_group.setLayout(hr_layout)
        layout.addWidget(hr_group)

        # Strava Actions Group
        actions_group = QGroupBox(self.tr("Strava Actions"))
        actions_layout = QVBoxLayout()

        # Connect/Disconnect button
        self.connect_btn = QPushButton(self.tr("Connect to Strava"))
        self.connect_btn.clicked.connect(self._handle_connect)
        actions_layout.addWidget(self.connect_btn)

        # Sync button
        self.sync_btn = QPushButton(self.tr("Sync Activities"))
        self.sync_btn.setEnabled(False)
        self.sync_btn.clicked.connect(self._handle_sync)
        actions_layout.addWidget(self.sync_btn)

        # Status label
        self.status_label = QLabel(self.tr("Not connected"))
        self.status_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        actions_layout.addWidget(self.status_label)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

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
        language = self.settings.get('language', 'auto')

        self.client_id_input.setText(client_id)
        self.client_secret_input.setText(client_secret)
        self.hrmax_input.setValue(manual_hrmax)

        # Set language combo box
        language_map = {'auto': 0, 'de': 1, 'en': 2}
        self.language_combo.setCurrentIndex(language_map.get(language, 0))

    def _save_settings(self):
        """Save settings and close dialog."""
        # Check what changed
        old_client_id = self.settings.get('strava_client_id', '')
        old_client_secret = self.settings.get('strava_client_secret', '')
        old_hrmax = self.settings.get('manual_hrmax', 0)

        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        manual_hrmax = self.hrmax_input.value()

        # Get language selection
        language_index = self.language_combo.currentIndex()
        language_map = {0: 'auto', 1: 'de', 2: 'en'}
        language = language_map.get(language_index, 'auto')

        strava_changed = (client_id != old_client_id or client_secret != old_client_secret)
        hrmax_changed = (manual_hrmax != old_hrmax)

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

        # Save manual HRmax
        self.settings.set('manual_hrmax', manual_hrmax)

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

        # Trigger data refresh in main window if HRmax changed
        if hrmax_changed and self.main_window:
            self.main_window._refresh_data()

        self.accept()

    def _update_auth_status(self):
        """Update UI based on authentication status."""
        if not self.main_window:
            return

        if self.main_window.auth and self.main_window.auth.is_authenticated():
            self.connect_btn.setText(self.tr("Disconnect from Strava"))
            self.sync_btn.setEnabled(True)
            self.status_label.setText(self.tr("Connected to Strava"))
            self.status_label.setStyleSheet("color: green; font-size: 10px; padding: 5px;")
        else:
            self.connect_btn.setText(self.tr("Connect to Strava"))
            self.sync_btn.setEnabled(False)
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
