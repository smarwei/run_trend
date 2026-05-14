"""
Training load calculation using ACWR (Acute:Chronic Workload Ratio).

Based on Gabbett et al. (2016) methodology for injury prevention.

T40 adds a daily-rolling variant (``daily_acwr_series`` /
``latest_acwr``) that walks day-by-day over a {date: load} map and
computes 7-day acute against 28-day chronic averages — the form used in
the original Gabbett paper. The older ``TrainingLoadCalculator``
class-based path operates on weekly aggregates and remains in place so
existing chart / aggregator code keeps working, but new UI callers
should prefer the daily variant.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Mapping, Optional

import numpy as np


# Threshold constants used by both the daily and the legacy ACWR paths.
# Kept at module level so the daily helpers don't have to reach into the
# class.
ACWR_SAFE_MIN = 0.8
ACWR_SAFE_MAX = 1.3
ACWR_CAUTION_MAX = 1.5


def _classify_acwr(acwr: float) -> str:
    """Map a single ACWR value to a coarse status bucket."""
    if acwr < ACWR_SAFE_MIN:
        return 'undertraining'
    if acwr <= ACWR_SAFE_MAX:
        return 'safe'
    if acwr <= ACWR_CAUTION_MAX:
        return 'caution'
    return 'danger'


def daily_acwr_series(
    daily_loads: Mapping[date, float],
    *,
    acute_window: int = 7,
    chronic_window: int = 28,
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Walk day-by-day over ``daily_loads`` and compute Gabbett ACWR.

    For each day ``t`` in ``[start, end]`` (defaults inferred from
    ``daily_loads`` keys):

        acute_t   = sum(load[t-acute_window+1 ... t])
        chronic_t = sum(load[t-chronic_window+1 ... t]) / (chronic_window / acute_window)
        acwr_t    = acute_t / chronic_t

    The chronic value is normalised to the same window length as the
    acute one — that's what makes the ratio dimensionally comparable
    (week-vs-week, not week-vs-month). For the default 7:28 windows the
    divisor is 4, i.e. chronic_t is the 28-day-mean *scaled* to weekly
    units.

    Cold-start: until day ``t`` has at least ``chronic_window`` days of
    history available (counting from the earliest known day, even with
    zero load), the entry's ``has_acwr`` is False. Same when chronic is
    zero (avoids the small-denominator artefact Impellizzeri 2020
    documents).

    Returns one record per day in the range:
        {'date', 'acute', 'chronic', 'acwr' | None, 'status' | None, 'has_acwr'}
    """
    if not daily_loads and (start is None or end is None):
        return []

    if start is None:
        start = min(daily_loads.keys())
    if end is None:
        end = max(daily_loads.keys())
    if end < start:
        return []

    # Expand the input dict to a list aligned with [start, end] so the
    # rolling-sum step doesn't need date arithmetic at every iteration.
    span = (end - start).days + 1
    loads = [float(daily_loads.get(start + timedelta(days=i), 0.0))
             for i in range(span)]

    # Normaliser converts the chronic sum-over-W_chronic into a unit
    # comparable to acute (sum-over-W_acute). For 7:28 → 4.0.
    chronic_divisor = chronic_window / acute_window

    series: List[Dict[str, Any]] = []
    for i in range(span):
        # Acute window: last ``acute_window`` days including today.
        a_lo = max(0, i - acute_window + 1)
        acute = sum(loads[a_lo:i + 1])
        # Chronic window: last ``chronic_window`` days including today.
        c_lo = max(0, i - chronic_window + 1)
        chronic_sum = sum(loads[c_lo:i + 1])
        chronic = chronic_sum / chronic_divisor

        # Cold-start: not enough history yet for the chronic window.
        has_full_chronic = (i + 1) >= chronic_window
        if not has_full_chronic or chronic <= 0:
            series.append({
                'date': start + timedelta(days=i),
                'acute': acute,
                'chronic': chronic,
                'acwr': None,
                'status': None,
                'has_acwr': False,
            })
            continue

        acwr = acute / chronic
        series.append({
            'date': start + timedelta(days=i),
            'acute': acute,
            'chronic': chronic,
            'acwr': acwr,
            'status': _classify_acwr(acwr),
            'has_acwr': True,
        })
    return series


