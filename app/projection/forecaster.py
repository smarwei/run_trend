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
        'Marathon': 42.195
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

        # Extract data for regression
        data_to_use = historical_data
        if use_recent_periods and use_recent_periods > 0:
            data_to_use = historical_data[-use_recent_periods:]

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
        period_type: str = 'week'
    ) -> Optional[Dict[str, Any]]:
        """
        Estimate when a milestone distance will be reached.

        Args:
            historical_data: List of period aggregates
            milestone_distance: Target distance in km
            period_type: 'week' or 'month'

        Returns:
            Dictionary with milestone estimate or None
        """
        if not historical_data or len(historical_data) < 2:
            return None

        # Use recent periods for more accurate prediction
        use_recent = min(12, len(historical_data))
        projection = Forecaster.project_trend(
            historical_data,
            'total_distance_km',
            periods_ahead=52,  # Look up to a year ahead
            use_recent_periods=use_recent
        )

        if not projection['has_projection']:
            return None

        slope = projection['slope']
        intercept = projection['intercept']

        # Current period index
        last_period_idx = len(historical_data) - 1

        # Find when projected value reaches milestone
        # y = slope * x + intercept
        # milestone = slope * x + intercept
        # x = (milestone - intercept) / slope

        if slope <= 0:
            # No positive trend, milestone won't be reached
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

        # Calculate estimated date
        last_period = historical_data[-1]
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
        period_type: str = 'week'
    ) -> Dict[str, Any]:
        """
        Get estimates for all standard milestones.

        Args:
            historical_data: List of period aggregates
            period_type: 'week' or 'month'

        Returns:
            Dictionary mapping milestone names to estimates
        """
        estimates = {}

        for milestone_name, distance_km in Forecaster.MILESTONES.items():
            estimate = Forecaster.estimate_milestone_date(
                historical_data,
                distance_km,
                period_type
            )
            estimates[milestone_name] = estimate

        return estimates
