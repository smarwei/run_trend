"""
Dialog for creating or editing a training goal (Ticket 18).
"""
from typing import Any, Dict, Optional

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QMessageBox,
    QTimeEdit,
    QVBoxLayout,
)


# Common race distances for the preset combo. The "Custom" entry switches the
# spin box back into editable mode for arbitrary distances.
_PRESETS = [
    ("5K", 5.0),
    ("10K", 10.0),
    ("15K", 15.0),
    ("Half Marathon", 21.0975),
    ("Marathon", 42.195),
]


class GoalDialog(QDialog):
    """Add or edit a goal.

    `goal` (optional) seeds the fields for edit mode.
    """

    def __init__(
        self,
        parent=None,
        goal: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(parent)
        self._goal = goal
        self.setWindowTitle(
            self.tr("Edit Goal") if goal else self.tr("New Goal")
        )
        self.setMinimumWidth(380)
        self._setup_ui()
        self._populate(goal)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.distance_combo = QComboBox()
        for label, _ in _PRESETS:
            self.distance_combo.addItem(label)
        self.distance_combo.addItem(self.tr("Custom"))
        self.distance_combo.currentIndexChanged.connect(self._on_preset_changed)
        form.addRow(self.tr("Distance:"), self.distance_combo)

        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(0.1, 999.999)
        self.distance_spin.setDecimals(3)
        self.distance_spin.setSingleStep(0.1)
        self.distance_spin.setSuffix(self.tr(" km"))
        form.addRow("", self.distance_spin)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setTime(QTime(1, 0, 0))
        form.addRow(self.tr("Target time:"), self.time_edit)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate().addMonths(3))
        form.addRow(self.tr("Target date:"), self.date_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Default to Half Marathon.
        self.distance_combo.setCurrentIndex(3)
        self._on_preset_changed(3)

    def _on_preset_changed(self, index: int):
        if 0 <= index < len(_PRESETS):
            _, km = _PRESETS[index]
            self.distance_spin.setValue(km)
            self.distance_spin.setEnabled(False)
        else:
            # "Custom" — let the user type a distance.
            self.distance_spin.setEnabled(True)

    def _populate(self, goal: Optional[Dict[str, Any]]):
        if not goal:
            return
        distance = float(goal.get("target_distance_km", 0.0))
        # Match a preset if the distance lines up; else switch to Custom.
        matched = next(
            (i for i, (_, km) in enumerate(_PRESETS) if abs(km - distance) < 1e-6),
            None,
        )
        if matched is not None:
            self.distance_combo.setCurrentIndex(matched)
        else:
            self.distance_combo.setCurrentIndex(len(_PRESETS))  # Custom
            self.distance_spin.setEnabled(True)
            self.distance_spin.setValue(distance)

        seconds = int(goal.get("target_time_seconds") or 0)
        if seconds > 0:
            self.time_edit.setTime(self._seconds_to_qtime(seconds))

        date_str = goal.get("target_date") or ""
        qd = QDate.fromString(date_str, "yyyy-MM-dd")
        if qd.isValid():
            self.date_edit.setDate(qd)

    @staticmethod
    def _seconds_to_qtime(seconds: int) -> QTime:
        seconds = max(0, int(seconds))
        seconds = min(seconds, 23 * 3600 + 59 * 60 + 59)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return QTime(h, m, s)

    @staticmethod
    def _qtime_to_seconds(t: QTime) -> int:
        return t.hour() * 3600 + t.minute() * 60 + t.second()

    def _on_accept(self):
        if self.distance_spin.value() <= 0:
            QMessageBox.warning(
                self,
                self.tr("Missing distance"),
                self.tr("Please enter a target distance."),
            )
            return
        if self._qtime_to_seconds(self.time_edit.time()) <= 0:
            QMessageBox.warning(
                self,
                self.tr("Missing target time"),
                self.tr("Please enter a target finish time."),
            )
            return
        self.accept()

    def get_data(self) -> Dict[str, Any]:
        """Return the field values. All three fields are required."""
        return {
            "target_distance_km": float(self.distance_spin.value()),
            "target_time_seconds": self._qtime_to_seconds(self.time_edit.time()),
            "target_date": self.date_edit.date().toString("yyyy-MM-dd"),
        }
