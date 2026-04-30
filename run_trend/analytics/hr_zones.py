"""
Heart-rate zone analytics — pure functions, no I/O.

Computes zone boundaries from HR-Max (and optional HR-Rest for Karvonen)
and aggregates seconds spent in each zone from paired heartrate/time
streams as returned by Strava.

The 5-zone classic model is used by default; Karvonen (HRR-based) is
selected when ``hr_rest`` is provided AND ``scheme='karvonen'``.
"""
from typing import List, Optional, Sequence, Tuple, Dict

# Classic five-zone percentages of HR-Max.
# Source: ACSM / Strava-default ranges. Boundaries are inclusive on the low
# end and exclusive on the high end except for the last zone.
DEFAULT_ZONE_BOUNDS_PCT: List[Tuple[float, float]] = [
    (0.50, 0.60),   # Z1 — active recovery
    (0.60, 0.70),   # Z2 — endurance
    (0.70, 0.80),   # Z3 — tempo
    (0.80, 0.90),   # Z4 — threshold
    (0.90, 1.00),   # Z5 — vo2max
]

ZONE_LABELS: List[str] = ["Z1", "Z2", "Z3", "Z4", "Z5"]
NUM_ZONES: int = len(ZONE_LABELS)


def compute_zone_bounds(
    hr_max: int,
    hr_rest: Optional[int] = None,
    scheme: str = "classic",
) -> List[Tuple[int, int]]:
    """Return absolute BPM boundaries (inclusive low, exclusive high) per zone.

    classic:  bounds = pct × hr_max
    karvonen: bounds = pct × (hr_max − hr_rest) + hr_rest   (HRR-based)
    """
    if hr_max <= 0:
        raise ValueError("hr_max must be positive")
    if scheme == "karvonen":
        if hr_rest is None or hr_rest <= 0 or hr_rest >= hr_max:
            raise ValueError("karvonen scheme requires 0 < hr_rest < hr_max")
        reserve = hr_max - hr_rest
        return [
            (int(round(low * reserve + hr_rest)),
             int(round(high * reserve + hr_rest)))
            for low, high in DEFAULT_ZONE_BOUNDS_PCT
        ]
    return [
        (int(round(low * hr_max)), int(round(high * hr_max)))
        for low, high in DEFAULT_ZONE_BOUNDS_PCT
    ]


def zone_for_bpm(bpm: float, zone_bounds: Sequence[Tuple[int, int]]) -> int:
    """Return zone index 0..NUM_ZONES-1, or -1 if below the lowest zone.

    Values at or above the highest zone's upper bound clamp to the top zone
    (capturing brief HR spikes above HR-Max instead of dropping them).
    """
    if bpm < zone_bounds[0][0]:
        return -1
    for i, (low, high) in enumerate(zone_bounds):
        if i == len(zone_bounds) - 1:
            if bpm >= low:
                return i
        elif low <= bpm < high:
            return i
    return -1


def time_in_zones(
    hr_stream: Sequence[float],
    time_stream: Sequence[float],
    zone_bounds: Sequence[Tuple[int, int]],
) -> List[int]:
    """Aggregate seconds spent in each zone from paired streams.

    The two streams must be the same length. Each sample contributes the
    delta in seconds to the zone of its **starting** HR sample (left edge),
    consistent with how Strava emits time-series data. Samples below the
    lowest zone are ignored.
    """
    if len(hr_stream) != len(time_stream):
        raise ValueError("hr_stream and time_stream must be the same length")
    if len(hr_stream) < 2:
        return [0] * NUM_ZONES

    seconds = [0] * NUM_ZONES
    for i in range(len(hr_stream) - 1):
        dt = time_stream[i + 1] - time_stream[i]
        if dt <= 0:
            continue
        zone = zone_for_bpm(hr_stream[i], zone_bounds)
        if zone < 0:
            continue
        seconds[zone] += int(dt)
    return seconds


def aggregate_zone_seconds(per_activity: Sequence[Sequence[int]]) -> List[int]:
    """Sum a list of per-activity zone-seconds vectors element-wise."""
    totals = [0] * NUM_ZONES
    for vec in per_activity:
        if len(vec) != NUM_ZONES:
            continue
        for i, v in enumerate(vec):
            totals[i] += int(v)
    return totals


def polarized_ratio(zone_seconds: Sequence[int]) -> Dict[str, float]:
    """Return the 80/20 indicator as fractions in [0, 1].

    low    = Z1+Z2 fraction (target ~0.80 for endurance training)
    middle = Z3 fraction
    high   = Z4+Z5 fraction (target ~0.20)

    Returns zeros when no time is recorded.
    """
    total = sum(zone_seconds)
    if total <= 0:
        return {"low": 0.0, "middle": 0.0, "high": 0.0}
    low = (zone_seconds[0] + zone_seconds[1]) / total
    middle = zone_seconds[2] / total
    high = (zone_seconds[3] + zone_seconds[4]) / total
    return {"low": low, "middle": middle, "high": high}
