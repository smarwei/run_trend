"""
Training status score calculation.
"""
from typing import List, Dict, Any
import numpy as np


class TrainingScoreCalculator:
    """Calculates composite training status score."""

    @staticmethod
    def calculate_scores(aggregates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate training scores for each period.

        Args:
            aggregates: List of period aggregates

        Returns:
            List of aggregates with added 'training_score' field
        """
        if not aggregates or len(aggregates) < 2:
            return aggregates

        # Extract metrics for normalization
        distances = [a['total_distance_km'] for a in aggregates]
        frequencies = [a['num_runs'] for a in aggregates]
        paces = [a['weighted_avg_pace_min_per_km'] for a in aggregates if a['weighted_avg_pace_min_per_km'] > 0]
        efficiencies = [a['efficiency_factor'] for a in aggregates if a.get('efficiency_factor', 0) > 0]

        # Calculate baseline values (rolling average approach)
        baseline_distance = np.mean(distances) if distances else 0
        baseline_frequency = np.mean(frequencies) if frequencies else 0
        baseline_pace = np.mean(paces) if paces else 0
        baseline_efficiency = np.mean(efficiencies) if efficiencies else 0

        # Avoid division by zero
        if baseline_distance == 0:
            baseline_distance = 1.0
        if baseline_frequency == 0:
            baseline_frequency = 1.0
        if baseline_pace == 0:
            baseline_pace = 6.0  # Default ~6 min/km
        if baseline_efficiency == 0:
            baseline_efficiency = 0.018  # Default ~0.018 (corresponds to ~2.78 m/s at 155 bpm)

        # Calculate scores for each period
        scored_aggregates = []

        for i, aggregate in enumerate(aggregates):
            # Use rolling baseline (average of all previous periods)
            if i >= 3:
                rolling_baseline_distance = np.mean(distances[:i])
                rolling_baseline_frequency = np.mean(frequencies[:i])
                rolling_paces = [aggregates[j]['weighted_avg_pace_min_per_km']
                               for j in range(i)
                               if aggregates[j]['weighted_avg_pace_min_per_km'] > 0]
                rolling_baseline_pace = np.mean(rolling_paces) if rolling_paces else baseline_pace
                rolling_efficiencies = [aggregates[j]['efficiency_factor']
                                       for j in range(i)
                                       if aggregates[j].get('efficiency_factor', 0) > 0]
                rolling_baseline_efficiency = np.mean(rolling_efficiencies) if rolling_efficiencies else baseline_efficiency
            else:
                rolling_baseline_distance = baseline_distance
                rolling_baseline_frequency = baseline_frequency
                rolling_baseline_pace = baseline_pace
                rolling_baseline_efficiency = baseline_efficiency

            # Normalize distance (higher is better)
            normalized_distance = aggregate['total_distance_km'] / rolling_baseline_distance
            normalized_distance = min(normalized_distance, 2.0)  # Cap at 2x baseline

            # Normalize frequency (higher is better)
            normalized_frequency = aggregate['num_runs'] / rolling_baseline_frequency
            normalized_frequency = min(normalized_frequency, 2.0)  # Cap at 2x baseline

            # Normalize pace (lower is better, so invert)
            current_pace = aggregate['weighted_avg_pace_min_per_km']
            if current_pace > 0:
                # Pace improvement: baseline / current (>1 means faster)
                pace_improvement = rolling_baseline_pace / current_pace
                normalized_pace = min(pace_improvement, 1.5)  # Cap at 1.5x improvement
            else:
                normalized_pace = 0.0

            # Normalize efficiency factor (higher is better)
            current_efficiency = aggregate.get('efficiency_factor', 0)
            has_hr_data = current_efficiency > 0

            if has_hr_data:
                # Efficiency improvement: current / baseline (>1 means better)
                normalized_efficiency = current_efficiency / rolling_baseline_efficiency
                normalized_efficiency = min(normalized_efficiency, 1.5)  # Cap at 1.5x improvement
            else:
                normalized_efficiency = 0.0

            # Compute composite score with new balanced weights
            # If no HR data available, adjust weights proportionally
            if has_hr_data:
                # New weights: Distance 30%, Frequency 20%, Pace 30%, Efficiency 20%
                training_score = (
                    0.30 * normalized_distance +
                    0.20 * normalized_frequency +
                    0.30 * normalized_pace +
                    0.20 * normalized_efficiency
                )
            else:
                # Fallback without HR: Distance 37.5%, Frequency 25%, Pace 37.5%
                # (proportionally adjusted: 30/80 = 37.5%, 20/80 = 25%, 30/80 = 37.5%)
                training_score = (
                    0.375 * normalized_distance +
                    0.250 * normalized_frequency +
                    0.375 * normalized_pace
                )

            # Scale to 0-100 range (assuming normalized values average around 1.0)
            training_score = min(max(training_score * 50, 0), 100)

            # Add score to aggregate
            scored_aggregate = aggregate.copy()
            scored_aggregate['training_score'] = training_score
            scored_aggregate['score_components'] = {
                'normalized_distance': normalized_distance,
                'normalized_frequency': normalized_frequency,
                'normalized_pace': normalized_pace,
                'normalized_efficiency': normalized_efficiency,
                'has_hr_data': has_hr_data
            }

            scored_aggregates.append(scored_aggregate)

        return scored_aggregates

    @staticmethod
    def get_score_explanation() -> str:
        """
        Get human-readable explanation of training score calculation.

        Returns:
            Explanation text
        """
        return """
Training Score Calculation:

The training score is a composite metric (0-100) reflecting your training progress.

Components (when HR data available):
• Distance (30%): Total distance compared to your baseline
• Pace (30%): Pace improvement compared to your baseline
• Efficiency Factor (20%): Aerobic fitness (pace-normalized HR)
• Frequency (20%): Number of runs compared to your baseline

Components (when HR data NOT available):
• Distance (37.5%): Total distance compared to your baseline
• Pace (37.5%): Pace improvement compared to your baseline
• Frequency (25%): Number of runs compared to your baseline

How it works:
- Score increases when you run more consistently
- Score increases when you increase distance sustainably
- Score increases when your pace improves (becomes faster)
- Score increases when your Efficiency Factor improves (better aerobic fitness)
- Baseline is computed from your historical rolling average
- Score is designed to not overreact to single workouts
- Weights adjust automatically when HR data is unavailable

Interpretation:
• 0-30: Below baseline, consider increasing volume/consistency
• 30-60: Around baseline, maintaining current level
• 60-80: Above baseline, making good progress
• 80-100: Significantly above baseline, excellent progress
""".strip()
