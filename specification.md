# Running Progress Tracker — Functional Specification

## 1. Overview

**Project name:** Running Progress Tracker
**Platform:** Desktop application
**Technology stack:** Python, PySide6, Strava API, Nix Flakes
**Primary goal:** Provide a desktop application that automatically synchronizes running activities from Strava, aggregates them by selectable time periods, computes progress metrics, and visualizes training development over time.

The application is intended for athletes who want to track how their running training evolves from a user-selected training start date. It should emphasize simplicity, local-first data ownership, reproducibility, and clear visual insight into long-term progress.

## 2. Goals

The application shall:

* import all running activities from Strava starting from a user-selected start date
* keep the locally stored activity dataset synchronized with Strava
* compute time-based aggregates on a weekly or monthly level
* visualize changes in:

  * total distance
  * average pace
  * average speed
  * training frequency
* optionally smooth time series to make long-term trends easier to read
* estimate future progression trends based on historical data
* estimate when a target distance milestone may be reached if the current trend continues
* provide a simple, interpretable training status score derived from multiple training indicators

## 3. Non-Goals

The first version shall **not** include:

* manual body weight tracking
* heart rate based fitness estimation
* VO2max estimation
* Garmin integration
* cloud sync other than Strava import
* mobile support
* social features
* multi-user support
* advanced sports science modeling beyond transparent trend scoring

## 4. Users

### Primary user

A single athlete who wants to analyze their own running history and ongoing progress.

### Usage pattern

The user opens the desktop application, connects it to Strava once, chooses a training start date, and then uses the app repeatedly to refresh activities and view updated charts and metrics.

## 5. Data Source and Synchronization

## 5.1 External source

The application shall use the Strava API as the authoritative source for running activities. Activities shall be fetched from the authenticated athlete account. The application shall only import activities of type **Run**. Strava provides endpoints for listing athlete activities and fetching activity details. ([Strava Developers][1])

## 5.2 Authentication

The application shall use Strava OAuth.
Required scopes should be limited to the minimum needed to read activities, ideally:

* `activity:read`
* optionally `activity:read_all` if private activities should also be included

Tokens shall be stored locally in a secure but practical way suitable for a desktop application.

## 5.3 Initial import

The user shall enter or select a **training start date**.
On first import, the application shall:

* fetch all running activities from Strava on or after that date
* normalize and store them locally
* compute derived metrics
* populate the visualizations

## 5.4 Incremental synchronization

The application shall support repeated synchronization.
On refresh, it shall:

* fetch activities newer than the newest locally stored activity
* optionally re-fetch a small recent time window to catch edits
* update changed activities if Strava activity metadata changed
* avoid duplicate imports
* preserve a local database as the main analysis source

## 5.5 Local persistence

The application shall store imported data locally, preferably in SQLite.

Suggested stored fields per activity:

* Strava activity ID
* activity name
* activity type
* start date/time
* timezone
* distance in meters
* moving time in seconds
* elapsed time in seconds
* average speed in m/s
* optional max speed
* optional elevation gain
* optional average heart rate if available
* optional kudos/comments are not needed for analysis
* last synced timestamp
* local derived flags / cache fields

## 6. Derived Metrics

The application shall compute derived metrics from raw activity data.

## 6.1 Per-activity derived metrics

For each run:

* distance in kilometers
* pace in minutes per kilometer
* speed in kilometers per hour
* duration in minutes
* optional “quality flags” such as unusually short run, outlier pace, etc.

## 6.2 Aggregated metrics by period

The user shall be able to group data by:

* week
* month

For each time bucket, the application shall compute:

* total distance
* number of runs
* average distance per run
* average pace
* weighted average pace
* average speed
* total moving time
* longest run
* consistency ratio (number of active days / days in period)

### Recommendation on pace aggregation

The application should prefer a **distance-weighted average pace** or compute pace indirectly from:

* total moving time / total distance

This avoids distortions caused by simply averaging pace across runs of very different lengths.

## 7. Charts and Visualizations

## 7.1 General requirements

The application shall present time series charts that allow the user to inspect progress from the chosen start date onward.

The user shall be able to select whether to display data:

* per week
* per month

The user shall be able to switch between:

* raw series
* smoothed series
* raw + smoothed overlay

## 7.2 Chart types

The initial version should provide separate charts rather than forcing everything into a single overloaded chart.

Recommended charts:

### Chart A — Distance Progress

Displays:

* total distance per period
* smoothed distance trend (optional)

### Chart B — Pace / Speed Progress

Displays either:

* average pace per period
  or
* average speed per period

The UI should allow switching between pace and speed representation.

### Chart C — Training Frequency

Displays:

* runs per period
* optional active days per period

### Chart D — Training Status Score

Displays:

* composite training score per period
* optional smoothed trend

