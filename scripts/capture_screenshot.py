"""
One-off screenshot capture for the marketing site.

Boots a full MainWindow against the user's real activities.db, switches
to the Training Load tab (most visually distinctive feature added since
the last website screenshot), waits for the charts to lay out, and
saves a PNG to screenshots/main-window.png + a duplicate to
screenshot.png at repo root.

Run with the Wayland session active (uses QT_QPA_PLATFORM=offscreen
internally so the window doesn't actually appear).
"""
import os
import sys
from pathlib import Path

# Render off-screen — we only need the pixmap, not an actual window.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from PySide6.QtCore import QEventLoop, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


def pump(ms: int) -> None:
    """Spin the event loop for `ms` milliseconds so charts can lay out."""
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def find_tab_index(tab_widget, *needles: str) -> int:
    """Locate a tab whose label contains any of the needles (case-insensitive)."""
    for i in range(tab_widget.count()):
        label = tab_widget.tabText(i).lower()
        if any(n.lower() in label for n in needles):
            return i
    return -1


def main() -> None:
    app = QApplication(sys.argv)

    from run_trend.ui.main_window import MainWindow

    window = MainWindow()
    # Give the window a generous size so chart contents are readable.
    window.resize(1400, 900)
    window.show()

    # Let _load_data + initial chart updates run.
    pump(2500)

    # Switch to Training Load tab if available.
    target_idx = find_tab_index(window.tab_widget, "training load", "load")
    if target_idx >= 0:
        window.tab_widget.setCurrentIndex(target_idx)
        pump(1500)

    out_a = REPO / "screenshots" / "main-window.png"
    out_b = REPO / "screenshot.png"
    out_a.parent.mkdir(parents=True, exist_ok=True)

    pixmap = window.grab()
    if pixmap.isNull():
        sys.stderr.write("error: window.grab() returned a null pixmap\n")
        sys.exit(2)

    pixmap.save(str(out_a), "PNG")
    pixmap.save(str(out_b), "PNG")
    print(f"wrote {out_a}  ({pixmap.width()}x{pixmap.height()})")
    print(f"wrote {out_b}")

    # Tear down cleanly so background timers in MainWindow don't whine.
    if hasattr(window, "_status_refresh_timer"):
        window._status_refresh_timer.stop()
    window.deleteLater()


if __name__ == "__main__":
    main()
