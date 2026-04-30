"""
Sortable table widget for individual runs.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from datetime import datetime, timezone
from typing import List, Dict, Any


class NumericTableItem(QTableWidgetItem):
    """QTableWidgetItem that sorts numerically instead of lexicographically."""

    def __init__(self, display_text: str, sort_value: float):
        super().__init__(display_text)
        self._sort_value = sort_value

    def __lt__(self, other: "NumericTableItem") -> bool:
        try:
            return self._sort_value < other._sort_value
        except (AttributeError, TypeError):
            return super().__lt__(other)


class RunsTable(QWidget):
    """Table widget showing individual runs with sortable columns."""

    COL_DATE = 0
    COL_NAME = 1
    COL_DISTANCE = 2
    COL_DURATION = 3
    COL_PACE = 4
    COL_ELEVATION = 5
    COL_AVG_HR = 6
    COL_MAX_HR = 7

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            self.tr("Date"),
            self.tr("Name"),
            self.tr("Distance (km)"),
            self.tr("Duration"),
            self.tr("Pace (min/km)"),
            self.tr("Elevation (m)"),
            self.tr("Avg HR (bpm)"),
            self.tr("Max HR (bpm)"),
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        for col in (self.COL_DATE, self.COL_DISTANCE, self.COL_DURATION,
                    self.COL_PACE, self.COL_ELEVATION, self.COL_AVG_HR, self.COL_MAX_HR):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

    @staticmethod
    def _format_duration(seconds: int) -> str:
        if seconds >= 3600:
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h}:{m:02d}:{s:02d}"
        m = seconds // 60
        s = seconds % 60
        return f"{m}:{s:02d}"

    @staticmethod
    def _format_pace(moving_time_s: int, distance_m: float) -> tuple:
        """Return (display_str MM:SS/km, sort_value seconds/km)."""
        if distance_m <= 0:
            return "-", float("inf")
        pace_s_per_km = (moving_time_s / distance_m) * 1000.0
        m = int(pace_s_per_km) // 60
        s = int(pace_s_per_km) % 60
        return f"{m}:{s:02d}", pace_s_per_km

    @staticmethod
    def _parse_date(iso_str: str) -> tuple:
        """Return (DD.MM.YYYY display, unix timestamp sort key)."""
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return dt.strftime("%d.%m.%Y"), dt.timestamp()
        except (ValueError, AttributeError):
            return iso_str[:10], 0.0

    def update_table(self, activities: List[Dict[str, Any]]):
        if not activities:
            self.table.setRowCount(0)
            return

        # Disable sorting during fill to prevent index confusion
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(activities))

        for row, act in enumerate(activities):
            date_str, date_ts = self._parse_date(act.get("start_date", ""))
            dist_m = act.get("distance", 0) or 0
            dist_km = dist_m / 1000.0
            moving_time = act.get("moving_time", 0) or 0
            elevation = act.get("elevation_gain") or 0
            has_hr = act.get("has_heartrate", 0)
            avg_hr = act.get("average_heartrate")
            max_hr = act.get("max_heartrate")

            pace_str, pace_sort = self._format_pace(moving_time, dist_m)
            duration_str = self._format_duration(moving_time)

            self.table.setItem(row, self.COL_DATE,
                               NumericTableItem(date_str, date_ts))
            self.table.setItem(row, self.COL_NAME,
                               QTableWidgetItem(act.get("name", "")))
            self.table.setItem(row, self.COL_DISTANCE,
                               NumericTableItem(f"{dist_km:.2f}", dist_km))
            self.table.setItem(row, self.COL_DURATION,
                               NumericTableItem(duration_str, moving_time))
            self.table.setItem(row, self.COL_PACE,
                               NumericTableItem(pace_str, pace_sort))
            self.table.setItem(row, self.COL_ELEVATION,
                               NumericTableItem(f"{elevation:.0f}", elevation))

            if has_hr and avg_hr is not None:
                self.table.setItem(row, self.COL_AVG_HR,
                                   NumericTableItem(f"{avg_hr:.0f}", avg_hr))
            else:
                self.table.setItem(row, self.COL_AVG_HR,
                                   NumericTableItem("-", float("inf")))

            if has_hr and max_hr is not None:
                self.table.setItem(row, self.COL_MAX_HR,
                                   NumericTableItem(f"{max_hr:.0f}", max_hr))
            else:
                self.table.setItem(row, self.COL_MAX_HR,
                                   NumericTableItem("-", float("inf")))

        self.table.setSortingEnabled(True)
        # Default: newest run first
        self.table.sortItems(self.COL_DATE, Qt.DescendingOrder)
