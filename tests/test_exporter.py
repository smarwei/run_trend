"""Tests for the activity CSV exporter."""
import csv
import os
import tempfile
import unittest
from datetime import datetime

from run_trend.io.exporter import (
    CSV_COLUMNS,
    default_csv_filename,
    export_activities_csv,
)


def _sample_activity(**overrides):
    base = {
        "strava_id": 1,
        "name": "Morning Run",
        "type": "Run",
        "start_date": "2026-04-30T08:00:00Z",
        "distance": 10000.0,
        "moving_time": 3000,
        "elapsed_time": 3100,
        "elevation_gain": 120.5,
        "average_heartrate": 145.5,
        "max_heartrate": 172.0,
        "trainer": 0,
        "manual": 0,
    }
    base.update(overrides)
    return base


class TestExportActivitiesCsv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False, mode="w"
        )
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def _read_rows(self):
        with open(self.path, encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    def test_writes_header_and_row(self):
        count = export_activities_csv([_sample_activity()], self.path)
        self.assertEqual(count, 1)

        rows = self._read_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows[0].keys()), CSV_COLUMNS)

        row = rows[0]
        self.assertEqual(row["date"], "2026-04-30")
        self.assertEqual(row["distance_km"], "10.000")
        self.assertEqual(row["duration_s"], "3000")
        # 3000 s / 10000 m = 0.3 s/m → 5.000 min/km
        self.assertEqual(row["pace_min_per_km"], "5.000")
        self.assertEqual(row["avg_hr_bpm"], "145.5")
        self.assertEqual(row["max_hr_bpm"], "172.0")
        self.assertEqual(row["elevation_gain_m"], "120.5")
        self.assertEqual(row["trainer"], "0")
        self.assertEqual(row["manual"], "0")

    def test_handles_missing_hr_and_elevation(self):
        activity = _sample_activity(
            average_heartrate=None,
            max_heartrate=None,
            elevation_gain=None,
        )
        export_activities_csv([activity], self.path)
        row = self._read_rows()[0]

        self.assertEqual(row["avg_hr_bpm"], "")
        self.assertEqual(row["max_hr_bpm"], "")
        # elevation_gain falls back to 0 so spreadsheet sums still work
        self.assertEqual(row["elevation_gain_m"], "0")

    def test_handles_zero_distance(self):
        activity = _sample_activity(distance=0, moving_time=0)
        export_activities_csv([activity], self.path)
        row = self._read_rows()[0]
        self.assertEqual(row["distance_km"], "0.000")
        self.assertEqual(row["duration_s"], "0")
        self.assertEqual(row["pace_min_per_km"], "")

    def test_writes_multiple_rows(self):
        activities = [_sample_activity(strava_id=i) for i in range(5)]
        count = export_activities_csv(activities, self.path)
        self.assertEqual(count, 5)
        self.assertEqual(len(self._read_rows()), 5)

    def test_trainer_and_manual_flags_are_emitted_as_ints(self):
        activity = _sample_activity(trainer=1, manual=1)
        export_activities_csv([activity], self.path)
        row = self._read_rows()[0]
        self.assertEqual(row["trainer"], "1")
        self.assertEqual(row["manual"], "1")


class TestDefaultCsvFilename(unittest.TestCase):
    def test_includes_iso_date(self):
        name = default_csv_filename(datetime(2026, 4, 30, 12, 0))
        self.assertEqual(name, "runtrend_export_2026-04-30.csv")

    def test_no_args_uses_today(self):
        name = default_csv_filename()
        self.assertTrue(name.startswith("runtrend_export_"))
        self.assertTrue(name.endswith(".csv"))


if __name__ == "__main__":
    unittest.main()