### Chart E — Projection

Displays:

* observed historical trend
* projected future trajectory
* milestone marker (e.g. 42.195 km)

## 7.3 Interaction

The charts should support:

* mouse hover tooltips
* zoom
* pan
* reset zoom
* legend toggling where useful

PySide6 officially supports chart widgets via `QtCharts` and `QChartView`, including line chart examples and zoomable line chart examples. ([Qt Documentation][2])

## 8. Smoothing

The application shall support smoothing of time series to improve readability.

Recommended smoothing methods:

* simple moving average
* exponential moving average

The user shall be able to configure smoothing strength, for example:

* Off
* Light
* Medium
* Strong

or via a numeric window size.

Smoothing must only affect visualization and trend estimation, not the stored raw data.

## 9. Projection and Forecasting

## 9.1 Purpose

The projection feature shall provide a simple estimate of how the user’s training may evolve if the current trend continues.

It is not intended to be a medical or performance guarantee.

## 9.2 Projection targets

The application shall allow projecting:

* future weekly/monthly distance trend
* date when a target period distance is expected to be reached
* optional milestone examples:

  * 5 km
  * 10 km
  * half marathon
  * marathon

## 9.3 Projection model

The first version should use a transparent, simple model, such as:

* linear regression on recent periods
* optional rolling linear regression
* optional projection based on smoothed data only

The projection should be clearly labeled as an estimate.

## 9.4 Milestone interpretation

The application should define clearly what “reaching marathon distance” means.

Recommended default interpretation:

> “The aggregated training distance per selected period reaches at least 42.195 km.”

This is a training volume milestone, not a prediction that the user can race a marathon at a certain pace.

## 10. Training Status Score

## 10.1 Purpose

The application should compute a simple composite score that reflects whether training is trending in a positive direction.

The score should be transparent and explainable.

## 10.2 Inputs

Recommended inputs:

* period distance
* training frequency
* pace trend

Optional later extension:

* longest run
* moving time
* heart rate efficiency
* elevation load

## 10.3 Example formula

A reasonable first-version normalized score:

```text
training_score =
    0.50 * normalized_distance +
    0.25 * normalized_frequency +
    0.25 * normalized_pace_improvement
```

Where:

* `normalized_distance` compares current distance to a rolling baseline
* `normalized_frequency` compares runs per period to a rolling baseline
* `normalized_pace_improvement` reflects pace improvement versus baseline

For pace, lower is better, so the normalization must invert the metric appropriately.

## 10.4 Design principles for the score

The score should:

* increase when the user runs more consistently
* increase when the user runs more distance sustainably
* increase when pace improves
* not overreact to a single outlier workout
* remain explainable in the UI

The UI shall provide a small explanation panel describing exactly how the score is computed.

## 11. Filters and Settings

The application shall provide the following user-configurable options:

* training start date
* aggregation period: week / month
* metric mode: pace / speed
* smoothing mode and intensity
* projection horizon (e.g. 1–12 months)
* inclusion or exclusion of treadmill runs if detectable
* inclusion or exclusion of manually entered activities if relevant
* refresh / sync trigger

## 12. Suggested Additional Metrics

To make the application more useful without overcomplicating version 1, the following metrics are recommended:

* **Longest run per period**
  Useful because endurance progression is not fully visible through total distance alone.

* **Runs per period**
  Useful to distinguish high volume from consistent training.

* **Average run distance**
  Useful to see whether increased volume comes from more frequent running or longer runs.

* **Total moving time**
  Useful when pace fluctuates due to terrain or easy/recovery weeks.

These should be included in the data model even if not all are shown by default.

## 13. User Interface

## 13.1 Main window layout

Recommended layout:

### Top toolbar / control panel

* Connect to Strava
* Sync
* Start date selector
* Aggregation selector: Week / Month
* Metric selector: Pace / Speed
* Smoothing selector
* Projection target selector

### Left-side summary panel

Shows headline KPIs, such as:

* total imported runs
* total distance since start date
* current average weekly/monthly distance
* current average pace
* current training score
* projected milestone date

### Main content area

Tabbed or stacked chart area containing:

* Distance
* Pace/Speed
* Frequency
* Score
* Projection

### Bottom status area

Shows:

* last sync time
* token/auth status
* API sync messages
* data refresh errors

## 13.2 UX requirements

The application should remain useful even for users with little technical background.

Therefore it should:

* avoid requiring command-line interaction after installation
* make sync state visible
* explain derived metrics in plain language
* clearly distinguish historical values from projected values

## 14. Error Handling

The application shall handle:

* expired access token
* revoked Strava authorization
* API rate limit responses
* network errors
* incomplete activity data
* duplicate activity imports
* invalid date range selections

If synchronization fails, the application shall preserve the previously imported local dataset.

