"""
Regression guard for Ticket 28: source files must not call
``datetime.utcnow()`` (deprecated in Python 3.12, slated for removal).

Use ``datetime.now(timezone.utc).replace(tzinfo=None)`` for a drop-in
that preserves the existing naive-UTC ISO storage format.
"""
import unittest
from pathlib import Path


_SRC_DIR = Path(__file__).resolve().parent.parent / "run_trend"


class TestNoDatetimeUtcnow(unittest.TestCase):

    def test_sources_do_not_use_datetime_utcnow(self):
        offenders = []
        for path in _SRC_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                # Skip commented-out references (e.g. historical notes).
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                if "datetime.utcnow(" in line:
                    offenders.append(f"{path.relative_to(_SRC_DIR.parent)}:{lineno}")
        self.assertEqual(
            offenders,
            [],
            "datetime.utcnow() is deprecated; use "
            "datetime.now(timezone.utc).replace(tzinfo=None) instead. "
            f"Offending lines: {offenders!r}",
        )


if __name__ == "__main__":
    unittest.main()
