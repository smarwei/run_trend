"""
Manual/Help dialog window.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QPushButton, QLineEdit, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence, QTextCursor, QTextDocument
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

        # Search bar
        search_layout = QHBoxLayout()

        search_label = QLabel("Suchen:")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Text suchen... (Ctrl+F)")
        self.search_input.textChanged.connect(self._on_search)
        self.search_input.returnPressed.connect(self._find_next)
        search_layout.addWidget(self.search_input)

        self.prev_btn = QPushButton("◀ Zurück")
        self.prev_btn.clicked.connect(self._find_previous)
        search_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Weiter ▶")
        self.next_btn.clicked.connect(self._find_next)
        search_layout.addWidget(self.next_btn)

        self.match_label = QLabel("")
        search_layout.addWidget(self.match_label)

        layout.addLayout(search_layout)

        # Text browser for markdown content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        layout.addWidget(self.text_browser)

        # Close button
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        # Ctrl+F shortcut to focus search
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self._focus_search)

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

                # Get colors from system palette for dark mode support
                palette = self.text_browser.palette()
                text_color = palette.text().color().name()
                base_color = palette.base().color().name()
                highlight_color = palette.highlight().color().name()

                # Derive code background (slightly different from base)
                base_rgb = palette.base().color()
                if base_rgb.lightness() > 128:  # Light mode
                    code_bg = "#f4f4f4"
                    h1_color = "#2c3e50"
                    h2_color = "#34495e"
                    h3_color = "#7f8c8d"
                    strong_color = "#2c3e50"
                else:  # Dark mode
                    code_bg = f"rgba({base_rgb.red()}, {base_rgb.green()}, {base_rgb.blue()}, 0.5)"
                    h1_color = text_color
                    h2_color = text_color
                    h3_color = text_color
                    strong_color = highlight_color

                # Add some CSS styling with palette colors
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
                            color: {text_color};
                            background-color: {base_color};
                        }}
                        h1 {{
                            color: {h1_color};
                            border-bottom: 2px solid {highlight_color};
                            padding-bottom: 10px;
                        }}
                        h2 {{
                            color: {h2_color};
                            margin-top: 30px;
                        }}
                        h3 {{
                            color: {h3_color};
                        }}
                        code {{
                            background-color: {code_bg};
                            padding: 2px 6px;
                            border-radius: 3px;
                            color: {text_color};
                        }}
                        pre {{
                            background-color: {code_bg};
                            padding: 10px;
                            border-radius: 5px;
                            overflow-x: auto;
                            color: {text_color};
                        }}
                        ul, ol {{
                            margin-left: 20px;
                        }}
                        strong {{
                            color: {strong_color};
                        }}
                        a {{
                            color: {highlight_color};
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

    def _focus_search(self):
        """Focus the search input and select all text."""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _on_search(self, text):
        """Handle search text changes."""
        if not text:
            self.match_label.setText("")
            # Clear any highlights by finding empty string
            self.text_browser.find("")
            return

        # Start search from beginning
        cursor = self.text_browser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.text_browser.setTextCursor(cursor)

        # Find first occurrence
        found = self.text_browser.find(text)
        if found:
            self.match_label.setText("✓")
            self.match_label.setStyleSheet("color: green;")
        else:
            self.match_label.setText("Nicht gefunden")
            self.match_label.setStyleSheet("color: red;")

    def _find_next(self):
        """Find next occurrence of search text."""
        text = self.search_input.text()
        if text:
            found = self.text_browser.find(text)
            if not found:
                # Wrap around to beginning
                cursor = self.text_browser.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                self.text_browser.setTextCursor(cursor)
                self.text_browser.find(text)

    def _find_previous(self):
        """Find previous occurrence of search text."""
        text = self.search_input.text()
        if text:
            found = self.text_browser.find(text, QTextDocument.FindFlag.FindBackward)
            if not found:
                # Wrap around to end
                cursor = self.text_browser.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.text_browser.setTextCursor(cursor)
                self.text_browser.find(text, QTextDocument.FindFlag.FindBackward)
