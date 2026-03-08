# Running Progress Tracker

A desktop application for tracking and analyzing running progress from Strava.

## Overview

Running Progress Tracker is a PySide6-based desktop application that synchronizes your running activities from Strava, computes progress metrics, and visualizes your training development over time.

## Features

- **Strava Integration**: Automatic synchronization of running activities via OAuth
- **Data Aggregation**: View progress by week or month
- **Multiple Charts**:
  - Distance progress over time
  - Pace/Speed improvements
  - Training frequency
  - Composite training status score
  - Future trend projections
- **Smoothing**: Apply SMA or EMA smoothing to visualize long-term trends
- **Projections**: Estimate when you'll reach milestone distances (5K, 10K, half marathon, marathon)
- **Training Score**: Transparent composite score based on distance, frequency, and pace
- **Local-First**: All data stored locally in SQLite

## Prerequisites

- Nix with Flakes enabled
- Strava API credentials (client ID and client secret)

## Getting Strava API Credentials

1. Go to https://www.strava.com/settings/api
2. Create a new application
3. Note your Client ID and Client Secret
4. Set Authorization Callback Domain to `localhost`

## Installation and Setup

### Quick Start (Recommended)

```bash
# Just run it!
nix run

# Or build and run
nix build
./result/bin/run-trend
```

### Development

**Option 1: Using direnv (Recommended)**

If you have [direnv](https://direnv.net/) installed and hooked into your shell:

```bash
# Allow direnv for this project (one-time)
direnv allow

# The environment will now load automatically when you cd into the directory
# Just run:
python app/main.py

# Run tests
pytest tests/
```

**Option 2: Manual nix develop**

```bash
# Enter development shell for development work
nix develop

# Then run directly
python app/main.py
```

## Configuration

### GUI Settings

1. Launch the application
2. Click "Settings" in the toolbar
3. Enter your Strava Client ID and Client Secret
4. Click "Save"
5. Click "Connect to Strava" to start OAuth authorization
6. Authorize in the browser that opens
7. You're connected! Click "Sync Activities" to import your data

## Usage

1. **Sync Activities**: Click "Sync Activities" in Settings to import your running data
   - By default, all activities since 2000 are imported (covers all Strava history)
   - You can adjust the "Start Date" in the toolbar before syncing if needed
2. **Explore Charts**: Use the tabs to view different metrics:
   - Distance: Total distance per period with smoothing
   - Pace/Speed: Performance improvements over time
   - Frequency: Number of runs per period
   - Training Score: Composite progress metric
   - Projection: Future trend estimates and milestone predictions
6. **Adjust View**: Change aggregation period (Week/Month), smoothing strength, and metric type (Pace/Speed)

## Project Structure

```
app/
├── main.py                 # Application entry point
├── ui/                     # User interface components
│   ├── main_window.py      # Main application window
│   └── summary_panel.py    # Summary statistics panel
├── charts/                 # Chart widgets
│   ├── distance_chart.py
│   ├── pace_chart.py
│   ├── frequency_chart.py
│   ├── score_chart.py
│   └── projection_chart.py
├── strava/                 # Strava integration
│   ├── auth.py             # OAuth authentication
│   └── client.py           # API client
├── storage/                # Data persistence
│   └── database.py         # SQLite database
├── sync/                   # Synchronization logic
│   └── sync_manager.py
├── analytics/              # Data analysis
│   ├── aggregator.py       # Activity aggregation
│   ├── smoothing.py        # Time series smoothing
│   └── training_score.py   # Score calculation
├── projection/             # Forecasting
│   └── forecaster.py       # Trend projection
└── settings/               # Configuration
    └── config.py
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Training Score Explanation

The training score is a composite metric (0-100) that reflects your training progress:

- **50%** - Distance component: Total distance vs baseline
- **25%** - Frequency component: Number of runs vs baseline
- **25%** - Pace component: Pace improvement vs baseline

Score ranges:
- 0-30: Below baseline
- 30-60: Around baseline
- 60-80: Above baseline, good progress
- 80-100: Significantly above baseline, excellent progress

## Data Storage

All data is stored locally in `~/.run_trend/`:
- `activities.db` - SQLite database with activities
- `strava_token.json` - OAuth tokens
- `config.json` - Application settings

## Privacy

- All data is stored locally on your machine
- No external analytics or telemetry
- Only connects to Strava API with your explicit authorization
- You can revoke access at any time

## Development

### Development Shell

```bash
nix develop
```

This provides:
- Python 3.11
- PySide6
- All required dependencies
- Development tools (pytest, etc.)

### Running in Development

```bash
cd app
python main.py
```

## Technical Stack

- **UI Framework**: PySide6 (Qt for Python)
- **Charts**: PySide6.QtCharts
- **Database**: SQLite
- **HTTP**: requests library
- **Numerics**: numpy
- **Build System**: Nix Flakes

## Requirements from Specification

This implementation fulfills all requirements from `specification.md`:

✓ Strava OAuth integration
✓ Activity import and sync
✓ Weekly/monthly aggregation
✓ Distance, pace, speed, frequency charts
✓ Smoothing (SMA, EMA)
✓ Projection and forecasting
✓ Training status score
✓ Milestone estimation
✓ Local SQLite storage
✓ PySide6 UI
✓ Nix Flakes build
✓ Unit tests

## License

This project is licensed under the **MIT License with Commons Clause**.

**Author:** Arne Weiß
**Contact:** run-trend@arne-weiss.de

### What does this mean?

✅ **Allowed:**
- Private use
- Non-commercial use
- Viewing, modifying, and sharing the code
- Contributions and further development

❌ **Not allowed:**
- Commercial sale or distribution of the software
- Selling derivative works based on this software

See the [LICENSE](LICENSE) file for full license text.

## Troubleshooting

### OAuth Callback Issues

If the OAuth callback doesn't work:
- Ensure `localhost` is set as the authorization callback domain in your Strava API settings
- Check that port 8000 is not in use
- Try using 127.0.0.1 instead of localhost in your browser

### Database Issues

If you encounter database errors:
```bash
rm ~/.run_trend/activities.db
# Then re-sync from Strava
```

### Import Errors

Ensure you're running from the project root or have the app directory in your PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Contributing

This project follows the functional specification in `specification.md`. When adding features, ensure they align with the specification's goals and non-goals.
