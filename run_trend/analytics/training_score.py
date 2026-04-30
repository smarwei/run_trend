"""
Training status score calculation.
"""
from typing import List, Dict, Any
import numpy as np


# Minimum number of valid efficiency_factor samples required across the
# training history before EF contributes to the training score. Below this
# threshold we drop the EF component entirely and re-normalise the other
# weights — preferable to a synthetic default that biases the score for
# athletes without an established HR baseline.
MIN_EF_SAMPLES = 3


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

        # Filter to complete periods for baseline calculations
        # This ensures incomplete periods don't bias the baseline
        complete_aggregates = [a for a in aggregates if a.get('is_complete', True)]

        if not complete_aggregates:
            # If no complete periods, fall back to all aggregates
            complete_aggregates = aggregates

        # Extract metrics for normalization (from complete periods only)
        distances = [a['total_distance_km'] for a in complete_aggregates]
        frequencies = [a['num_runs'] for a in complete_aggregates]
        paces = [a['weighted_avg_pace_min_per_km'] for a in complete_aggregates if a['weighted_avg_pace_min_per_km'] > 0]
        efficiencies = [a['efficiency_factor'] for a in complete_aggregates if a.get('efficiency_factor', 0) > 0]

        # EF only contributes to the score when there are enough samples to
        # form a meaningful baseline; otherwise we drop it and re-normalise
        # the remaining weights instead of falling back to an arbitrary
        # default that systematically biases the score for new athletes.
        ef_history_sufficient = len(efficiencies) >= MIN_EF_SAMPLES

        # Calculate baseline values (rolling average approach)
        baseline_distance = np.mean(distances) if distances else 0
        baseline_frequency = np.mean(frequencies) if frequencies else 0
        baseline_pace = np.mean(paces) if paces else 0
        baseline_efficiency = np.mean(efficiencies) if ef_history_sufficient else 0

        # Avoid division by zero
        if baseline_distance == 0:
            baseline_distance = 1.0
        if baseline_frequency == 0:
            baseline_frequency = 1.0
        if baseline_pace == 0:
            baseline_pace = 6.0  # Default ~6 min/km
        # No fallback for baseline_efficiency: when ef_history_sufficient is
        # False we never divide by it because has_hr_data stays False.

        # Calculate scores for each period
        scored_aggregates = []

        for i, aggregate in enumerate(aggregates):
            # Use rolling baseline (average of all previous COMPLETE periods)
            # Filter previous periods to only complete ones for baseline
            complete_previous = [aggregates[j] for j in range(i) if aggregates[j].get('is_complete', True)]

            if len(complete_previous) >= 3:
                rolling_baseline_distance = np.mean([a['total_distance_km'] for a in complete_previous])
                rolling_baseline_frequency = np.mean([a['num_runs'] for a in complete_previous])
                rolling_paces = [a['weighted_avg_pace_min_per_km']
                               for a in complete_previous
                               if a['weighted_avg_pace_min_per_km'] > 0]
                rolling_baseline_pace = np.mean(rolling_paces) if rolling_paces else baseline_pace
                rolling_efficiencies = [a['efficiency_factor']
                                       for a in complete_previous
                                       if a.get('efficiency_factor', 0) > 0]
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
                normalized_pace = min(pace_improvement, 2.0)  # Cap at 2x improvement
            else:
                normalized_pace = 0.0

            # Normalize efficiency factor (higher is better).
            # EF contributes only when the period has HR-derived EF AND the
            # training history holds enough samples for a stable baseline
            # (see ef_history_sufficient above).
            current_efficiency = aggregate.get('efficiency_factor', 0)
            has_hr_data = ef_history_sufficient and current_efficiency > 0

            if has_hr_data:
                # Efficiency improvement: current / baseline (>1 means better)
                normalized_efficiency = current_efficiency / rolling_baseline_efficiency
                normalized_efficiency = min(normalized_efficiency, 2.0)  # Cap at 2x improvement
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
    def get_score_contributions(score_components: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Translate normalized score components into per-component contributions
        on the same 0-100 scale as the final training score.

        The score is computed as ``sum(weight_i * normalized_i) * 50``; this
        helper exposes ``weight_i * normalized_i * 50`` (current contribution)
        and ``weight_i * 2.0 * 50`` (maximum possible contribution given the
        2x cap) for each component, so the UI can show a breakdown without
        re-implementing the weighting rules.

        Args:
            score_components: dict produced in ``calculate_scores`` containing
                ``normalized_distance``, ``normalized_frequency``,
                ``normalized_pace``, ``normalized_efficiency``,
                ``has_hr_data``.

        Returns:
            Mapping ``{name: {'contribution', 'max', 'has_data'}}`` for the
            four components. When HR data is missing, the efficiency entry
            has ``has_data=False`` and a max of 0; the remaining three carry
            the rebalanced weights so their maxima still sum to 100.
        """
        if not score_components:
            return {}

        nd = score_components.get('normalized_distance', 0.0)
        nf = score_components.get('normalized_frequency', 0.0)
        np_ = score_components.get('normalized_pace', 0.0)
        ne = score_components.get('normalized_efficiency', 0.0)
        has_hr = bool(score_components.get('has_hr_data', False))

        if has_hr:
            weights = {'distance': 0.30, 'frequency': 0.20, 'pace': 0.30, 'efficiency': 0.20}
        else:
            weights = {'distance': 0.375, 'frequency': 0.250, 'pace': 0.375, 'efficiency': 0.0}

        return {
            'distance': {
                'contribution': weights['distance'] * nd * 50,
                'max': weights['distance'] * 2.0 * 50,
                'has_data': True,
            },
            'frequency': {
                'contribution': weights['frequency'] * nf * 50,
                'max': weights['frequency'] * 2.0 * 50,
                'has_data': True,
            },
            'pace': {
                'contribution': weights['pace'] * np_ * 50,
                'max': weights['pace'] * 2.0 * 50,
                'has_data': True,
            },
            'efficiency': {
                'contribution': weights['efficiency'] * ne * 50,
                'max': weights['efficiency'] * 2.0 * 50,
                'has_data': has_hr,
            },
        }

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

Components (when HR data NOT available, or fewer than 3 EF samples
in the training history):
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
- All metrics are capped at 2x their baseline, making 100 the true maximum

Interpretation:
• 0-30: Below baseline, consider increasing volume/consistency
• 30-60: Around baseline, maintaining current level
• 60-80: Above baseline, making good progress
• 80-100: Significantly above baseline, excellent progress
• 100: All metrics at 2x their historical baseline simultaneously
""".strip()
