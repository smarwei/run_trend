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
            # Find MANUAL.md relative to this file
            manual_path = Path(__file__).parent.parent.parent / "MANUAL.md"

            if manual_path.exists():
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
                self.text_browser.setPlainText(
                    "MANUAL.md nicht gefunden.\n\n"
                    f"Erwartet in: {manual_path}"
                )
        except Exception as e:
            self.text_browser.setPlainText(
                f"Fehler beim Laden des Handbuchs:\n{e}"
            )