def latest_acwr(
    daily_loads: Mapping[date, float],
    *,
    on_date: Optional[date] = None,
    acute_window: int = 7,
    chronic_window: int = 28,
) -> Dict[str, Any]:
    """Convenience: only today's ACWR record from the daily series.

    Returns ``{'has_acwr': False, 'message': ...}`` when the input is
    empty or the cold-start period hasn't elapsed. Otherwise returns
    the same shape as one entry of ``daily_acwr_series``.
    """
    if not daily_loads:
        return {
            'has_acwr': False,
            'acwr': None,
            'status': None,
            'message': 'No daily load data',
        }
    target = on_date or max(daily_loads.keys())
    start = min(daily_loads.keys())
    series = daily_acwr_series(
        daily_loads,
        acute_window=acute_window,
        chronic_window=chronic_window,
        start=start,
        end=target,
    )
    if not series:
        return {
            'has_acwr': False,
            'acwr': None,
            'status': None,
            'message': 'No data in range',
        }
    last = series[-1]
    if not last.get('has_acwr'):
        return {
            'has_acwr': False,
            'acwr': None,
            'status': None,
            'date': last['date'],
            'acute': last['acute'],
            'chronic': last['chronic'],
            'message': f'Need {chronic_window} days of history',
        }
    return last


def daily_distance_loads(activities: Iterable[Dict[str, Any]]) -> Dict[date, float]:
    """TRIMP-less fallback: per-day total distance in km as the "load".

    Used by the daily-ACWR path when the user hasn't set up the HR
    prerequisites (hr_rest / hr_max / gender) needed for Banister TRIMP.
    Distance is a coarser load proxy — it ignores intensity — but it
    still produces a reasonable ratio for users without HR data, and
    the tooltip flags which variant was used.
    """
    from datetime import datetime
    out: Dict[date, float] = {}
    for a in activities:
        dist_m = a.get('distance') or 0
        if dist_m <= 0:
            continue
        start_str = a.get('start_date')
        if not start_str:
            continue
        try:
            dt = datetime.fromisoformat(str(start_str).replace('Z', '+00:00'))
        except (ValueError, TypeError):
            continue
        day = dt.date()
        out[day] = out.get(day, 0.0) + (dist_m / 1000.0)
    return out


