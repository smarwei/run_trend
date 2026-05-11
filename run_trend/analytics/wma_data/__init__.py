"""
WMA 2023 age-grading reference data.

Two pieces live here:
- ``factors_2023.FACTORS`` — the WMA factor table (gender × distance × age).
- ``OPEN_WR_TIMES_S`` — open-class world-record times the factors are
  calibrated against. WMA-2023 was published in Feb 2023 using
  performances current at that time; we use the recent published WRs
  for each distance so the displayed age-graded % reflects today's
  open standard, not a frozen historical one.
"""
from .factors_2023 import FACTORS, DISTANCE_METRES, DISTANCE_LABELS


# Current world records in seconds. Track WRs for 5K/10K (WMA's columns
# are "5000m"/"10000m" — track distances), road WRs for HM and Marathon.
# Sources cross-checked 2026-05.
OPEN_WR_TIMES_S = {
    "male": {
        # 12:35.36, Joshua Cheptegei, Monaco, 2020-08-14 (track 5000m WR)
        "5000m": 755.36,
        # 26:11.00, Joshua Cheptegei, Valencia, 2020-10-07 (track 10000m WR)
        "10000m": 1571.00,
        # 57:20, Jacob Kiplimo, Lisbon, 2026-03-08 (half-marathon road WR)
        "HalfMarathon": 3440.0,
        # 2:00:35, Kelvin Kiptum, Chicago, 2023-10-08 (marathon road WR)
        "Marathon": 7235.0,
    },
    "female": {
        # 14:00.21, Beatrice Chebet, Eugene, 2024-05-25 (track 5000m WR)
        "5000m": 840.21,
        # 28:46.34, Beatrice Chebet, Eugene, 2024-05-25 (track 10000m WR)
        "10000m": 1726.34,
        # 1:02:52, Letesenbet Gidey, Valencia, 2021-10-24 (half-marathon road WR)
        "HalfMarathon": 3772.0,
        # 2:09:56, Ruth Chepngetich, Chicago, 2024-10-13 (marathon road WR)
        "Marathon": 7796.0,
    },
}


__all__ = [
    "FACTORS",
    "DISTANCE_METRES",
    "DISTANCE_LABELS",
    "OPEN_WR_TIMES_S",
]
