"""
Activity aggregation and metrics calculation.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict
import math


class ActivityAggregator:
    """Aggregates activities by time period and computes metrics."""

    @staticmethod
    def compute_per_activity_metrics(activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute derived metrics for a single activity.

        Args:
            activity: Activity data

        Returns:
            Dictionary with computed metrics
        """
        distance_m = activity.get('distance', 0.0)
        moving_time_s = activity.get('moving_time', 0)
        average_speed_ms = activity.get('average_speed', 0.0)

        # Convert to more useful units
        distance_km = distance_m / 1000.0
        moving_time_min = moving_time_s / 60.0
        moving_time_h = moving_time_s / 3600.0

        # Calculate pace (min/km)
        if distance_km > 0:
            pace_min_per_km = moving_time_min / distance_km
        else:
            pace_min_per_km = 0.0

        # Calculate speed (km/h)
        if average_speed_ms:
            speed_kmh = average_speed_ms * 3.6
        elif moving_time_h > 0:
            speed_kmh = distance_km / moving_time_h
        else:
            speed_kmh = 0.0

        return {
            'distance_km': distance_km,
            'pace_min_per_km': pace_min_per_km,
            'speed_kmh': speed_kmh,
            'duration_min': moving_time_min,
            'duration_h': moving_time_h
        }

    @staticmethod
    def aggregate_by_week(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate activities by week.

        Args:
            activities: List of activity dictionaries

        Returns:
            List of weekly aggregates
        """
        return ActivityAggregator._aggregate_by_period(activities, 'week')

    @staticmethod
    def aggregate_by_month(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate activities by month.

        Args:
            activities: List of activity dictionaries

        Returns:
            List of monthly aggregates
        """
        return ActivityAggregator._aggregate_by_period(activities, 'month')

    @staticmethod
    def _aggregate_by_period(activities: List[Dict[str, Any]], period: str) -> List[Dict[str, Any]]:
        """
        Aggregate activities by time period.

        Args:
            activities: List of activity dictionaries
            period: 'week' or 'month'

        Returns:
            List of period aggregates
        """
        if not activities:
            return []

        # Group activities by period
        period_groups = defaultdict(list)
        period_dates = {}  # Store period dates

        for activity in activities:
            start_date_str = activity['start_date']
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))

            if period == 'week':
                # Get ISO week (year, week_number)
                iso_cal = start_date.isocalendar()
                period_key = f"{iso_cal[0]}-W{iso_cal[1]:02d}"
                # Get Monday of that week for consistent date representation
                period_date = datetime.fromisocalendar(iso_cal[0], iso_cal[1], 1)
            else:  # month
                period_key = start_date.strftime('%Y-%m')
                period_date = datetime(start_date.year, start_date.month, 1)

            period_groups[period_key].append(activity)
            period_dates[period_key] = period_date

        # Compute aggregates for each period
        aggregates = []

        for period_key in sorted(period_groups.keys()):
            period_activities = period_groups[period_key]
            aggregate = ActivityAggregator._compute_period_aggregate(
                period_activities,
                period_key,
                period
            )
            aggregate['period_date'] = period_dates[period_key]
            aggregates.append(aggregate)

        return aggregates

    @staticmethod
    def _compute_period_aggregate(
        activities: List[Dict[str, Any]],
        period_key: str,
        period_type: str
    ) -> Dict[str, Any]:
        """
        Compute aggregate metrics for a period.

        Args:
            activities: Activities in the period
            period_key: Period identifier
            period_type: 'week' or 'month'

        Returns:
            Dictionary with aggregate metrics
        """
        if not activities:
            return {}

        # Calculate totals
        total_distance_m = sum(a.get('distance', 0.0) for a in activities)
        total_moving_time_s = sum(a.get('moving_time', 0) for a in activities)
        num_runs = len(activities)

        # Convert to useful units
        total_distance_km = total_distance_m / 1000.0
        total_moving_time_h = total_moving_time_s / 3600.0
        total_moving_time_min = total_moving_time_s / 60.0

        # Calculate averages
        avg_distance_km = total_distance_km / num_runs if num_runs > 0 else 0.0

        # Weighted average pace (total time / total distance)
        if total_distance_km > 0:
            weighted_avg_pace_min_per_km = total_moving_time_min / total_distance_km
            avg_speed_kmh = total_distance_km / total_moving_time_h if total_moving_time_h > 0 else 0.0
        else:
            weighted_avg_pace_min_per_km = 0.0
            avg_speed_kmh = 0.0

        # Find longest run
        longest_run_km = max((a.get('distance', 0.0) / 1000.0 for a in activities), default=0.0)

        # Calculate active days (unique dates)
        active_dates = set()
        for activity in activities:
            start_date_str = activity['start_date']
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            active_dates.add(start_date.date())

        num_active_days = len(active_dates)

        # Calculate consistency ratio (active days / days in period)
        if period_type == 'week':
            days_in_period = 7
        else:  # month - approximate
            # Use the date of first activity to determine month
            first_activity = min(activities, key=lambda a: a['start_date'])
            first_date = datetime.fromisoformat(first_activity['start_date'].replace('Z', '+00:00'))
            if first_date.month == 12:
                next_month = datetime(first_date.year + 1, 1, 1)
            else:
                next_month = datetime(first_date.year, first_date.month + 1, 1)
            days_in_period = (next_month - datetime(first_date.year, first_date.month, 1)).days

        consistency_ratio = num_active_days / days_in_period if days_in_period > 0 else 0.0

        # Determine period start date for sorting/display
        first_activity = min(activities, key=lambda a: a['start_date'])
        period_start_date = datetime.fromisoformat(first_activity['start_date'].replace('Z', '+00:00'))

        if period_type == 'week':
            iso_cal = period_start_date.isocalendar()
            period_start = datetime.fromisocalendar(iso_cal[0], iso_cal[1], 1)
        else:
            period_start = datetime(period_start_date.year, period_start_date.month, 1)

        return {
            'period': period_key,
            'period_start': period_start.isoformat(),
            'total_distance_km': total_distance_km,
            'num_runs': num_runs,
            'avg_distance_per_run_km': avg_distance_km,
            'weighted_avg_pace_min_per_km': weighted_avg_pace_min_per_km,
            'avg_speed_kmh': avg_speed_kmh,
            'total_moving_time_h': total_moving_time_h,
            'total_moving_time_min': total_moving_time_min,
            'longest_run_km': longest_run_km,
            'active_days': num_active_days,
            'consistency_ratio': consistency_ratio
        }
