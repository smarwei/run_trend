"""
Regression guard: requirements.txt must stay in sync with pyproject.toml.

Drift led to `pip install -r requirements.txt && python -m run_trend.main`
failing on import of `markdown` (used in manual_dialog.py), which the
file was missing.
"""
import re
import unittest
from pathlib import Path

# Python 3.11+ ships tomllib in stdlib.
import tomllib


_REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_pin(spec: str) -> tuple[str, str]:
    """Split a `package>=X.Y.Z` line into (package, full_spec)."""
    name = re.split(r'[<>=!~ ]', spec.strip(), maxsplit=1)[0]
    return name.lower(), spec.strip()


class TestRequirementsSync(unittest.TestCase):

    def setUp(self):
        req_text = (_REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.req_lines = [
            line.strip()
            for line in req_text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        with (_REPO_ROOT / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)
        self.pyproject_deps = data["project"]["dependencies"]

    def test_every_pyproject_dep_present_in_requirements(self):
        req_names = {_parse_pin(line)[0] for line in self.req_lines}
        for dep in self.pyproject_deps:
            name = _parse_pin(dep)[0]
            with self.subTest(dep=name):
                self.assertIn(
                    name,
                    req_names,
                    f"{name!r} is in pyproject.toml but missing from "
                    f"requirements.txt — please add it",
                )

    def test_no_extra_runtime_deps_in_requirements(self):
        """requirements.txt should not list runtime deps that pyproject
        doesn't declare. (Dev-only deps live under [project.optional-dependencies]
        and are not expected in requirements.txt either.)"""
        pyproject_names = {_parse_pin(d)[0] for d in self.pyproject_deps}
        for line in self.req_lines:
            name = _parse_pin(line)[0]
            with self.subTest(dep=name):
                self.assertIn(
                    name,
                    pyproject_names,
                    f"{name!r} is in requirements.txt but not in "
                    f"pyproject.toml dependencies — drift",
                )


if __name__ == "__main__":
    unittest.main()
