"""
Small reusable widgets for inline help/tooltip discovery.
"""
from PySide6.QtWidgets import QLabel, QToolTip
from PySide6.QtCore import Qt


class _HelpIcon(QLabel):
    """A '?' badge that shows its tooltip on hover *and* on click.

    QLabel ignores clicks by default, so clicking the badge does nothing
    on touch devices or after the hover-tooltip has timed out. Re-showing
    the same text on click makes the icon work without a modal popup.
    """

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            QToolTip.showText(event.globalPosition().toPoint(), self.toolTip(), self)
            event.accept()
            return
        super().mousePressEvent(event)


def make_help_icon(tooltip: str) -> QLabel:
    """Return a small '?' badge that explains a metric on hover or click.

    The badge is styled as a circular blue-bordered "?" so users can spot
    it next to a chart title or metric label.
    """
    label = _HelpIcon("?")
    label.setToolTip(tooltip)
    label.setAlignment(Qt.AlignCenter)
    label.setCursor(Qt.PointingHandCursor)
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
