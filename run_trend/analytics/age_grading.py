"""
Age-grading analytics (Ticket 37).

Pure functions only — no Qt, no DB, no I/O. Two methods:

* **WMA Age-Grading** (variant A) — performance compared to age-adjusted
  world-record using the published WMA 2023 factor tables.
* **HF physiology / personal-peak EF decline** (variant B) — measured
  Efficiency Factor compared to the user's own best 4-week-mean EF in
  the last 12 months, with expected decline derived from training-
  volume-coupled VO2max literature (Coppola et al. 2022).

See ``tickets/37-age-graded-performance.md`` for methodology and source
citations.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable, List, Optional, Tuple

from .wma_data import FACTORS, DISTANCE_METRES, OPEN_WR_TIMES_S


# Map RacePredictor's labels to WMA's column labels so the chart can pass
# the existing keys without translation.
_RACE_PREDICTOR_TO_WMA = {
    "5K": "5000m",
    "10K": "10000m",
    "Half Marathon": "HalfMarathon",
    "Marathon": "Marathon",
}


# Empirical VO2max-decline rates (per year, fraction) based on the
# training-volume meta-analysis in Coppola et al. 2022 (PMC9517884):
#   • volume maintained:        5–6.5 %/decade  → 0.0055/yr median
#   • moderate reduction (11–20%): 8–26 %/decade → 0.017/yr median
#   • sedentary (>20% reduction): 15–46 %/decade → 0.0305/yr median
#
# We interpolate between these anchors based on the user's recent
# ``current_volume / peak_volume`` ratio.
_DECLINE_RATE_ANCHORS = [
    (1.00, 0.00550),  # full volume maintained
    (0.80, 0.01700),  # moderate reduction
    (0.50, 0.03050),  # sedentary territory
    (0.00, 0.04600),  # extrapolated upper bound (fully detrained)
]


# ----------------------------- helpers ----------------------------- #

def age_on_date(birth: date, on_date: date) -> int:
    """Whole years elapsed between ``birth`` and ``on_date``.

    Handles the leap-year-Feb-29 edge case the same way most legal
    systems do: a person born 1996-02-29 turns 30 on 2026-03-01.
    """
    years = on_date.year - birth.year
    has_birthday_yet = (on_date.month, on_date.day) >= (birth.month, birth.day)
    if not has_birthday_yet:
        years -= 1
    return years


def tanaka_hrmax(age: int) -> float:
    """Estimate HRmax from age using Tanaka (2001): ``208 - 0.7 × age``.

    Meta-analytic regression over 351 studies / 18 712 subjects with
    r = -0.90; gender-independent and activity-independent.
    """
    return 208.0 - 0.7 * age


# ----------------------------- variant A ----------------------------- #

def wma_factor(distance_label: str, age: int, gender: str) -> Optional[float]:
    """Look up the WMA-2023 factor.

    Returns ``None`` for unsupported gender (e.g. ``"prefer-not-to-say"``);
    a missing or invalid age falls back to the table range (clamps to
    [min_age, max_age]).
    """
    if gender not in FACTORS:
        return None
    wma_label = _RACE_PREDICTOR_TO_WMA.get(distance_label, distance_label)
    if wma_label not in FACTORS[gender]:
        return None
    age_table = FACTORS[gender][wma_label]
    min_age, max_age = min(age_table), max(age_table)
    if age < min_age:
        return 1.0  # open class
    if age > max_age:
        age = max_age  # WMA tables top out; clamp
    return age_table[age]


def wma_percent(
    time_s: float, distance_label: str, age: int, gender: str,
) -> Optional[float]:
    """Compute the WMA age-graded percentage for a single race time.

    Formula (per WMA convention):

        percent = WR_time / (your_time × age_factor) × 100

    Returns ``None`` if the inputs don't permit a calculation (unknown
    gender, non-positive time, missing factor).
    """
    if not time_s or time_s <= 0:
        return None
    factor = wma_factor(distance_label, age, gender)
    if factor is None or factor <= 0:
        return None
    wma_label = _RACE_PREDICTOR_TO_WMA.get(distance_label, distance_label)
    wr = OPEN_WR_TIMES_S.get(gender, {}).get(wma_label)
    if wr is None:
        return None
    return wr / (time_s * factor) * 100.0


# ----------------------------- variant B ----------------------------- #

def vo2max_annual_decline_rate(volume_ratio: float) -> float:
    """Return expected fractional VO2max decline per year.

    ``volume_ratio`` is the user's recent training volume divided by
    their peak training volume in the reference window (range 0..1+).
    The piecewise-linear interpolation follows the literature anchors
    listed at the top of this module.
    """
    r = max(0.0, min(1.0, volume_ratio))
    # Walk anchors top-down (highest ratio first); interpolate within bracket.
    anchors = _DECLINE_RATE_ANCHORS  # already sorted high-to-low by ratio
    for i in range(len(anchors) - 1):
        hi_r, hi_d = anchors[i]
        lo_r, lo_d = anchors[i + 1]
        if r >= lo_r:
            # Linear blend: at hi_r → hi_d, at lo_r → lo_d.
            if hi_r == lo_r:
                return hi_d
            t = (hi_r - r) / (hi_r - lo_r)
            return hi_d + (lo_d - hi_d) * t
    return anchors[-1][1]


def personal_peak_ef(
    ef_dated: Iterable[Tuple[datetime, float]],
    *,
    window_weeks: int = 4,
    lookback_days: int = 365,
) -> Optional[Tuple[float, datetime]]:
    """Find the best rolling-mean EF in the last ``lookback_days``.

    ``ef_dated`` is an iterable of ``(period_date, ef_value)`` pairs
    (typically one per weekly aggregate). Returns the best mean EF over
    any contiguous ``window_weeks`` window inside the lookback range,
    together with the centre date of that window, or ``None`` if the
    history is too short.
    """
    samples = sorted(
        (d, v) for d, v in ef_dated if v is not None and v > 0
    )
    if not samples:
        return None

    cutoff = samples[-1][0] - timedelta(days=lookback_days)
    samples = [(d, v) for d, v in samples if d >= cutoff]
    if len(samples) < window_weeks:
        return None

    best_mean = None
    best_center: Optional[datetime] = None
    for i in range(len(samples) - window_weeks + 1):
        window = samples[i:i + window_weeks]
        mean = sum(v for _, v in window) / window_weeks
        center = window[window_weeks // 2][0]
        if best_mean is None or mean > best_mean:
            best_mean = mean
            best_center = center
    return (best_mean, best_center) if best_mean is not None else None


def expected_ef(
    peak_ef: float,
    peak_date: datetime,
    current_date: datetime,
    volume_ratio: float,
) -> float:
    """Forward-project EF from a personal peak applying the age-driven
    decline rate. Years between dates are treated as decimal years
    (365.25 days/yr)."""
    delta_days = (current_date - peak_date).days
    if delta_days <= 0:
        return peak_ef
    years = delta_days / 365.25
    rate = vo2max_annual_decline_rate(volume_ratio)
    return peak_ef * max(0.0, 1.0 - rate * years)


def aerobic_capacity_percent(
    measured_ef: float, expected_ef_value: float,
) -> Optional[float]:
    """Percent of expected EF the user is actually delivering."""
    if expected_ef_value is None or expected_ef_value <= 0:
        return None
    return measured_ef / expected_ef_value * 100.0