class TrainingLoadCalculator:
    """Calculate training load and overtraining risk using ACWR."""

    # ACWR thresholds (based on sport science research)
    ACWR_SAFE_MIN = 0.8
    ACWR_SAFE_MAX = 1.3
    ACWR_CAUTION_MAX = 1.5
    ACWR_DANGER = 1.5  # Above this = high injury/overtraining risk

    # Weights for composite score
    WEIGHT_DISTANCE = 0.40
    WEIGHT_PACE = 0.30
    WEIGHT_HR = 0.30

    @staticmethod
    def calculate_acwr(
        aggregates: List[Dict[str, Any]],
        metric_key: str,
        invert: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate ACWR for a specific metric.

        Args:
            aggregates: List of period aggregates (must be complete periods only!)
            metric_key: Key to extract metric (e.g., 'total_distance_km')
            invert: If True, invert metric (for pace: lower = better → higher = more load)

        Returns:
            Dictionary with ACWR value and status
        """
        # Need at least 5 complete weeks (1 acute + 4 chronic)
        if len(aggregates) < 5:
            return {
                'has_acwr': False,
                'acwr': 0.0,
                'message': 'Need at least 5 weeks of data for ACWR'
            }

        # Get acute (last week) and chronic (4 weeks before)
        acute_agg = aggregates[-1]
        chronic_aggs = aggregates[-5:-1]  # 4 weeks

        # Extract values
        acute_value = acute_agg.get(metric_key, 0.0)
        chronic_values = [agg.get(metric_key, 0.0) for agg in chronic_aggs]

        # Handle zero/missing values
        if acute_value == 0 or any(v == 0 for v in chronic_values):
            return {
                'has_acwr': False,
                'acwr': 0.0,
                'message': f'Missing data for {metric_key}'
            }

        # Invert if needed (for pace)
        if invert:
            acute_value = 1.0 / acute_value
            chronic_values = [1.0 / v for v in chronic_values]

        # Calculate chronic average
        chronic_avg = np.mean(chronic_values)

        # Calculate ACWR
        acwr = acute_value / chronic_avg

        # Classify status
        if acwr < TrainingLoadCalculator.ACWR_SAFE_MIN:
            status = 'undertraining'
        elif acwr <= TrainingLoadCalculator.ACWR_SAFE_MAX:
            status = 'safe'
        elif acwr <= TrainingLoadCalculator.ACWR_CAUTION_MAX:
            status = 'caution'
        else:
            status = 'danger'

        return {
            'has_acwr': True,
            'acwr': acwr,
            'status': status,
            'acute_value': acute_value,
            'chronic_avg': chronic_avg
        }

    @staticmethod
    def calculate_training_load(aggregates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate composite training load score (0-100) based on ACWR.

        Args:
            aggregates: List of period aggregates (already filtered to complete!)

        Returns:
            Dictionary with training load score, status, and warnings
        """
        if len(aggregates) < 5:
            return {
                'has_load': False,
                'training_load': 0.0,
                'status': 'insufficient_data',
                'message': 'Need at least 5 weeks of complete data',
                'components': {}
            }

        # Calculate ACWR for each component
        acwr_distance = TrainingLoadCalculator.calculate_acwr(
            aggregates, 'total_distance_km', invert=False
        )

        acwr_pace = TrainingLoadCalculator.calculate_acwr(
            aggregates, 'weighted_avg_pace_min_per_km', invert=True  # Invert!
        )

        # Heart rate (optional)
        has_hr_data = aggregates[-1].get('avg_heartrate', 0) > 0
        if has_hr_data:
            acwr_hr = TrainingLoadCalculator.calculate_acwr(
                aggregates, 'avg_heartrate', invert=False
            )
        else:
            acwr_hr = {'has_acwr': False, 'acwr': 1.0}

        # Check if we have minimum required data
        if not acwr_distance.get('has_acwr') or not acwr_pace.get('has_acwr'):
            return {
                'has_load': False,
                'training_load': 0.0,
                'status': 'insufficient_data',
                'message': 'Missing distance or pace data',
                'components': {}
            }

        # Calculate composite ACWR
        if has_hr_data and acwr_hr.get('has_acwr'):
            composite_acwr = (
                TrainingLoadCalculator.WEIGHT_DISTANCE * acwr_distance['acwr'] +
                TrainingLoadCalculator.WEIGHT_PACE * acwr_pace['acwr'] +
                TrainingLoadCalculator.WEIGHT_HR * acwr_hr['acwr']
            )
        else:
            # Fallback without HR: redistribute weights
            composite_acwr = (
                0.57 * acwr_distance['acwr'] +
                0.43 * acwr_pace['acwr']
            )

        # Map ACWR to 0-100 score
        # ACWR 0.8 → 40 (undertraining)
        # ACWR 1.0 → 50 (ideal)
        # ACWR 1.3 → 65 (upper safe limit)
        # ACWR 1.5 → 75 (warning threshold)
        # ACWR 2.0 → 100 (extreme)
        if composite_acwr <= 1.0:
            training_load = 50 * (composite_acwr / 1.0)
        else:
            training_load = 50 + 50 * ((composite_acwr - 1.0) / 1.0)

        training_load = min(max(training_load, 0), 100)

        # Determine status and warnings
        if training_load >= 90:
            status = 'danger'
            message = '⚠️ WARNUNG: Sehr hohes Übertraining-Risiko! Erwäge Regenerationswoche.'
        elif training_load >= 80:
            status = 'warning'
            message = '⚠ Erhöhtes Übertraining-Risiko. Reduziere Trainingsumfang oder Intensität.'
        elif training_load >= 70:
            status = 'caution'
            message = 'Vorsicht: Training nähert sich oberer Belastungsgrenze.'
        elif training_load >= 40:
            status = 'safe'
            message = 'Trainingsbelastung im optimalen Bereich.'
        else:
            status = 'undertraining'
            message = 'Trainingsbelastung niedrig. Erwäge Steigerung.'

        return {
            'has_load': True,
            'training_load': training_load,
            'composite_acwr': composite_acwr,
            'status': status,
            'message': message,
            'components': {
                'distance_acwr': acwr_distance['acwr'],
                'pace_acwr': acwr_pace['acwr'],
                'hr_acwr': acwr_hr.get('acwr', 0.0),
                'has_hr_data': has_hr_data
            }
        }

    @staticmethod
    def get_explanation() -> str:
        """Return explanation of Training Load metric."""
        return (
            "Training Load basiert auf ACWR (Acute:Chronic Workload Ratio).\n\n"
            "ACWR = Aktuelle Last (1 Woche) / Chronische Last (4 Wochen)\n\n"
            "Sicherer Bereich: 0.8-1.3 (Score 40-65)\n"
            "Erhöhtes Risiko: >1.5 (Score >80)\n\n"
            "Berechnet aus: Distanz (40%), Pace (30%), Herzfrequenz (30%)\n\n"
            "Wissenschaftliche Basis: Gabbett et al. (2016)"
        )
