"""
Repo-hygiene guards (Ticket 31).

These tests don't exercise application logic — they enforce that the
repository root stays tidy and that the developer-scratchpad files
introduced during day-to-day debugging don't accumulate at the root.
"""
import ast
import unittest
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent


class TestNoDebugScriptsAtRoot(unittest.TestCase):

    def test_root_does_not_contain_debug_scripts(self):
        offenders = sorted(p.name for p in _REPO_ROOT.glob("debug_*.py"))
        self.assertEqual(
            offenders,
            [],
            "debug_*.py scripts must live under scripts/dev/, not at the "
            f"repo root. Found: {offenders!r}",
        )

    def test_scripts_dev_directory_exists(self):
        scripts_dev = _REPO_ROOT / "scripts" / "dev"
        self.assertTrue(
            scripts_dev.is_dir(),
            f"{scripts_dev} should exist (created in T31).",
        )
        self.assertTrue(
            (scripts_dev / "README.md").is_file(),
            "scripts/dev/README.md should document what lives here.",
        )

    def test_moved_debug_scripts_parse_as_python(self):
        """The three migrated debug scripts had their `app.*` imports
        rewritten to `run_trend.*` during the move. Smoke-check that they
        at least parse — runtime correctness is out of scope, but syntax
        must hold."""
        for name in (
            "debug_hr_actual.py",
            "debug_hr_zones.py",
            "debug_race_predictions.py",
        ):
            path = _REPO_ROOT / "scripts" / "dev" / name
            with self.subTest(name=name):
                self.assertTrue(path.is_file(), f"{path} not found")
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


class TestGitignoresScratchpads(unittest.TestCase):

    def test_gitignore_lists_resume_files(self):
        content = (_REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for entry in ("resume", "tmp_resume"):
            with self.subTest(entry=entry):
                # Match a whole-line entry to avoid false positives like
                # matching "resume" inside a longer path.
                lines = {ln.strip() for ln in content.splitlines()}
                self.assertIn(
                    entry,
                    lines,
                    f"{entry!r} should be in .gitignore (T31)",
                )


if __name__ == "__main__":
    unittest.main()
