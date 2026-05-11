"""
Smoke-tests for run_trend/ui/threads.py (Ticket 36 slice 1).

Verifies the public surface that survived the move from main_window.py:
the three thread classes exist, subclass QThread, and the legacy
``_StravaAuthThread`` alias still resolves.
"""
import unittest

from PySide6.QtCore import QThread

from run_trend.ui import threads


class TestThreadsModuleSurface(unittest.TestCase):

    def test_sync_thread_is_qthread(self):
        self.assertTrue(issubclass(threads.SyncThread, QThread))

    def test_hr_zone_fetch_thread_is_qthread(self):
        self.assertTrue(issubclass(threads.HrZoneFetchThread, QThread))

    def test_strava_auth_thread_is_qthread(self):
        self.assertTrue(issubclass(threads.StravaAuthThread, QThread))

    def test_legacy_underscore_alias_resolves(self):
        self.assertIs(threads._StravaAuthThread, threads.StravaAuthThread)

    def test_threads_re_exported_for_main_window(self):
        from run_trend.ui.main_window import (
            SyncThread, HrZoneFetchThread, StravaAuthThread,
        )
        self.assertIs(SyncThread, threads.SyncThread)
        self.assertIs(HrZoneFetchThread, threads.HrZoneFetchThread)
        self.assertIs(StravaAuthThread, threads.StravaAuthThread)


class TestThreadConstructors(unittest.TestCase):
    """Verify constructors capture their arguments without touching Qt's
    thread infrastructure (no .start() calls)."""

    def test_sync_thread_captures_args(self):
        t = threads.SyncThread(
            db_path='/tmp/x.db',
            client=object(),
            sync_type='initial',
            start_date=None,
        )
        self.assertEqual(t.db_path, '/tmp/x.db')
        self.assertEqual(t.sync_type, 'initial')

    def test_hr_zone_fetch_thread_cancel_flag(self):
        t = threads.HrZoneFetchThread(
            db_path='/tmp/x.db',
            client=object(),
            settings_snapshot={'foo': 'bar'},
            activity_ids=[1, 2, 3],
        )
        self.assertFalse(t._cancel)
        t.cancel()
        self.assertTrue(t._cancel)

    def test_hr_zone_fetch_thread_copies_inputs(self):
        snapshot = {'k': 1}
        ids = [10, 20]
        t = threads.HrZoneFetchThread(
            db_path='/tmp/x.db', client=object(),
            settings_snapshot=snapshot, activity_ids=ids,
        )
        # Inputs are copied — mutating originals doesn't leak in.
        snapshot['k'] = 999
        ids.append(99)
        self.assertEqual(t._settings_snapshot, {'k': 1})
        self.assertEqual(t._activity_ids, [10, 20])


if __name__ == '__main__':
    unittest.main()
