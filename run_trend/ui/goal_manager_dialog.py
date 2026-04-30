"""
Goal-Manager dialog: list, add, edit, delete, and toggle goals (Ticket 18).
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

from .goal_dialog import GoalDialog


class GoalManagerDialog(QDialog):
    """List all goals, with Add/Edit/Delete and Mark-Achieved actions."""

    COL_DATE = 0
    COL_DISTANCE = 1
    COL_TIME = 2
    COL_STATUS = 3

    GOAL_ID_ROLE = Qt.UserRole + 1

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle(self.tr("Manage Goals"))
        self.setMinimumSize(560, 380)
        self._setup_ui()
        self._reload()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            self.tr("Target date"),
            self.tr("Distance (km)"),
            self.tr("Target time"),
            self.tr("Status"),
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_STATUS, QHeaderView.Stretch)
        for col in (self.COL_DATE, self.COL_DISTANCE, self.COL_TIME):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.table.itemDoubleClicked.connect(lambda _i: self._edit_selected())
        layout.addWidget(self.table)

        action_row = QHBoxLayout()
        self.add_button = QPushButton(self.tr("Add…"))
        self.edit_button = QPushButton(self.tr("Edit…"))
        self.toggle_button = QPushButton(self.tr("Toggle Achieved"))
        self.delete_button = QPushButton(self.tr("Delete"))
        self.add_button.clicked.connect(self._add)
        self.edit_button.clicked.connect(self._edit_selected)
        self.toggle_button.clicked.connect(self._toggle_selected)
        self.delete_button.clicked.connect(self._delete_selected)
        action_row.addWidget(self.add_button)
        action_row.addWidget(self.edit_button)
        action_row.addWidget(self.toggle_button)
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

    def _format_status(self, achieved) -> str:
        return self.tr("Achieved") if achieved else self.tr("Active")

    def _reload(self):
        goals: List[Dict[str, Any]] = self.db.get_goals()
        self.table.setRowCount(len(goals))
        for row, g in enumerate(goals):
            date_item = QTableWidgetItem(g.get("target_date", ""))
            date_item.setData(self.GOAL_ID_ROLE, g.get("id"))
            self.table.setItem(row, self.COL_DATE, date_item)
            self.table.setItem(row, self.COL_DISTANCE,
                               QTableWidgetItem(
                                   self._format_distance(g.get("target_distance_km"))
                               ))
            self.table.setItem(row, self.COL_TIME,
                               QTableWidgetItem(
                                   self._format_time(g.get("target_time_seconds"))
                               ))
            self.table.setItem(row, self.COL_STATUS,
                               QTableWidgetItem(
                                   self._format_status(g.get("achieved"))
                               ))
        self._update_action_state()

    def _selected_goal(self) -> Dict[str, Any] | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        date_item = self.table.item(row, self.COL_DATE)
        if not date_item:
            return None
        goal_id = date_item.data(self.GOAL_ID_ROLE)
        if goal_id is None:
            return None
        for g in self.db.get_goals():
            if g.get("id") == goal_id:
                return g
        return None

    def _update_action_state(self):
        enabled = self.table.currentRow() >= 0
        self.edit_button.setEnabled(enabled)
        self.toggle_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def _add(self):
        dialog = GoalDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.db.add_goal(
                target_distance_km=data["target_distance_km"],
                target_time_seconds=data["target_time_seconds"],
                target_date=data["target_date"],
            )
            self._reload()

    def _edit_selected(self):
        goal = self._selected_goal()
        if not goal:
            return
        dialog = GoalDialog(self, goal=goal)
        if dialog.exec():
            data = dialog.get_data()
            self.db.update_goal(
                goal["id"],
                target_distance_km=data["target_distance_km"],
                target_time_seconds=data["target_time_seconds"],
                target_date=data["target_date"],
            )
            self._reload()

    def _toggle_selected(self):
        goal = self._selected_goal()
        if not goal:
            return
        new_state = not bool(goal.get("achieved"))
        self.db.update_goal(goal["id"], achieved=new_state)
        self._reload()

    def _delete_selected(self):
        goal = self._selected_goal()
        if not goal:
            return
        label = (
            f"{self._format_distance(goal.get('target_distance_km'))} km "
            f"@ {goal.get('target_date', '')}"
        )
        reply = QMessageBox.question(
            self,
            self.tr("Delete goal"),
            self.tr("Delete '{}'? This cannot be undone.").format(label),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.db.delete_goal(goal["id"])
        self._reload()
