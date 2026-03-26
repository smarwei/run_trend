#!/usr/bin/env python3
"""
Running Progress Tracker - Main entry point.

A desktop application for tracking running progress from Strava.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale
from run_trend.ui.main_window import MainWindow
from run_trend.settings.config import SettingsManager


def load_translations(app, settings):
    """
    Load translations based on settings or system locale.

    Args:
        app: QApplication instance
        settings: SettingsManager instance

    Returns:
        tuple: (language_code, translator) - language code and translator object
    """
    # Get language preference from settings (or None for auto-detect)
    lang_setting = settings.get('language', 'auto')

    # Determine language to use
    if lang_setting == 'auto':
        # Auto-detect from system locale
        system_locale = QLocale.system().name()  # e.g., "de_DE", "en_US"
        lang_code = system_locale.split('_')[0]  # Extract "de" or "en"
    else:
        lang_code = lang_setting

    # Default to English if not German
    if lang_code not in ['de', 'en']:
        lang_code = 'en'

    # Load translator for both German and English
    translator = QTranslator()

    # Get path to translations directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(app_dir, 'translations')
    translation_file = os.path.join(translations_dir, f'runtrend_{lang_code}.qm')

    # Load translation file
    if os.path.exists(translation_file):
        if translator.load(translation_file):
            app.installTranslator(translator)
            print(f"Loaded translations: {lang_code}")
        else:
            print(f"Failed to load translation file: {translation_file}")
    else:
        print(f"Translation file not found: {translation_file}")
        print(f"Looking in: {translations_dir}")

    return lang_code, translator


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    app.setApplicationName("Running Progress Tracker")
    app.setOrganizationName("RunTrend")
    app.setOrganizationDomain("runtrend.local")

    # Load settings to check language preference
    settings = SettingsManager()

    # Load translations based on settings/locale
    current_language, translator = load_translations(app, settings)

    # Keep translator alive by storing reference in app object
    # This prevents garbage collection
    app.translator = translator

    # Create and show main window
    window = MainWindow()
    window.current_language = current_language  # Store for manual dialog
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
