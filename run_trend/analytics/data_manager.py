"""
DataManager: orchestrates the full data-processing pipeline.

Responsibilities:
  1. Aggregate raw activities into period summaries (week or month)
  2. Enrich with training scores
  3. Enrich with training load (ACWR) — O(n) algorithm
"""
from typing import Any, Dict, List

from .aggregator import ActivityAggregator
from .training_score import TrainingScoreCalculator
from .training_load import TrainingLoadCalculator


class DataManager:
    """Static helper that runs the aggregation + scoring + load pipeline."""

    @staticmethod
    def build_aggregates(
        activities: List[Dict[str, Any]],
        period: str = 'week',
    ) -> List[Dict[str, Any]]:
        """Run the full pipeline and return enriched aggregates.

        Args:
            activities: Raw activity dicts (as returned by the database).
            period:     'week' or 'month'.

        Returns:
            List of aggregate dicts with 'training_score' and 'training_load'
            fields populated where sufficient data exists.
        """
        if not activities:
            return []

        if period == 'week':
            aggregates = ActivityAggregator.aggregate_by_week(activities)
        else:
            aggregates = ActivityAggregator.aggregate_by_month(activities)

        aggregates = TrainingScoreCalculator.calculate_scores(aggregates)
        DataManager._calculate_all_training_loads(aggregates)
        return aggregates

    @staticmethod
    def _calculate_all_training_loads(aggregates: List[Dict[str, Any]]) -> None:
        """Populate 'training_load' on complete aggregates in-place (O(n)).

        Requires at least 5 complete periods before the first load value is
        written (index >= 4 within the complete-only sub-list).
        """
        complete = [agg for agg in aggregates if agg.get('is_complete', True)]
        for i, agg in enumerate(complete):
            if i >= 4:
                agg['training_load'] = TrainingLoadCalculator.calculate_training_load(
                    complete[:i + 1]
                )
