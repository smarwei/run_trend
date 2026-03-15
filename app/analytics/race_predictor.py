"""
Race time prediction based on training data and heart rate zones.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics


class RacePredictor:
    """Predicts race times based on training pace and heart rate data."""

    # McMillan's pace differences from Easy Pace (in seconds per km)
    # These are conservative estimates based on McMillan's training zones
    MCMILLAN_ADJUSTMENTS = {
        '5K': -75,           # 5K pace ≈ Easy - 75 sec/km
        '10K': -60,          # 10K pace ≈ Easy - 60 sec/km
        'Half Marathon': -45,  # Half ≈ Easy - 45 sec/km
        'Marathon': -30      # Marathon ≈ Easy - 30 sec/km
    }

    # Easy run zone: 60-75% of HRmax (Zone 2, aerobic base)
    # This is the scientifically established Easy/Aerobic zone
    EASY_RUN_HR_MIN = 60  # % of HRmax
    EASY_RUN_HR_MAX = 75  # % of HRmax (Zone 2 upper limit)
    MIN_EASY_RUN_DISTANCE = 3.0  # km - minimum distance for reliable easy pace

    @staticmethod
    def identify_easy_runs(
        runs: List[Dict[str, Any]],
        max_hr: float,
        recent_months: int = 6,
        manual_hrmax: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Identify easy runs based on heart rate zones.

        Args:
            runs: List of individual run data
            max_hr: Maximum heart rate detected from activities
            recent_months: Only consider runs from last N months
            manual_hrmax: Manually configured HRmax (takes priority over detected)

        Returns:
            List of runs that qualify as easy runs
        """
        # Priority: Manual HRmax > Detected HRmax with safety margin
        if manual_hrmax and manual_hrmax > 0:
            # Use manual HRmax directly (no safety margin needed)
            estimated_true_hrmax = manual_hrmax
        elif max_hr and max_hr > 0:
            # Apply safety margin: Many runners never reach true HRmax in training
            # Detected max is often 10-15% below true max
            estimated_true_hrmax = max_hr * 1.10
        else:
            # No HRmax available
            return []

        # Calculate cutoff date (timezone-aware)
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=recent_months * 30)

        easy_runs = []

        for run in runs:
            # Check if run has required data
            avg_hr = run.get('average_heartrate', 0)
            distance = run.get('distance_km', 0)
            pace_min_per_km = run.get('pace_min_per_km', 0)

            if not avg_hr or not distance or not pace_min_per_km:
                continue

            # Check if run is recent enough
            start_date = run.get('start_date')
            if start_date:
                try:
                    run_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    if run_date < cutoff_date:
                        continue
                except (ValueError, AttributeError):
                    continue

            # Check if distance is sufficient
            if distance < RacePredictor.MIN_EASY_RUN_DISTANCE:
                continue

            # Calculate HR percentage (using estimated true HRmax)
            hr_percentage = (avg_hr / estimated_true_hrmax) * 100

            # Check if in Easy Run zone (Zone 2: 60-75%)
            if RacePredictor.EASY_RUN_HR_MIN <= hr_percentage <= RacePredictor.EASY_RUN_HR_MAX:
                easy_runs.append({
                    'distance': distance,
                    'pace_min_per_km': pace_min_per_km,
                    'hr_percentage': hr_percentage,
                    'date': start_date
                })

        return easy_runs

    @staticmethod
    def calculate_median_easy_pace(easy_runs: List[Dict[str, Any]]) -> Optional[float]:
        """
        Calculate median easy pace from identified easy runs.

        Args:
            easy_runs: List of easy run data

        Returns:
            Median pace in minutes per km, or None if insufficient data
        """
        if len(easy_runs) < 3:  # Need at least 3 easy runs for reliable estimate
            return None

        paces = [run['pace_min_per_km'] for run in easy_runs]
        return statistics.median(paces)

    @staticmethod
    def predict_race_times(
        easy_pace_min_per_km: float,
        efficiency_factor: Optional[float] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Predict race times using McMillan formula.

        Args:
            easy_pace_min_per_km: Median easy run pace
            efficiency_factor: Optional EF for adjustment

        Returns:
            Dictionary with predicted times for each distance
        """
        predictions = {}

        for race_name, adjustment_sec in RacePredictor.MCMILLAN_ADJUSTMENTS.items():
            # Convert easy pace to seconds per km
            easy_pace_sec_per_km = easy_pace_min_per_km * 60

            # Apply McMillan adjustment
            race_pace_sec_per_km = easy_pace_sec_per_km + adjustment_sec

            # Optional: Adjust based on efficiency factor
            # Higher EF suggests better aerobic efficiency → slightly faster race pace
            if efficiency_factor and efficiency_factor > 0:
                # For every 10% above baseline EF, reduce race pace by 1%
                # This is conservative - EF mainly affects endurance, not speed
                ef_bonus = min(0.05, (efficiency_factor - 0.015) / 0.015 * 0.01)
                race_pace_sec_per_km *= (1 - ef_bonus)

            # Convert back to min/km
            race_pace_min_per_km = race_pace_sec_per_km / 60

            # Calculate total race time based on distance
            distances = {
                '5K': 5.0,
                '10K': 10.0,
                'Half Marathon': 21.0975,
                'Marathon': 42.195
            }

            distance_km = distances[race_name]
            total_time_minutes = race_pace_min_per_km * distance_km

            predictions[race_name] = {
                'pace_min_per_km': race_pace_min_per_km,
                'total_time_minutes': total_time_minutes,
                'total_time_formatted': RacePredictor.format_time(total_time_minutes)
            }

        return predictions

    @staticmethod
    def format_time(minutes: float) -> str:
        """
        Format time in minutes to human-readable format.

        Args:
            minutes: Time in minutes

        Returns:
            Formatted string (e.g., "1:23:45" for marathon)
        """
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        secs = int((minutes % 1) * 60)

        if hours > 0:
            return f"{hours}:{mins:02d}:{secs:02d}"
        else:
            return f"{mins}:{secs:02d}"

    @staticmethod
    def format_pace(pace_min_per_km: float) -> str:
        """
        Format pace in min/km to readable format.

        Args:
            pace_min_per_km: Pace in minutes per kilometer

        Returns:
            Formatted string (e.g., "5:30")
        """
        mins = int(pace_min_per_km)
        secs = int((pace_min_per_km % 1) * 60)
        return f"{mins}:{secs:02d}"

    @staticmethod
    def _estimate_hrmax_from_regression(runs: List[Dict[str, Any]]) -> Optional[int]:
        """
        Estimate HRmax using linear regression on pace-HR relationship.

        Theory: As pace increases (faster running), HR increases linearly.
        By extrapolating to maximum effort (fastest sustainable pace),
        we can estimate HRmax.

        Args:
            runs: List of runs with pace_min_per_km and average_heartrate

        Returns:
            Estimated HRmax or None if not enough variation
        """
        # Extract pace-HR pairs
        pace_hr_pairs = []
        for r in runs:
            pace = r.get('pace_min_per_km')
            hr = r.get('average_heartrate')
            if pace and hr and hr > 0:
                # Use inverse pace (speed) for better linear relationship
                # Faster pace = lower min/km value = higher speed
                speed = 1.0 / pace  # km/min
                pace_hr_pairs.append((speed, hr))

        if len(pace_hr_pairs) < 5:
            return None

        # Simple linear regression: HR = a * speed + b
        n = len(pace_hr_pairs)
        sum_speed = sum(p[0] for p in pace_hr_pairs)
        sum_hr = sum(p[1] for p in pace_hr_pairs)
        sum_speed_hr = sum(p[0] * p[1] for p in pace_hr_pairs)
        sum_speed_sq = sum(p[0] ** 2 for p in pace_hr_pairs)

        # Calculate slope and intercept
        denominator = n * sum_speed_sq - sum_speed ** 2
        if abs(denominator) < 0.0001:  # Avoid division by zero
            return None

        slope = (n * sum_speed_hr - sum_speed * sum_hr) / denominator
        intercept = (sum_hr - slope * sum_speed) / n

        # Extrapolate to maximum speed
        # Use the fastest observed pace, then extrapolate 20% faster
        # This is more conservative than assuming a fixed 3:00 min/km pace
        max_observed_speed = max(p[0] for p in pace_hr_pairs)
        max_effort_speed = max_observed_speed * 1.20  # 20% faster than fastest training run

        estimated_hrmax = slope * max_effort_speed + intercept

        # Sanity check: should be between 150-230 bpm (extended upper range)
        if 150 <= estimated_hrmax <= 230:
            return int(estimated_hrmax)

        # If extrapolation is too high, try more conservative (10% faster)
        if estimated_hrmax > 230:
            max_effort_speed = max_observed_speed * 1.10
            estimated_hrmax = slope * max_effort_speed + intercept
            if 150 <= estimated_hrmax <= 230:
                return int(estimated_hrmax)

        return None

    @staticmethod
    def _estimate_hrmax_from_percentile(
        runs: List[Dict[str, Any]],
        hr_values: List[float]
    ) -> int:
        """
        Estimate HRmax using percentile-based approach.

        Theory: Use the slowest runs (highest pace values) to identify easy effort,
        then take 75th percentile of those HRs and assume it's 75% of HRmax.

        Args:
            runs: List of runs with pace_min_per_km
            hr_values: List of heart rate values

        Returns:
            Estimated HRmax
        """
        # Find median pace
        paces = [r.get('pace_min_per_km') for r in runs if r.get('pace_min_per_km')]
        if not paces:
            # Fallback: simple median HR = 70% HRmax
            median_hr = sorted(hr_values)[len(hr_values) // 2]
            return int(median_hr / 0.70)

        median_pace = sorted(paces)[len(paces) // 2]

        # Get HR values from slower-than-median runs (easier effort)
        easy_hrs = []
        for r in runs:
            pace = r.get('pace_min_per_km')
            hr = r.get('average_heartrate')
            if pace and hr and hr > 0 and pace >= median_pace:
                easy_hrs.append(hr)

        if len(easy_hrs) >= 5:
            # Use 75th percentile of easy run HRs
            sorted_hrs = sorted(easy_hrs)
            p75_hr = sorted_hrs[int(len(sorted_hrs) * 0.75)]
            # Assume 75th percentile is ~75% of HRmax
            return int(p75_hr / 0.75)
        else:
            # Fallback: median of all HRs = 70% HRmax
            median_hr = sorted(hr_values)[len(hr_values) // 2]
            return int(median_hr / 0.70)

    @staticmethod
    def check_hrmax_plausibility(
        detected_hrmax: float,
        runs: List[Dict[str, Any]],
        converted_runs: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if detected HRmax is plausible based on training data.

        Args:
            detected_hrmax: Maximum heart rate detected from activities
            runs: List of individual run data (raw format)
            converted_runs: Optional list of runs in RacePredictor format (with distance_km, pace_min_per_km)

        Returns:
            Dictionary with plausibility info and suggestion, or None if plausible
        """
        if not detected_hrmax or detected_hrmax <= 0:
            return None

        # Criterion 1: Detected HRmax too low (< 150 bpm is uncommon for runners)
        if detected_hrmax < 150:
            suggested_hrmax = 180  # Conservative default
            return {
                'is_plausible': False,
                'reason': 'detected_hrmax_too_low',
                'detected_hrmax': detected_hrmax,
                'suggested_hrmax': suggested_hrmax,
                'message': f'Detected HRmax ({detected_hrmax:.0f} bpm) is unusually low. '
                          f'Consider setting manual HRmax to ~{suggested_hrmax} bpm in Settings.'
            }

        # Count runs with HR data
        hr_values = []
        for r in runs:
            hr = r.get('average_heartrate')
            if hr is not None and hr > 0:
                hr_values.append(hr)

        if len(hr_values) < 10:
            return None  # Not enough data for reliable check

        # Criterion 2: Too few Easy Runs despite having enough data
        # This is more robust than checking if runs are "too intense"
        # Works for all training styles (Zone 2 only, mixed, tempo-heavy)
        if converted_runs:
            # Try to identify easy runs with current HRmax
            easy_runs = RacePredictor.identify_easy_runs(
                converted_runs,
                detected_hrmax,
                recent_months=6
            )

            # If we have 10+ runs with HR but find <3 Easy Runs:
            # Check if the median HR suggests the HRmax is too low
            if len(easy_runs) < 3:
                median_hr = sorted(hr_values)[len(hr_values) // 2]
                median_hr_percentage = (median_hr / detected_hrmax) * 100

                # Only warn if median HR is in the "Easy Run zone" (60-80%)
                # If median > 80%, the person likely does tempo/threshold training (no warning needed)
                if median_hr_percentage < 80:
                    # Hybrid approach: Try regression first, fallback to percentile

                    # Check if we have enough variation for regression
                    paces = [r.get('pace_min_per_km') for r in converted_runs if r.get('pace_min_per_km')]
                    if paces:
                        pace_range = max(paces) - min(paces)
                        hr_range = max(hr_values) - min(hr_values)

                        # If enough variation: try regression
                        if pace_range > 2.0 and hr_range > 30:
                            suggested_hrmax = RacePredictor._estimate_hrmax_from_regression(converted_runs)

                            # If regression failed or gave implausible result, use percentile
                            if not suggested_hrmax:
                                suggested_hrmax = RacePredictor._estimate_hrmax_from_percentile(
                                    converted_runs, hr_values
                                )
                        else:
                            # Not enough variation: use percentile method
                            suggested_hrmax = RacePredictor._estimate_hrmax_from_percentile(
                                converted_runs, hr_values
                            )
                    else:
                        # No pace data: simple median approach
                        suggested_hrmax = int(median_hr / 0.70)

                    return {
                        'is_plausible': False,
                        'reason': 'insufficient_easy_runs',
                        'detected_hrmax': detected_hrmax,
                        'suggested_hrmax': suggested_hrmax,
                        'easy_runs_found': len(easy_runs),
                        'total_runs': len(hr_values),
                        'message': f'Found only {len(easy_runs)} Easy Runs out of {len(hr_values)} runs. '
                                  f'Your detected HRmax ({detected_hrmax:.0f} bpm) may be too low. '
                                  f'Consider setting manual HRmax to ~{suggested_hrmax} bpm in Settings.'
                    }
                # Else: median HR > 80% → tempo/threshold runner, no warning

        return None  # Plausible

    @staticmethod
    def estimate_race_times(
        runs: List[Dict[str, Any]],
        max_hr: float,
        efficiency_factor: Optional[float] = None,
        recent_months: int = 6,
        manual_hrmax: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Main method: Estimate race times from training data.

        Args:
            runs: List of individual run data
            max_hr: Maximum heart rate detected from activities
            efficiency_factor: Current efficiency factor
            recent_months: Only use runs from last N months
            manual_hrmax: Manually configured HRmax (takes priority over detected)

        Returns:
            Dictionary with predictions and metadata, or None if insufficient data
        """
        # Step 1: Identify easy runs
        easy_runs = RacePredictor.identify_easy_runs(runs, max_hr, recent_months, manual_hrmax)

        if len(easy_runs) < 3:
            return {
                'has_prediction': False,
                'reason': 'insufficient_easy_runs',
                'message': f'Need at least 3 easy runs (3+ km, 60-75% HRmax). Found: {len(easy_runs)}'
            }

        # Step 2: Calculate median easy pace
        median_easy_pace = RacePredictor.calculate_median_easy_pace(easy_runs)

        if not median_easy_pace:
            return {
                'has_prediction': False,
                'reason': 'no_easy_pace',
                'message': 'Could not calculate easy pace'
            }

        # Step 3: Predict race times
        predictions = RacePredictor.predict_race_times(median_easy_pace, efficiency_factor)

        return {
            'has_prediction': True,
            'easy_runs_count': len(easy_runs),
            'median_easy_pace': median_easy_pace,
            'median_easy_pace_formatted': RacePredictor.format_pace(median_easy_pace),
            'predictions': predictions,
            'method': 'McMillan (HR-based)',
            'disclaimer': 'Estimate based on training pace. Actual race times may vary.'
        }
