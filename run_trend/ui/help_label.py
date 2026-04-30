"""
Small reusable widgets for inline help/tooltip discovery.
"""
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt


def make_help_icon(tooltip: str) -> QLabel:
    """Return a small '?' badge whose hover-tooltip explains a metric.

    The badge is styled as a circular blue-bordered "?" so users can spot
    it next to a chart title or metric label and hover to read the
    definition / formula / typical range.
    """
    label = QLabel("?")
    label.setToolTip(tooltip)
    label.setAlignment(Qt.AlignCenter)
    label.setCursor(Qt.WhatsThisCursor)
    label.setStyleSheet(
        "QLabel {"
        " color: #3498db;"
        " font-weight: bold;"
        " border: 1px solid #3498db;"
        " border-radius: 7px;"
        " min-width: 14px; max-width: 14px;"
        " min-height: 14px; max-height: 14px;"
        " font-size: 10px;"
        "}"
    )
    return label