Strava applies API rate limits for developers, so sync behavior should be conservative and incremental. ([Strava Developers][1])

## 15. Architecture

## 15.1 Recommended internal modules

Suggested module structure:

* `app/`

  * `main.py`
  * `ui/`
  * `charts/`
  * `sync/`
  * `strava/`
  * `storage/`
  * `analytics/`
  * `projection/`
  * `settings/`

## 15.2 Layering

### UI layer

PySide6 widgets, dialogs, chart views

### Service layer

Synchronization logic, aggregation, projection, score calculation

### Persistence layer

SQLite database, schema migration support

### Integration layer

Strava OAuth and API requests

## 15.3 Recommended architectural style

Use a separation close to MVVM or MVP:

* UI widgets should not directly call the Strava API
* business logic should be testable independently from the UI
* chart data preparation should be separated from raw metric computation

## 16. Technology Requirements

## 16.1 Python and UI

The application shall be implemented in Python using PySide6. Qt for Python is the official Python binding for Qt, and `QtCharts` is available directly from PySide6 in current documentation. ([Qt Documentation][3])

## 16.2 Charts

Preferred first-version chart library:

* `PySide6.QtCharts`

Reason:

* strong fit for traditional 2D line charts
* official examples exist for line charts, area charts, model-backed charts, and zoomable charts ([Qt Documentation][4])

`QtGraphs` may be evaluated later, but version 1 should optimize for implementation clarity and predictable desktop behavior. Qt Graphs exists in PySide6 and supports line series, but for this application it is secondary to the more straightforward chart widget approach. ([Qt Documentation][5])

## 16.3 Build and packaging

The project shall be buildable with Nix Flakes.

The repository should include:

* `flake.nix`
* `flake.lock`
* a reproducible development shell
* an app package output
* a runnable application target

The Nix CLI officially supports the `nix flake` command family. ([NixOS][6])

## 17. Nix Flake Requirements

The flake should provide:

* `packages.<system>.default`
* `apps.<system>.default`
* `devShells.<system>.default`

The development shell should include:

* Python
* PySide6
* SQLite
* any Python packaging/build helpers needed

The default app target should launch the desktop application.

A `nix flake check` compatible setup is recommended. The Nix manual documents `nix flake check` as part of the flake command set. ([NixOS][6])

## 18. Performance Expectations

The application should work smoothly with at least several thousand imported activities.

Expected optimizations:

* local caching in SQLite
* incremental sync
* precomputed aggregates
* lightweight chart redraws

## 19. Security and Privacy

The application is local-first.

Requirements:

* activity data remains stored locally
* access tokens are stored locally only
* no external analytics or telemetry by default
* no mandatory cloud backend

## 20. Testing Requirements

The project should include tests for:

* aggregation by week
* aggregation by month
* pace calculation
* weighted pace calculation
* smoothing logic
* projection logic
* training score calculation
* duplicate activity handling
* sync merge logic

Recommended test categories:

* unit tests for analytics
* integration tests for local storage and sync logic
* optional mocked API tests for Strava integration

## 21. Acceptance Criteria

Version 1 is accepted when:

1. the user can authenticate with Strava
2. the application can import all running activities since a chosen start date
3. the application stores activities locally without duplicates
4. the application can refresh and synchronize new activities
5. weekly and monthly views are available
6. distance, pace/speed, and frequency charts are available
7. smoothing can be enabled and adjusted
8. a composite training score is shown
9. a simple projection view is available
10. the application builds and runs via Nix Flakes

## 22. Future Extensions

Possible later features:

* manual body weight tracking
* Garmin import
* shoe tracking
* heart rate efficiency metrics
* race result tracking
* training blocks and annotations
* export to CSV / PDF
* dark mode / theme support
* comparison of multiple training periods
* pace zones and effort analysis

---

[1]: https://developers.strava.com/docs/reference/?utm_source=chatgpt.com "Strava API v3"
[2]: https://doc.qt.io/qtforpython-6/faq/porting_from2.html?utm_source=chatgpt.com "Porting Applications from PySide2 to PySide6 - Qt for Python"
[3]: https://doc.qt.io/qtforpython-6/?utm_source=chatgpt.com "Qt for Python"
[4]: https://doc.qt.io/qtforpython-6/examples/example_charts_linechart.html?utm_source=chatgpt.com "Line Chart Example - Qt for Python"
[5]: https://doc.qt.io/qtforpython-6/PySide6/QtGraphs/index.html?utm_source=chatgpt.com "PySide6.QtGraphs - Qt for Python"
[6]: https://nixos.org/manual/nix/unstable/command-ref/new-cli/nix3-flake.html?utm_source=chatgpt.com "nix flake - Nix 2.34.0 Reference Manual"

