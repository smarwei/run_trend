"""
Race-Manager dialog: list, add, edit, and delete race markers (Ticket 15).
"""
from typing import Any, Dict, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .race_dialog import RaceDialog


class RaceManagerDialog(QDialog):
    """List all race markers, with Add/Edit/Delete actions."""

    COL_DATE = 0
    COL_NAME = 1
    COL_DISTANCE = 2
    COL_TIME = 3

    # Stash the marker id on the date cell so row→id stays correct after sort.
    MARKER_ID_ROLE = Qt.UserRole + 1

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle(self.tr("Manage Races"))
        self.setMinimumSize(560, 380)
        self._setup_ui()
        self._reload()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            self.tr("Date"),
            self.tr("Name"),
            self.tr("Distance (km)"),
            self.tr("Time"),
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        for col in (self.COL_DATE, self.COL_DISTANCE, self.COL_TIME):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        # Double-click on a row opens the Edit dialog.
        self.table.itemDoubleClicked.connect(lambda _i: self._edit_selected())
        layout.addWidget(self.table)

        action_row = QHBoxLayout()
        self.add_button = QPushButton(self.tr("Add…"))
        self.edit_button = QPushButton(self.tr("Edit…"))
        self.delete_button = QPushButton(self.tr("Delete"))
        self.add_button.clicked.connect(self._add)
        self.edit_button.clicked.connect(self._edit_selected)
        self.delete_button.clicked.connect(self._delete_selected)
        action_row.addWidget(self.add_button)
        action_row.addWidget(self.edit_button)
        action_row.addWidget(self.delete_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        close_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_box.rejected.connect(self.reject)
        layout.addWidget(close_box)

        self.table.itemSelectionChanged.connect(self._update_action_state)
        self._update_action_state()

    @staticmethod
    def _format_time(seconds: int) -> str:
        if seconds is None:
            return "—"
        seconds = int(seconds)
        if seconds <= 0:
            return "—"
        if seconds >= 3600:
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h}:{m:02d}:{s:02d}"
        m = seconds // 60
        s = seconds % 60
        return f"{m}:{s:02d}"

    @staticmethod
    def _format_distance(distance_km) -> str:
        if distance_km is None:
            return "—"
        return f"{float(distance_km):.2f}"

    def _reload(self):
        markers: List[Dict[str, Any]] = self.db.get_race_markers()
        self.table.setRowCount(len(markers))
        for row, m in enumerate(markers):
            date_item = QTableWidgetItem(m.get("date", ""))
            date_item.setData(self.MARKER_ID_ROLE, m.get("id"))
            self.table.setItem(row, self.COL_DATE, date_item)
            self.table.setItem(row, self.COL_NAME,
                               QTableWidgetItem(m.get("name", "")))
            self.table.setItem(row, self.COL_DISTANCE,
                               QTableWidgetItem(
                                   self._format_distance(m.get("distance_km"))
                               ))
            self.table.setItem(row, self.COL_TIME,
                               QTableWidgetItem(
                                   self._format_time(m.get("result_time"))
                               ))
        self._update_action_state()

    def _selected_marker(self) -> Dict[str, Any] | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        date_item = self.table.item(row, self.COL_DATE)
        if not date_item:
            return None
        marker_id = date_item.data(self.MARKER_ID_ROLE)
        if marker_id is None:
            return None
        # Re-fetch from DB so we always edit current data, not stale UI text.
        for m in self.db.get_race_markers():
            if m.get("id") == marker_id:
                return m
        return None

    def _update_action_state(self):
        enabled = self.table.currentRow() >= 0
        self.edit_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def _add(self):
        dialog = RaceDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.db.add_race_marker(
                date=data["date"],
                name=data["name"],
                distance_km=data["distance_km"],
                result_time=data["result_time"],
                notes=data["notes"],
            )
            self._reload()

    def _edit_selected(self):
        marker = self._selected_marker()
        if not marker:
            return
        dialog = RaceDialog(self, marker=marker)
        if dialog.exec():
            data = dialog.get_data()
            self.db.replace_race_marker(
                marker["id"],
                date=data["date"],
                name=data["name"],
                distance_km=data["distance_km"],
                result_time=data["result_time"],
                notes=data["notes"],
            )
            self._reload()

    def _delete_selected(self):
        marker = self._selected_marker()
        if not marker:
            return
        reply = QMessageBox.question(
            self,
            self.tr("Delete race"),
            self.tr("Delete '{}'? This cannot be undone.").format(
                marker.get("name", "")
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.db.delete_race_marker(marker["id"])
        self._reload()
