"""
Activity export helpers.

CSV export writes the activity columns prescribed by ticket 12 in a
fixed order so coaches and external tools see a stable schema.
"""
import csv
from datetime import datetime
from typing import Iterable, Mapping, Any, Optional


CSV_COLUMNS = [
    "date",
    "distance_km",
    "duration_s",
    "pace_min_per_km",
    "avg_hr_bpm",
    "max_hr_bpm",
    "elevation_gain_m",
    "trainer",
    "manual",
]


def _format_date(start_date: Optional[str]) -> str:
    if not start_date:
        return ""
    try:
        return datetime.fromisoformat(start_date.replace("Z", "+00:00")).date().isoformat()
    except (TypeError, ValueError):
        return start_date


def _activity_row(activity: Mapping[str, Any]) -> dict:
    distance_m = activity.get("distance") or 0
    moving_time_s = activity.get("moving_time") or 0
    distance_km = distance_m / 1000.0 if distance_m else 0.0

    if distance_m and moving_time_s:
        pace = (moving_time_s / distance_m) * 1000.0 / 60.0
    else:
        pace = 0.0

    return {
        "date": _format_date(activity.get("start_date")),
        "distance_km": f"{distance_km:.3f}",
        "duration_s": int(moving_time_s) if moving_time_s else 0,
        "pace_min_per_km": f"{pace:.3f}" if pace else "",
        "avg_hr_bpm": activity.get("average_heartrate") or "",
        "max_hr_bpm": activity.get("max_heartrate") or "",
        "elevation_gain_m": activity.get("elevation_gain") or 0,
        "trainer": int(bool(activity.get("trainer"))),
        "manual": int(bool(activity.get("manual"))),
    }


def export_activities_csv(activities: Iterable[Mapping[str, Any]], path: str) -> int:
    """Write activities to a CSV file. Returns the number of rows written.

    The column order matches ``CSV_COLUMNS`` so downstream tools can rely
    on a stable schema; missing fields are emitted as empty strings or
    zero so spreadsheet apps don't choke on holes.
    """
    rows = [_activity_row(a) for a in activities]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def default_csv_filename(today: Optional[datetime] = None) -> str:
    """Return a date-stamped default filename like ``runtrend_export_2026-04-30.csv``."""
    today = today or datetime.now()
    return f"runtrend_export_{today.date().isoformat()}.csv"
