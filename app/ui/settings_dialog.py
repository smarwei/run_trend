"""
Settings dialog for application configuration.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    """Settings dialog window."""

    def __init__(self, settings, parent=None, main_window=None):
        super().__init__(parent)
        self.settings = settings
        self.main_window = main_window
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Strava Settings Group
        strava_group = QGroupBox("Strava API Configuration")
        strava_layout = QFormLayout()

        # Client ID
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Your Strava API Client ID")
        strava_layout.addRow("Client ID:", self.client_id_input)

        # Client Secret
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        self.client_secret_input.setPlaceholderText("Your Strava API Client Secret")

        show_secret_btn = QPushButton("Show")
        show_secret_btn.setMaximumWidth(60)
        show_secret_btn.clicked.connect(self._toggle_secret_visibility)

        secret_layout = QHBoxLayout()
        secret_layout.addWidget(self.client_secret_input)
        secret_layout.addWidget(show_secret_btn)

        strava_layout.addRow("Client Secret:", secret_layout)

        # Info label
        info_label = QLabel(
            "Get your API credentials from:\n"
            "https://www.strava.com/settings/api\n\n"
            "After saving, use 'Connect to Strava' below to authorize."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        strava_layout.addRow("", info_label)

        strava_group.setLayout(strava_layout)
        layout.addWidget(strava_group)

        # Strava Actions Group
        actions_group = QGroupBox("Strava Actions")
        actions_layout = QVBoxLayout()

        # Connect/Disconnect button
        self.connect_btn = QPushButton("Connect to Strava")
        self.connect_btn.clicked.connect(self._handle_connect)
        actions_layout.addWidget(self.connect_btn)

        # Sync button
        self.sync_btn = QPushButton("Sync Activities")
        self.sync_btn.setEnabled(False)
        self.sync_btn.clicked.connect(self._handle_sync)
        actions_layout.addWidget(self.sync_btn)

        # Status label
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        actions_layout.addWidget(self.status_label)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # Update button states based on auth status
        self._update_auth_status()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
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

        self.client_id_input.setText(client_id)
        self.client_secret_input.setText(client_secret)

    def _save_settings(self):
        """Save settings and close dialog."""
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()

        if not client_id or not client_secret:
            reply = QMessageBox.question(
                self, "Missing Credentials",
                "Client ID and Secret are required. Do you want to save anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Save credentials
        self.settings.set('strava_client_id', client_id)
        self.settings.set('strava_client_secret', client_secret)

        QMessageBox.information(
            self, "Settings Saved",
            "API credentials saved successfully!\n\n"
            "Now click 'Connect to Strava' to authorize the application."
        )

        self.accept()

    def _update_auth_status(self):
        """Update UI based on authentication status."""
        if not self.main_window:
            return

        if self.main_window.auth and self.main_window.auth.is_authenticated():
            self.connect_btn.setText("Disconnect from Strava")
            self.sync_btn.setEnabled(True)
            self.status_label.setText("Connected to Strava")
            self.status_label.setStyleSheet("color: green; font-size: 10px; padding: 5px;")
        else:
            self.connect_btn.setText("Connect to Strava")
            self.sync_btn.setEnabled(False)
            self.status_label.setText("Not connected")
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
