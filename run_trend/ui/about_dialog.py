"""
About dialog for application information.
"""
from importlib.metadata import version, PackageNotFoundError

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


def _read_app_version() -> str:
    """Read the installed package version.

    Falls back to "dev" when the package isn't installed (e.g. running
    straight from a source checkout without ``pip install .``). Keeping
    this outside the class avoids re-reading metadata on every dialog
    open, and gives tests an easy hook to patch.
    """
    try:
        return version("run-trend")
    except PackageNotFoundError:
        return "dev"


class AboutDialog(QDialog):
    """About dialog window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("About Run Trend"))
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # App name — kept as untranslated brand string.
        app_name = QLabel("Running Progress Tracker")
        app_name_font = QFont()
        app_name_font.setPointSize(16)
        app_name_font.setBold(True)
        app_name.setFont(app_name_font)
        app_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_name)

        version_label = QLabel(self.tr("Version {}").format(_read_app_version()))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: gray;")
        layout.addWidget(version_label)

        layout.addSpacing(10)

        description = QLabel(self.tr(
            "A desktop application for tracking and analyzing "
            "running progress from Strava."
        ))
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

        layout.addSpacing(10)

        author = QLabel(self.tr("Developed by Arne Weiß"))
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)

        # Mailto link kept as markup (no tr() — would translate the URL).
        email = QLabel(
            '<a href="mailto:run-trend@arne-weiss.de">run-trend@arne-weiss.de</a>'
        )
        email.setAlignment(Qt.AlignCenter)
        email.setOpenExternalLinks(True)
        layout.addWidget(email)

        layout.addSpacing(10)

        license_label = QLabel(self.tr("License: MIT + Commons Clause"))
        license_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(license_label)

        license_info = QLabel(self.tr(
            "Free for private, non-commercial use. "
            "Commercial distribution is not allowed."
        ))
        license_info.setAlignment(Qt.AlignCenter)
        license_info.setStyleSheet("color: gray; font-size: 10px;")
        license_info.setWordWrap(True)
        layout.addWidget(license_info)

        github = QLabel(
            self.tr("Repository: ")
            + '<a href="https://github.com/smarwei/run_trend">'
              'github.com/smarwei/run_trend</a>'
        )
        github.setAlignment(Qt.AlignCenter)
        github.setOpenExternalLinks(True)
        github.setStyleSheet("font-size: 10px;")
        layout.addWidget(github)

        layout.addSpacing(10)

        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setMaximumWidth(100)
        close_btn.setDefault(True)

        button_layout = QVBoxLayout()
        button_layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        layout.addLayout(button_layout)
