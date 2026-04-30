"""
Lazy HR-zone fetcher with DB caching (Ticket 19).

Bridges three layers:
- ``AppSettings`` (HR-Max / HR-Rest / scheme),
- ``Database.activity_hr_zones`` cache,
- a stream-fetcher callable (typically ``StravaClient.get_activity_streams``).

Designed without direct dependencies on Qt or ``requests`` so it can be
unit-tested with plain dicts and lambdas.
"""
from typing import Any, Callable, Dict, List, Optional

from .hr_zones import (
    compute_zone_bounds,
    time_in_zones,
    NUM_ZONES,
)

StreamsFn = Callable[[int], Optional[Dict[str, List[Any]]]]


class HrZoneService:
    """Resolves per-activity zone seconds, hitting Strava only on cache miss."""

    def __init__(self, db, settings, fetch_streams: StreamsFn):
        self.db = db
        self.settings = settings
        self.fetch_streams = fetch_streams

    # ------------------------------------------------------------------
    # Config resolution
    # ------------------------------------------------------------------

    def _resolve_config(self) -> Optional[Dict[str, Any]]:
        """Return the active HR config or None if HR-Max isn't usable.

        ``hr_max`` must be > 0 (no auto-detect fallback in this layer — the
        caller decides what to show in that case). For Karvonen the
        ``hr_rest`` must be set to a value strictly below ``hr_max``; if not,
        we silently downgrade to classic so the user still gets *some* data
        when the saved scheme is karvonen but rest HR is missing.
        """
        hr_max = int(self.settings.get('manual_hrmax', 0) or 0)
        if hr_max <= 0:
            return None
        hr_rest = int(self.settings.get('hr_rest', 0) or 0)
        scheme = self.settings.get('hr_zone_scheme', 'classic') or 'classic'
        if scheme == 'karvonen' and (hr_rest <= 0 or hr_rest >= hr_max):
            scheme = 'classic'
        return {
            'hr_max': hr_max,
            'hr_rest': hr_rest if hr_rest > 0 else None,
            'scheme': scheme,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_zone_seconds(self, activity_id: int) -> Optional[List[int]]:
        """Return a 5-element seconds-per-zone vector for an activity.

        Returns ``None`` when:
        - HR-Max isn't configured,
        - the cached config matches but the activity has no stream data,
        - the streams fetcher returns nothing.
        """
        cfg = self._resolve_config()
        if cfg is None:
            return None

        cached = self.db.get_activity_hr_zones(activity_id)
        if cached is not None and self._cache_matches(cached, cfg):
            return [
                int(cached['z1_seconds']), int(cached['z2_seconds']),
                int(cached['z3_seconds']), int(cached['z4_seconds']),
                int(cached['z5_seconds']),
            ]

        streams = self.fetch_streams(activity_id)
        if not streams:
            return None
        hr = streams.get('heartrate')
        time_s = streams.get('time')
        if not hr or not time_s:
            return None

        bounds = compute_zone_bounds(
            cfg['hr_max'], hr_rest=cfg['hr_rest'], scheme=cfg['scheme'],
        )
        seconds = time_in_zones(hr, time_s, bounds)
        if len(seconds) != NUM_ZONES:
            return None

        self.db.upsert_activity_hr_zones(
            activity_id, seconds,
            hr_max_used=cfg['hr_max'],
            hr_rest_used=cfg['hr_rest'],
            scheme=cfg['scheme'],
        )
        return seconds

    @staticmethod
    def _cache_matches(cached: Dict[str, Any], cfg: Dict[str, Any]) -> bool:
        if int(cached.get('hr_max_used') or 0) != cfg['hr_max']:
            return False
        if (cached.get('scheme') or 'classic') != cfg['scheme']:
            return False
        cache_rest = cached.get('hr_rest_used')
        cache_rest = int(cache_rest) if cache_rest is not None else None
        if cache_rest != cfg['hr_rest']:
            return False
        return True
