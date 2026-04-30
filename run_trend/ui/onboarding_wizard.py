"""First-run onboarding wizard.

Shown on first launch (no Strava auth + empty activity DB) and
manually reachable from the Help menu via "First-Run Wizard".
"""
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QLabel, QVBoxLayout, QPushButton, QDateEdit,
)
from PySide6.QtCore import Qt, QDate, QCoreApplication, Signal


def _tr(text: str) -> str:
    """Shared translation context for all wizard strings."""
    return QCoreApplication.translate("OnboardingWizard", text)


class _WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(_tr("Welcome to RunTrend"))
        self.setSubTitle(_tr(
            "Track your running progress over time with charts, "
            "trends, and projections."
        ))
        layout = QVBoxLayout(self)
        intro = QLabel(_tr(
            "RunTrend reads activities from your Strava account and shows "
            "long-term trends in distance, pace, heart rate, and training "
            "load. Three quick steps will get you set up."
        ))
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addStretch()


class _ConnectPage(QWizardPage):
    """Step 2 — start the Strava OAuth flow.

    Emits ``connect_clicked`` when the user presses the button. The wizard
    forwards it to the main window's existing OAuth flow and listens for
    completion via ``MainWindow.auth_finished``.
    """

    connect_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setTitle(_tr("Connect to Strava"))
        self.setSubTitle(_tr(
            "Authorize RunTrend to read your activities. "
            "Your browser will open the Strava authorization page."
        ))
        layout = QVBoxLayout(self)

        explanation = QLabel(_tr(
            "RunTrend only requests read-only access to your activities. "
            "You can disconnect at any time in Settings."
        ))
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        self._connect_button = QPushButton(_tr("Connect to Strava"))
        self._connect_button.clicked.connect(self.connect_clicked.emit)
        layout.addWidget(self._connect_button, alignment=Qt.AlignLeft)

        self._status_label = QLabel(_tr("Not connected yet."))
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet("color: gray;")
        layout.addWidget(self._status_label)
        layout.addStretch()

    def mark_pending(self):
        self._connect_button.setEnabled(False)
        self._status_label.setText(_tr("Waiting for Strava authorization…"))
        self._status_label.setStyleSheet("color: gray;")

    def mark_result(self, success: bool):
        if success:
            self._status_label.setText(_tr("✓ Connected to Strava."))
            self._status_label.setStyleSheet("color: green;")
            self._connect_button.setEnabled(False)
        else:
            self._status_label.setText(_tr(
                "Connection failed. You can retry or skip this step."
            ))
            self._status_label.setStyleSheet("color: red;")
            self._connect_button.setEnabled(True)


class _StartDatePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(_tr("Choose Training Start"))
        self.setSubTitle(_tr(
            "Pick the date from which RunTrend should import activities. "
            "You can change this later via the toolbar's Start Date picker."
        ))
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(_tr("Training Start Date:")))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate().addYears(-1))
        layout.addWidget(self.date_edit, alignment=Qt.AlignLeft)
        layout.addStretch()


class OnboardingWizard(QWizard):
    """First-run wizard guiding users through Strava connect + start date."""

    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window

        self.setWindowTitle(_tr("First-Run Setup"))
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        # The Cancel button doubles as "Skip" per ticket — the user can
        # close the wizard at any step without breaking the app.
        self.setButtonText(QWizard.CancelButton, _tr("Skip"))

        self.welcome_page = _WelcomePage()
        self.connect_page = _ConnectPage()
        self.start_date_page = _StartDatePage()

        self.addPage(self.welcome_page)
        self.addPage(self.connect_page)
        self.addPage(self.start_date_page)

        self.connect_page.connect_clicked.connect(self._on_connect_clicked)
        self.main_window.auth_finished.connect(self.connect_page.mark_result)

    def _on_connect_clicked(self):
        self.connect_page.mark_pending()
        self.main_window._authenticate_strava()

    @property
    def selected_start_date(self) -> QDate:
        return self.start_date_page.date_edit.date()
