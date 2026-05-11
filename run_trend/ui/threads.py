"""
Background QThread subclasses used by MainWindow.

Extracted out of ``main_window.py`` (T36 slice 1) so the UI module stays
focused on widget composition. Each thread owns its own short-lived
``Database`` connection — SQLite handles must not be shared across
threads, so we open a fresh connection in ``run()`` and close it in the
``finally``.
"""
import logging

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class SyncThread(QThread):
    """Thread for running Strava sync operations."""

    progress = Signal(int, int, str)
    finished = Signal(dict)

    def __init__(self, db_path, client, sync_type, start_date=None):
        super().__init__()
        self.db_path = db_path
        self.client = client
        self.sync_type = sync_type
        self.start_date = start_date

    def run(self):
        # Create database connection in this thread — SQLite forbids
        # sharing a connection across threads.
        from ..storage.database import Database
        from ..sync.sync_manager import SyncManager

        db = Database(self.db_path)
        sync_manager = SyncManager(db, self.client)

        try:
            if self.sync_type == 'initial':
                stats = sync_manager.initial_sync(
                    self.start_date,
                    progress_callback=self.progress.emit,
                )
            else:
                stats = sync_manager.incremental_sync(
                    progress_callback=self.progress.emit,
                )
            self.finished.emit(stats)
        finally:
            db.close()


class HrZoneFetchThread(QThread):
    """Fetch HR-streams for a list of activities and cache the resulting zones.

    Runs in its own thread so the UI stays responsive during the (potentially
    many) Strava API calls. Each iteration emits ``progress(current, total)``;
    callers refresh the chart on ``finished_signal``.
    """

    progress = Signal(int, int)
    finished_signal = Signal()

    def __init__(self, db_path, client, settings_snapshot, activity_ids):
        super().__init__()
        self._db_path = db_path
        self._client = client
        self._settings_snapshot = dict(settings_snapshot)
        self._activity_ids = list(activity_ids)
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        from ..storage.database import Database
        from ..analytics.hr_zone_service import HrZoneService

        class _DictSettings:
            def __init__(self, d):
                self._d = d

            def get(self, key, default=None):
                return self._d.get(key, default)

        db = Database(self._db_path)
        try:
            svc = HrZoneService(
                db,
                _DictSettings(self._settings_snapshot),
                lambda aid: self._client.get_activity_streams(aid),
            )
            total = len(self._activity_ids)
            for i, aid in enumerate(self._activity_ids):
                if self._cancel:
                    break
                try:
                    svc.get_zone_seconds(aid)
                except Exception:  # noqa: BLE001 — never let one bad call kill the loop
                    logger.exception(
                        "HR-zone fetch failed for activity %s", aid
                    )
                self.progress.emit(i + 1, total)
        finally:
            db.close()
        self.finished_signal.emit()


class StravaAuthThread(QThread):
    """Run the blocking OAuth ``authorize`` call off the UI thread."""

    finished = Signal(bool)

    def __init__(self, auth, client_id, client_secret):
        super().__init__()
        self._auth = auth
        self._client_id = client_id
        self._client_secret = client_secret

    def run(self):
        result = self._auth.authorize(self._client_id, self._client_secret)
        self.finished.emit(result)


# Backwards-compatibility alias — _StravaAuthThread was the original
# private name inside main_window.py.
_StravaAuthThread = StravaAuthThread
