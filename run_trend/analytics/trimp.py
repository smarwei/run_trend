"""
Heart-rate-based training-load metrics (Ticket 38).

Implements Banister's TRIMP (Training Impulse) for per-activity load and
Coggan's exponentially weighted CTL / ATL / TSB for fitness / fatigue /
form. The functions are pure — no DB, no Qt, no I/O — so they're easily
unit-testable and reusable from the summary pipeline or a future
Performance-Manager chart.

References:
- Banister, E. W. (1991). "Modeling Elite Athletic Performance".
- Coggan, A., "Training Stress Score and the Performance Manager".
- Methodology and rationale: ``tickets/38-training-fitness-ctl.md``.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional


# Banister's gender-specific exponential weighting factor on HRr.
# Reflects the lactate-response difference between sexes (Banister 1991).
_BANISTER_B_MALE = 1.92
_BANISTER_B_FEMALE = 1.67


# TSB form-zone boundaries (Coggan PM, in TRIMP/day equivalent units).
# Same shape as the published cycling PM zones; absolute values are
# qualitatively comparable since we use TRIMP (HR-based) where the
# original framework used TSS (power-based). The interpretation labels
# stay the same.
def tsb_zone(tsb: float) -> str:
    """Map a TSB value to a coarse form-state label.

    Five buckets, matching the Coggan PM ranges referenced in the ticket:
        > +25   "transitional" (detraining — too rested)
        +10..25 "race fresh"
        −10..10 "neutral"
        −20..-10 "productive overload"
        −30..-20 "approaching fatigue limit"
        ≤ −30   "overreaching"
    """
    if tsb > 25:
        return "transitional"
    if tsb > 10:
        return "race-fresh"
    if tsb > -10:
        return "neutral"
    if tsb > -20:
        return "productive"
    if tsb > -30:
        return "fatigue-limit"
    return "overreaching"


def banister_trimp(
    duration_min: float,
    avg_hr: float,
    hr_rest: int,
    hr_max: int,
    gender: str = "male",
) -> float:
    """Compute Banister TRIMP for a single activity.

    Formula:  TRIMP = duration_min × HRr × 0.64 × e^(b × HRr)
    with HRr = (HR_avg − HR_rest) / (HR_max − HR_rest), clamped to [0,1].
    b is 1.92 (men) or 1.67 (women); unrecognised gender values fall
    back to the male coefficient (the more conservative side for users
    who haven't set the field — matches the WMA-tab default in T37).

    Returns 0.0 for any invalid input (missing HR, hr_rest ≥ hr_max,
    zero duration). The caller treats that as "this activity doesn't
    contribute to today's load" rather than raising.
    """
    if duration_min <= 0 or avg_hr <= 0:
        return 0.0
    if hr_rest <= 0 or hr_max <= 0 or hr_rest >= hr_max:
        return 0.0

    hr_r = (avg_hr - hr_rest) / (hr_max - hr_rest)
    # Clamp away pathological inputs (HR below rest, HR above max).
    hr_r = max(0.0, min(1.0, hr_r))

    b = _BANISTER_B_FEMALE if gender == "female" else _BANISTER_B_MALE
    return duration_min * hr_r * 0.64 * math.exp(b * hr_r)


def daily_trimp_series(
    activities: Iterable[Dict[str, Any]],
    hr_rest: int,
    hr_max: int,
    gender: str = "male",
) -> Dict[date, float]:
    """Sum per-activity TRIMPs into a {date → total} map.

    ``activities`` is the standard Strava-shaped dict list with
    ``start_date`` (ISO string), ``moving_time`` (seconds), and
    ``average_heartrate``. Activities without HR or with unparseable
    dates are dropped silently — that's just "no contribution today",
    not an error.
    """
    out: Dict[date, float] = {}
    for a in activities:
        avg_hr = a.get('average_heartrate') or 0
        if not avg_hr:
            continue
        moving_time_s = a.get('moving_time') or 0
        if moving_time_s <= 0:
            continue
        start_str = a.get('start_date')
        if not start_str:
            continue
        try:
            dt = datetime.fromisoformat(str(start_str).replace('Z', '+00:00'))
        except (ValueError, TypeError):
            continue
        day = dt.date()
        load = banister_trimp(
            duration_min=moving_time_s / 60.0,
            avg_hr=float(avg_hr),
            hr_rest=hr_rest,
            hr_max=hr_max,
            gender=gender,
        )
        if load <= 0:
            continue
        out[day] = out.get(day, 0.0) + load
    return out


def compute_ctl_atl_series(
    daily_loads: Dict[date, float],
    start: Optional[date] = None,
    end: Optional[date] = None,
    ctl_window: int = 42,
    atl_window: int = 7,
    initial_ctl: float = 0.0,
    initial_atl: float = 0.0,
) -> List[Dict[str, Any]]:
    """Walk day-by-day from ``start`` to ``end`` applying the Coggan
    EWMA updates:

        CTL_t = CTL_{t-1} × (1 − 1/W_ctl) + load_t × (1/W_ctl)
        ATL_t = ATL_{t-1} × (1 − 1/W_atl) + load_t × (1/W_atl)
        TSB_t = CTL_t − ATL_t

    When ``start`` / ``end`` are omitted, the range is inferred from
    the keys of ``daily_loads``. Days without a recorded load are
    treated as 0 — that's the whole point of the EWMA, so fatigue and
    fitness decay during rest.

    Returns one record per day in [start, end].
    """
    if not daily_loads and (start is None or end is None):
        return []

    if start is None:
        start = min(daily_loads.keys())
    if end is None:
        end = max(daily_loads.keys())
    if end < start:
        return []

    alpha_ctl = 1.0 / ctl_window
    alpha_atl = 1.0 / atl_window
    ctl = initial_ctl
    atl = initial_atl

    series: List[Dict[str, Any]] = []
    day = start
    while day <= end:
        load = float(daily_loads.get(day, 0.0))
        ctl = ctl * (1.0 - alpha_ctl) + load * alpha_ctl
        atl = atl * (1.0 - alpha_atl) + load * alpha_atl
        tsb = ctl - atl
        series.append({
            'date': day,
            'load': load,
            'ctl': ctl,
            'atl': atl,
            'tsb': tsb,
        })
        day = day + timedelta(days=1)
    return series


def latest_fitness_state(
    daily_loads: Dict[date, float],
    *,
    on_date: Optional[date] = None,
    ctl_window: int = 42,
    atl_window: int = 7,
) -> Optional[Dict[str, Any]]:
    """Convenience wrapper: return only the *current* CTL/ATL/TSB.

    The EWMA needs the full history to converge correctly (especially
    cold-start when < 42 days of data); we run the walk and return the
    last day's state. ``on_date`` defaults to today.
    """
    if not daily_loads:
        return None
    target = on_date or date.today()
    start = min(daily_loads.keys())
    series = compute_ctl_atl_series(
        daily_loads, start=start, end=target,
        ctl_window=ctl_window, atl_window=atl_window,
    )
    if not series:
        return None
    last = series[-1]
    return {
        'date': last['date'],
        'ctl': last['ctl'],
        'atl': last['atl'],
        'tsb': last['tsb'],
        'zone': tsb_zone(last['tsb']),
        # Helpful in the UI: how many days of EWMA warm-up we have so
        # callers can show a "ramp-up" hint while < ctl_window days old.
        'days_of_history': (target - start).days + 1,
        'cold_start': (target - start).days + 1 < ctl_window,
    }
