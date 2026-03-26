"""
Training load calculation using ACWR (Acute:Chronic Workload Ratio).

Based on Gabbett et al. (2016) methodology for injury prevention.
"""
from typing import List, Dict, Any
import numpy as np


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
