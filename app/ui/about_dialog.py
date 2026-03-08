"""
About dialog for application information.
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AboutDialog(QDialog):
    """About dialog window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Run Trend")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # App name
        app_name = QLabel("Running Progress Tracker")
        app_name_font = QFont()
        app_name_font.setPointSize(16)
        app_name_font.setBold(True)
        app_name.setFont(app_name_font)
        app_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_name)

        # Version
        version = QLabel("Version 0.1.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: gray;")
        layout.addWidget(version)

        # Spacing
        layout.addSpacing(10)

        # Description
        description = QLabel(
            "A desktop application for tracking and analyzing\n"
            "running progress from Strava."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

        # Spacing
        layout.addSpacing(10)

        # Author
        author = QLabel("Entwickelt von Arne Weiß")
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)

        # Email
        email = QLabel('<a href="mailto:run-trend@arne-weiss.de">run-trend@arne-weiss.de</a>')
        email.setAlignment(Qt.AlignCenter)
        email.setOpenExternalLinks(True)
        layout.addWidget(email)

        # Spacing
        layout.addSpacing(10)

        # License
        license_label = QLabel("Lizenz: MIT + Commons Clause")
        license_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(license_label)

        # License info
        license_info = QLabel(
            "Freie Nutzung für private und nicht-kommerzielle Zwecke.\n"
            "Kommerzielle Vermarktung nicht erlaubt."
        )
        license_info.setAlignment(Qt.AlignCenter)
        license_info.setStyleSheet("color: gray; font-size: 10px;")
        license_info.setWordWrap(True)
        layout.addWidget(license_info)

        # GitHub (placeholder)
        github = QLabel(
            'Repository: <a href="https://github.com/your-username/run-trend">'
            'https://github.com/your-username/run-trend</a>'
        )
        github.setAlignment(Qt.AlignCenter)
        github.setOpenExternalLinks(True)
        github.setStyleSheet("font-size: 10px;")
        layout.addWidget(github)

        # Spacing
        layout.addSpacing(10)

        # Close button
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        close_btn.setMaximumWidth(100)
        close_btn.setDefault(True)

        # Center the button
        button_layout = QVBoxLayout()
        button_layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        layout.addLayout(button_layout)
