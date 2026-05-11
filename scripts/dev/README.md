# Developer Scratchpad Scripts

One-off diagnostic scripts used during RunTrend development. Not part of
the shipping application, not covered by the test suite, and not run
automatically. Keep here so they don't clutter the repo root and so
they're version-controlled when useful.

## Current contents

- `debug_hr_actual.py` — dump actual HR values of recent runs from the
  local SQLite DB.
- `debug_hr_zones.py` — print HR-zone classification per activity to
  understand why "easy runs" are or aren't detected.
- `debug_race_predictions.py` — trace `RacePredictor` output to debug
  blank race-time predictions in the summary panel.

## Running

These scripts expect to be invoked with the `run_trend` package on the
import path:

```bash
nix develop -c python scripts/dev/debug_hr_zones.py
# or, from the project root:
python -m scripts.dev.debug_hr_zones
```

They were originally written against an earlier `app.*` module path
(rename to `run_trend.*` happened mid-project); imports have been
updated, but the storage / analytics API may have drifted further.
Treat any error as "needs maintenance," not "the script is bad."

## Adding new ones

Anything that helps you debug a specific behaviour locally is welcome
here. Keep them stand-alone (no shared fixtures); if a helper becomes
broadly useful, promote it into `run_trend/` proper.
