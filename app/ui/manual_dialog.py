"""
Manual/Help dialog window.
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PySide6.QtCore import Qt
from pathlib import Path
import markdown


class ManualDialog(QDialog):
    """Dialog showing the user manual."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Benutzerhandbuch")
        self.setMinimumSize(900, 700)
        self._setup_ui()
        self._load_manual()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Text browser for markdown content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        layout.addWidget(self.text_browser)

        # Close button
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_manual(self):
        """Load and display the manual."""
        try:
            # Find MANUAL.md - check multiple locations for packaged apps
            import sys

            # Try multiple possible locations
            search_paths = []

            # Briefcase: MANUAL.md is copied as source file alongside app module
            # It should be in the parent directory of the app module
            app_module_path = Path(__file__).parent.parent
            search_paths.append(app_module_path.parent / "MANUAL.md")

            # Development location (same as above for development)
            search_paths.append(Path(__file__).parent.parent.parent / "MANUAL.md")

            # PyInstaller location (if used)
            if getattr(sys, '_MEIPASS', None):
                search_paths.append(Path(sys._MEIPASS) / "MANUAL.md")

            # Find first existing path
            manual_path = None
            for path in search_paths:
                resolved = path.resolve()
                if resolved.exists():
                    manual_path = resolved
                    break

            if manual_path and manual_path.exists():
                with open(manual_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()

                # Convert markdown to HTML
                html_content = markdown.markdown(
                    markdown_content,
                    extensions=['extra', 'codehilite', 'toc']
                )

                # Add some CSS styling
                styled_html = f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            padding: 20px;
                            max-width: 800px;
                            margin: 0 auto;
                        }}
                        h1 {{
                            color: #2c3e50;
                            border-bottom: 2px solid #3498db;
                            padding-bottom: 10px;
                        }}
                        h2 {{
                            color: #34495e;
                            margin-top: 30px;
                        }}
                        h3 {{
                            color: #7f8c8d;
                        }}
                        code {{
                            background-color: #f4f4f4;
                            padding: 2px 6px;
                            border-radius: 3px;
                        }}
                        pre {{
                            background-color: #f4f4f4;
                            padding: 10px;
                            border-radius: 5px;
                            overflow-x: auto;
                        }}
                        ul, ol {{
                            margin-left: 20px;
                        }}
                        strong {{
                            color: #2c3e50;
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """

                self.text_browser.setHtml(styled_html)
            else:
                searched = "\n".join(f"  - {p}" for p in search_paths)
                self.text_browser.setPlainText(
                    "MANUAL.md nicht gefunden.\n\n"
                    f"Gesuchte Pfade:\n{searched}"
                )
        except Exception as e:
            self.text_browser.setPlainText(
                f"Fehler beim Laden des Handbuchs:\n{e}"
            )
