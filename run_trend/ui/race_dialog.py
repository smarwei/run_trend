"""
Dialog for creating or editing a race marker (Ticket 15).
"""
from datetime import datetime
from typing import Any, Dict, Optional

from PySide6.QtCore import QDate, Qt, QTime
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
)


class RaceDialog(QDialog):
    """Add or edit a race marker.

    `marker` (optional) seeds the fields for edit mode. `activity` (optional)
    provides defaults from a selected run when adding from the runs table.
    """

    def __init__(
        self,
        parent=None,
        marker: Optional[Dict[str, Any]] = None,
        activity: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(parent)
        self._marker = marker
        self.setWindowTitle(
            self.tr("Edit Race") if marker else self.tr("Mark as Race")
        )
        self.setMinimumWidth(380)
        self._setup_ui()
        self._populate(marker=marker, activity=activity)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow(self.tr("Name:"), self.name_edit)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        form.addRow(self.tr("Date:"), self.date_edit)

        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(0.0, 999.999)
        self.distance_spin.setDecimals(3)
        self.distance_spin.setSingleStep(0.1)
        self.distance_spin.setSuffix(self.tr(" km"))
        self.distance_spin.setSpecialValueText(self.tr("not set"))
        form.addRow(self.tr("Distance:"), self.distance_spin)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setTime(QTime(0, 0, 0))
        form.addRow(self.tr("Result time:"), self.time_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(80)
        form.addRow(self.tr("Notes:"), self.notes_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(
        self,
        marker: Optional[Dict[str, Any]],
        activity: Optional[Dict[str, Any]],
    ):
        if marker:
            self.name_edit.setText(marker.get("name", "") or "")
            date_str = marker.get("date") or ""
            qd = QDate.fromString(date_str, "yyyy-MM-dd")
            if qd.isValid():
                self.date_edit.setDate(qd)
            distance = marker.get("distance_km")
            if distance is not None:
                self.distance_spin.setValue(float(distance))
            seconds = marker.get("result_time")
            if seconds is not None:
                self.time_edit.setTime(self._seconds_to_qtime(int(seconds)))
            self.notes_edit.setPlainText(marker.get("notes") or "")
            return

        if activity:
            # Prefill from an activity (the user picked "Mark as Race" on a row).
            iso = activity.get("start_date") or ""
            try:
                dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
                self.date_edit.setDate(QDate(dt.year, dt.month, dt.day))
            except (ValueError, TypeError):
                pass
            self.name_edit.setText(activity.get("name", "") or "")
            distance_m = activity.get("distance") or 0
            if distance_m:
                self.distance_spin.setValue(float(distance_m) / 1000.0)
            moving = int(activity.get("moving_time") or 0)
            if moving > 0:
                self.time_edit.setTime(self._seconds_to_qtime(moving))

    @staticmethod
    def _seconds_to_qtime(seconds: int) -> QTime:
        seconds = max(0, int(seconds))
        # QTime wraps after 24h; clamp to fit the HH:mm:ss display.
        seconds = min(seconds, 23 * 3600 + 59 * 60 + 59)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return QTime(h, m, s)

    @staticmethod
    def _qtime_to_seconds(t: QTime) -> int:
        return t.hour() * 3600 + t.minute() * 60 + t.second()

    def _on_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self,
                self.tr("Missing name"),
                self.tr("Please enter a name for this race."),
            )
            self.name_edit.setFocus()
            return
        self.accept()

    def get_data(self) -> Dict[str, Any]:
        """Return the field values; optional fields may be None."""
        distance = self.distance_spin.value()
        result_seconds = self._qtime_to_seconds(self.time_edit.time())
        notes = self.notes_edit.toPlainText().strip()
        return {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "name": self.name_edit.text().strip(),
            "distance_km": distance if distance > 0 else None,
            "result_time": result_seconds if result_seconds > 0 else None,
            "notes": notes if notes else None,
        }
