# Running Progress Tracker

A desktop application for tracking and analyzing running progress from Strava.

**Version:** 0.1.0
**Documentation:** Press the Help button (❓) in the app for the full user manual

## Overview

Running Progress Tracker is a PySide6-based desktop application that synchronizes your running activities from Strava, computes progress metrics, and visualizes your training development over time. Features comprehensive heart rate analytics, race time predictions, and marathon readiness tracking.

## Features

- **Strava Integration**: Automatic synchronization of running activities via OAuth
- **Data Aggregation**: View progress by week or month
- **Comprehensive Charts**:
  - **Overview Tab**: Distance progress, Pace/Speed improvements, Training frequency
  - **Heart Rate Tab**: HR Range, Average HR, Efficiency Factor (aerobic fitness)
  - **Endurance Tab**: Longest Run progression, Average Distance per Run
  - **Score Tab**: Composite training status score
  - **Projection Tab**: Future trend projections and milestone estimates
- **Heart Rate Analytics**:
  - Efficiency Factor tracking (pace-normalized HR for aerobic fitness)
  - HR Zone analysis
  - Manual HRmax configuration for improved accuracy
  - HRmax plausibility checks with intelligent suggestions
- **Race Time Predictions**:
  - HR-based race time estimates for 5K, 10K, Half Marathon, and Marathon
  - Uses McMillan Calculator methodology with Easy Run identification
  - Scientific approach combining heart rate zones and training pace
- **Marathon Readiness**:
  - Long Run progression tracking
  - Marathon Milestone estimation (32km Long Run target)
  - Endurance-focused metrics
- **Smoothing**: Apply SMA or EMA smoothing to visualize long-term trends
- **Projections**: Estimate when you'll reach milestone distances and endurance targets
- **Training Score**: Adaptive composite score (includes Efficiency Factor when HR data available)
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
2. **Configure Heart Rate** (Optional): Set your manual HRmax in Settings for improved accuracy
   - The app auto-detects HRmax from your activities
   - Manual configuration improves race time predictions
   - The app will suggest a value if auto-detection seems implausible
3. **Explore Charts**: Use the tabs to view different metrics:
   - **Overview**: Distance, Pace/Speed, Frequency
   - **Heart Rate**: HR Range, Average HR, Efficiency Factor (aerobic fitness indicator)
   - **Endurance**: Longest Run progression, Average Distance per Run
   - **Score**: Composite training progress metric (adapts to HR data availability)
   - **Projection**: Future trend estimates, milestone predictions (Volume or Long Run mode)
4. **View Summary Panel**: Left sidebar shows key metrics:
   - Training volume and performance
   - Heart rate metrics (if HR monitor used)
   - Training Score (0-100)
   - Marathon Milestone (32km Long Run readiness)
   - Race Time Predictions (5K, 10K, Half, Marathon)
5. **Adjust View**: Change aggregation period (Week/Month), smoothing strength, and metric type (Pace/Speed)

## Project Structure

```
app/
├── main.py                     # Application entry point
├── ui/                         # User interface components
│   ├── main_window.py          # Main application window
│   ├── summary_panel.py        # Summary statistics panel
│   ├── settings_dialog.py      # Settings dialog with Strava & HR config
│   └── manual_dialog.py        # User manual dialog
├── charts/                     # Chart widgets
│   ├── distance_chart.py       # Distance progress chart
│   ├── pace_chart.py           # Pace/Speed chart
│   ├── frequency_chart.py      # Training frequency chart
│   ├── heartrate_chart.py      # Heart rate & efficiency factor chart
│   ├── longest_run_chart.py    # Longest run progression chart
│   ├── avg_distance_chart.py   # Average distance per run chart
│   ├── structure_overview_chart.py  # Training structure overview
│   ├── score_chart.py          # Training score chart
│   └── projection_chart.py     # Projection & forecasting chart
├── strava/                     # Strava integration
│   ├── auth.py                 # OAuth authentication
│   └── client.py               # API client
├── storage/                    # Data persistence
│   └── database.py             # SQLite database
├── sync/                       # Synchronization logic
│   └── sync_manager.py         # Activity sync orchestration
├── analytics/                  # Data analysis
│   ├── aggregator.py           # Activity aggregation by period
│   ├── smoothing.py            # Time series smoothing (SMA/EMA)
│   ├── training_score.py       # Composite training score calculation
│   └── race_predictor.py       # HR-based race time predictions (McMillan)
├── projection/                 # Forecasting
│   └── forecaster.py           # Trend projection & milestone estimation
└── settings/                   # Configuration
    └── config.py               # Settings persistence
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Training Score Explanation

The training score is a composite metric (0-100) that reflects your training progress. The weighting adapts based on data availability:

**With Heart Rate Data:**
- **30%** - Distance component: Total distance vs baseline
- **30%** - Pace component: Pace improvement vs baseline
- **20%** - Efficiency Factor: Aerobic fitness (pace-normalized HR)
- **20%** - Frequency component: Number of runs vs baseline

**Without Heart Rate Data:**
- **37.5%** - Distance component: Total distance vs baseline
- **37.5%** - Pace component: Pace improvement vs baseline
- **25%** - Frequency component: Number of runs vs baseline

The score automatically adjusts when HR data is available vs unavailable, ensuring consistent evaluation regardless of whether you use a heart rate monitor.

**Score ranges:**
- 0-30: Below baseline
- 30-60: Around baseline
- 60-80: Above baseline, good progress
- 80-100: Significantly above baseline, excellent progress

**Key Insight:** Using a heart rate monitor provides the Efficiency Factor component, which tracks your aerobic fitness development - a crucial metric for endurance training!

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

## Features Overview

This implementation includes comprehensive running analytics:

✓ Strava OAuth integration with automatic sync
✓ Activity import and sync (incremental updates)
✓ Weekly/monthly aggregation
✓ **5 Chart Tabs**: Overview, Heart Rate, Endurance, Score, Projection
✓ Heart Rate analytics (HR Range, Avg HR, Efficiency Factor)
✓ Endurance tracking (Longest Run, Avg Distance per Run)
✓ Smoothing (SMA, EMA) for trend visualization
✓ Projection and forecasting (Volume & Long Run modes)
✓ **Adaptive Training Score** (with/without HR data)
✓ Milestone estimation (Marathon Readiness - 32km Long Run)
✓ **Race Time Predictions** (HR-based McMillan methodology)
✓ Manual HRmax configuration with plausibility checks
✓ Local SQLite storage (privacy-first)
✓ PySide6 Qt UI with dark mode support
✓ Nix Flakes build system
✓ Comprehensive unit tests (17 tests for race predictor alone)

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
