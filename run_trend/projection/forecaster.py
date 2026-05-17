"""
Projection and forecasting module for training trends.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np


class Forecaster:
    """Provides projection and forecasting for training metrics."""

    # Common milestone distances (km)
    MILESTONES = {
        '5K': 5.0,
        '10K': 10.0,
        'Half Marathon': 21.0975,
        'Marathon Ready': 32.0  # Standard marathon preparation long run (20 miles)
    }

    @staticmethod
    def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float]:
        """
        Compute linear regression coefficients.

        Args:
            x: Independent variable values
            y: Dependent variable values

        Returns:
            Tuple of (slope, intercept)
        """
        if not x or not y or len(x) != len(y) or len(x) < 2:
            return (0.0, 0.0)

        x_array = np.array(x)
        y_array = np.array(y)

        # Use numpy's polyfit for linear regression
        coefficients = np.polyfit(x_array, y_array, 1)
        slope = coefficients[0]
        intercept = coefficients[1]

        return (slope, intercept)

    @staticmethod
    def project_trend(
        historical_data: List[Dict[str, Any]],
        metric_key: str,
        periods_ahead: int = 12,
        use_recent_periods: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Project future trend based on historical data.

        Args:
            historical_data: List of period aggregates
            metric_key: Key of metric to project (e.g., 'total_distance_km')
            periods_ahead: Number of periods to project into future
            use_recent_periods: If set, only use this many recent periods for trend

        Returns:
            Dictionary with projection data
        """
        if not historical_data or len(historical_data) < 2:
            return {
                'has_projection': False,
                'message': 'Insufficient data for projection'
            }

        # Filter to complete periods only for accurate trend calculation
        # Incomplete periods would skew the regression line downward
        complete_data = [d for d in historical_data if d.get('is_complete', True)]

        if not complete_data or len(complete_data) < 2:
            return {
                'has_projection': False,
                'message': 'Insufficient complete periods for projection'
            }

        # Extract data for regression
        data_to_use = complete_data
        if use_recent_periods and use_recent_periods > 0:
            data_to_use = complete_data[-use_recent_periods:]

        if len(data_to_use) < 2:
            return {
                'has_projection': False,
                'message': 'Insufficient data for projection'
            }

        # Create x values (period indices)
        x_values = list(range(len(data_to_use)))
        y_values = [period.get(metric_key, 0.0) for period in data_to_use]

        # Compute linear regression
        slope, intercept = Forecaster.linear_regression(x_values, y_values)

        # Generate projections
        last_x = len(data_to_use) - 1
        projected_periods = []

        for i in range(1, periods_ahead + 1):
            x_proj = last_x + i
            y_proj = slope * x_proj + intercept

            # Don't allow negative projections
            y_proj = max(0.0, y_proj)

            projected_periods.append({
                'period_offset': i,
                'projected_value': y_proj
            })

        return {
            'has_projection': True,
            'slope': slope,
            'intercept': intercept,
            'projected_periods': projected_periods,
            'trend': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
        }

    @staticmethod
    def estimate_milestone_date(
        historical_data: List[Dict[str, Any]],
        milestone_distance: float,
        period_type: str = 'week',
        metric_key: str = 'total_distance_km'
    ) -> Optional[Dict[str, Any]]:
        """
        Estimate when a milestone distance will be reached.

        Args:
            historical_data: List of period aggregates
            milestone_distance: Target distance in km
            period_type: 'week' or 'month'
            metric_key: Metric to use ('total_distance_km' or 'longest_run_km')

        Returns:
            Dictionary with milestone estimate or None
        """
        if not historical_data or len(historical_data) < 2:
            return None

        # Filter to complete periods for milestone estimation
        complete_data = [d for d in historical_data if d.get('is_complete', True)]

        if not complete_data or len(complete_data) < 2:
            return None

        # Use recent periods for more accurate prediction
        use_recent = min(12, len(complete_data))
        projection = Forecaster.project_trend(
            complete_data,
            metric_key,
            periods_ahead=52,  # Look up to a year ahead
            use_recent_periods=use_recent
        )

        if not projection['has_projection']:
            return None

        slope = projection['slope']
        intercept = projection['intercept']

        # Current period index (based on complete data)
        last_period_idx = len(complete_data) - 1

        # Find when projected value reaches milestone
        # y = slope * x + intercept
        # milestone = slope * x + intercept
        # x = (milestone - intercept) / slope

        # Treat near-zero slopes as flat (numpy.polyfit on flat-y can return
        # ±1e-17 due to floating-point noise — without the epsilon, a tiny
        # positive slope blows up periods_until_milestone below to ~1e18
        # and overflows timedelta in C-int range).
        if slope <= 1e-9:
            # No meaningful positive trend, milestone won't be reached.
            return {
                'reachable': False,
                'message': 'Current trend is not increasing. Milestone may not be reached.'
            }

        periods_until_milestone = (milestone_distance - intercept) / slope - last_period_idx

        if periods_until_milestone <= 0:
            return {
                'reachable': True,
                'reached': True,
                'message': 'Milestone already reached!'
            }

        # Calculate estimated date (use last complete period)
        last_period = complete_data[-1]
        last_period_date = datetime.fromisoformat(last_period['period_start'])

        if period_type == 'week':
            estimated_date = last_period_date + timedelta(weeks=int(periods_until_milestone))
        else:  # month
            # Approximate months
            estimated_date = last_period_date + timedelta(days=int(periods_until_milestone * 30.44))

        return {
            'reachable': True,
            'reached': False,
            'periods_until': int(periods_until_milestone),
            'estimated_date': estimated_date.isoformat(),
            'milestone_km': milestone_distance
        }

    @staticmethod
    def get_milestone_estimates(
        historical_data: List[Dict[str, Any]],
        period_type: str = 'week',
        metric_key: str = 'total_distance_km'
    ) -> Dict[str, Any]:
        """
        Get estimates for all standard milestones.

        Args:
            historical_data: List of period aggregates
            period_type: 'week' or 'month'
            metric_key: Metric to use ('total_distance_km' for volume, 'longest_run_km' for long run)

        Returns:
            Dictionary mapping milestone names to estimates
        """
        estimates = {}

        for milestone_name, distance_km in Forecaster.MILESTONES.items():
            estimate = Forecaster.estimate_milestone_date(
                historical_data,
                distance_km,
                period_type,
                metric_key
            )
            estimates[milestone_name] = estimate

        return estimates

    # ------------------------------------------------------------------ #
    # Period-agnostic long-run projection (T42)                          #
    # ------------------------------------------------------------------ #
    #
    # The classic project_trend / estimate_milestone_date pipeline above
    # regresses on period-aggregated max values (longest_run per week or
    # per month). That makes the slope per-period and binds the result
    # to the user's chosen aggregation: a runner viewing the same data
    # in weekly and monthly mode gets dramatically different milestone
    # dates because the regressors are mathematically different
    # quantities (12 noisy weekly maxes vs. 4 high-leverage monthly
    # maxes of the same activities).
    #
    # The functions below project on the raw activity stream with a
    # day-axis instead, so the slope is km/day and unit-independent.
    # Theil-Sen replaces OLS for outlier resistance (a single PR run
    # no longer swings the trend). A long-run filter strips short
    # recovery runs that don't contribute to long-run progression.
    #
    # See tickets/42-projection-period-agnostic.md for the full
    # rationale, including the conversation with Garmin's approach
    # (Garmin estimates *state* via VO2max → race-time; it does not
    # extrapolate distance over time, which we acknowledge is a
    # poorly-posed problem and treat as a transparent heuristic).

    @staticmethod
    def _theil_sen(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float]:
        """Median of all pairwise slopes, then median intercept.

        Robust to ~30 % outlier contamination. Returns (slope, intercept)
        for the line y = slope * x + intercept. Requires at least two
        distinct x-values; falls back to (0, mean(ys)) on degenerate
        input.
        """
        n = len(xs)
        if n < 2:
            return (0.0, float(ys[0]) if n == 1 else 0.0)

        # Pairwise slopes via broadcasting; mask the diagonal + lower
        # triangle, then keep only finite values (same x => infinite).
        dx = xs[None, :] - xs[:, None]
        dy = ys[None, :] - ys[:, None]
        with np.errstate(divide='ignore', invalid='ignore'):
            slopes_matrix = dy / dx
        mask = np.triu(np.ones_like(slopes_matrix, dtype=bool), k=1) & np.isfinite(slopes_matrix)
        slopes = slopes_matrix[mask]
        if slopes.size == 0:
            return (0.0, float(np.median(ys)))

        slope = float(np.median(slopes))
        intercept = float(np.median(ys - slope * xs))
        return (slope, intercept)

    @staticmethod
    def project_long_run_trend(
        activities: List[Dict[str, Any]],
        *,
        long_run_min_km: float = 8.0,
        lookback_days: int = 84,
        now: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        """Period-agnostic Theil-Sen trend over recent long runs.

        Picks "long runs" as any activity at or above ``long_run_min_km``
        in the lookback window (default 12 weeks). Earlier iterations
        used an additional 75th-percentile filter, but that
        misclassified ramp-style long-run schedules with no shorter
        recovery runs: the percentile threshold collapsed to the
        upper quartile and discarded most of the actual progression.
        The simple floor is more predictable and matches how a coach
        would describe a long run ("anything 8+ km this season").

        Returns ``None`` when there isn't enough signal:
        - no activities, or fewer than 4 within the lookback window
        - fewer than 3 activities meet the long-run threshold

        Returned dict has keys:
            slope_km_per_day, intercept_km, first_long_run_date,
            last_long_run_date, last_long_run_km, max_long_run_km,
            long_runs_used, threshold_km
        """
        if not activities:
            return None

        now = now or datetime.now()
        cutoff = now - timedelta(days=lookback_days)

        # Parse and filter to the lookback window. Tz-aware ISO strings
        # are stripped to naive for arithmetic — RunTrend's stored
        # dates are local-day-aligned anyway, and a tz handling slip
        # would cause off-by-one-day errors in the milestone date.
        points: List[Tuple[datetime, float]] = []
        for a in activities:
            dist_m = a.get('distance') or 0
            if dist_m <= 0:
                continue
            ds = a.get('start_date')
            if not ds:
                continue
            try:
                dt = datetime.fromisoformat(str(ds).replace('Z', '+00:00'))
            except (ValueError, TypeError):
                continue
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            if dt < cutoff:
                continue
            points.append((dt, dist_m / 1000.0))

        if len(points) < 4:
            return None

        threshold = long_run_min_km
        long_runs = [(dt, d) for dt, d in points if d >= threshold]
        if len(long_runs) < 3:
            return None

        long_runs.sort(key=lambda pair: pair[0])
        first_dt = long_runs[0][0]
        last_dt, last_km = long_runs[-1]
        max_km = max(d for _, d in long_runs)

        # Reduce to PR-setting runs only. The user's long-run
        # capability is encoded in their progression of personal-best
        # long-runs, not in the noisy day-to-day distance of every
        # weekend run (where a 12 km recovery long-run can sit between
        # two 15 km PRs). Theil-Sen on the raw stream gets pulled
        # toward zero by all the "this week was shorter than last
        # week" pairs even when the underlying capability is growing.
        # Filtering to monotone-PR points captures the actual ceiling
        # growth rate, which is what a runner means when they ask
        # "when can I do my first 30 km run?".
        pr_runs: List[Tuple[datetime, float]] = []
        running_max = 0.0
        for dt, km in long_runs:
            if km > running_max:
                running_max = km
                pr_runs.append((dt, km))

        # < 3 PR-setting points means either total stagnation
        # (running_max never changed → 1 PR) or a single jump
        # followed by a plateau (2 PRs). Either way, no meaningful
        # positive trend can be regressed. Return a flat-trend dict
        # (slope=0) so downstream predict_milestone_date routes to
        # the honest "trend is flat" message rather than the chart
        # being unable to render at all.
        if len(pr_runs) < 3:
            slope = 0.0
            intercept = pr_runs[-1][1] if pr_runs else 0.0
        else:
            xs = np.array([(dt - first_dt).total_seconds() / 86400.0
                           for dt, _ in pr_runs])
            ys = np.array([d for _, d in pr_runs])
            slope, intercept = Forecaster._theil_sen(xs, ys)

        return {
            'slope_km_per_day': slope,
            'intercept_km': intercept,
            'first_long_run_date': first_dt,
            'last_long_run_date': last_dt,
            'last_long_run_km': last_km,
            'max_long_run_km': max_km,
            'long_runs_used': len(long_runs),
            'pr_runs_used': len(pr_runs),
            'threshold_km': threshold,
        }

    @staticmethod
    def predict_value_on_date(
        trend: Dict[str, Any], target_date: datetime,
    ) -> float:
        """Evaluate the Theil-Sen line at an arbitrary date."""
        days = (target_date - trend['first_long_run_date']).total_seconds() / 86400.0
        return trend['slope_km_per_day'] * days + trend['intercept_km']

    @staticmethod
    def predict_milestone_date(
        trend: Dict[str, Any],
        milestone_km: float,
        *,
        flat_slope_threshold: float = 1e-4,  # km/day ≈ <0.7 km/week
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Invert the Theil-Sen line: when does projected distance hit
        ``milestone_km``?

        Returns a dict matching the legacy estimate_milestone_date
        shape so chart / panel callers can swap cleanly:
            {'reachable': bool, 'reached': bool,
             'estimated_date': iso str | None,
             'milestone_km': float, 'message': str (when applicable)}
        """
        now = now or datetime.now()
        max_km = trend['max_long_run_km']

        if max_km >= milestone_km:
            return {
                'reachable': True,
                'reached': True,
                'milestone_km': milestone_km,
                'message': 'Milestone already reached',
            }

        slope = trend['slope_km_per_day']
        if slope <= flat_slope_threshold:
            return {
                'reachable': False,
                'reached': False,
                'milestone_km': milestone_km,
                'message': 'Long-run trend is flat — milestone date undefined',
            }

        intercept = trend['intercept_km']
        # Days from anchor where projected_value = milestone_km
        x_target = (milestone_km - intercept) / slope
        target_date = trend['first_long_run_date'] + timedelta(days=x_target)

        if target_date <= now:
            # Linear trend says we'd be there by now, but max isn't ⇒
            # we're sitting on a plateau between projection-line and
            # actual achievement. Honestly report that as undefined.
            return {
                'reachable': False,
                'reached': False,
                'milestone_km': milestone_km,
                'message': 'Trend has plateaued — projected date is past',
            }

        return {
            'reachable': True,
            'reached': False,
            'estimated_date': target_date.isoformat(),
            'milestone_km': milestone_km,
            'days_until': max(0, int((target_date - now).total_seconds() / 86400.0)),
        }
