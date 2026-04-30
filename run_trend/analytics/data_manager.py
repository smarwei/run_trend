"""
DataManager: orchestrates the full data-processing pipeline.

Responsibilities:
  1. Aggregate raw activities into period summaries (week or month)
  2. Enrich with training scores
  3. Enrich with training load (ACWR) — O(n) algorithm
"""
from datetime import timedelta
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
    def align_previous_year_aggregates(
        aggregates: List[Dict[str, Any]],
        period: str = 'week',
    ) -> List[Dict[str, Any]]:
        """Shift aggregate ``period_date`` forward by ~1 year.

        Used by the year-over-year comparison toggle: prev-year aggregates
        are computed over the prior date window and then re-keyed onto the
        current x-axis so the chart can plot them next to current-year data.

        Weekly aggregates are shifted by 52 weeks (preserves Monday alignment);
        monthly aggregates jump to the same month of the next calendar year.
        """
        if not aggregates:
            return []

        aligned: List[Dict[str, Any]] = []
        for agg in aggregates:
            shifted = dict(agg)
            old_date = agg['period_date']
            if period == 'week':
                shifted['period_date'] = old_date + timedelta(weeks=52)
            else:
                try:
                    shifted['period_date'] = old_date.replace(year=old_date.year + 1)
                except ValueError:
                    # Feb 29 → Feb 28 in a non-leap target year.
                    shifted['period_date'] = old_date.replace(
                        year=old_date.year + 1, day=28
                    )
            aligned.append(shifted)
        return aligned

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
