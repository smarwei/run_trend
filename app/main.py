#!/usr/bin/env python3
"""
Running Progress Tracker - Main entry point.

A desktop application for tracking running progress from Strava.
"""
import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    app.setApplicationName("Running Progress Tracker")
    app.setOrganizationName("RunTrend")
    app.setOrganizationDomain("runtrend.local")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
