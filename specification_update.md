# Running Progress Tracker — Specification Update for Enhanced Metrics and Charting

## 1. Purpose of This Update

This update extends the existing specification by improving how training structure and endurance development are represented.

The original version focuses primarily on:

* total distance per period
* average pace or speed per period
* training frequency
* training status score
* trend projection

That version is useful, but it does not fully distinguish between:

* total training load
* training distribution
* endurance-specific progression

Two training periods with the same total distance may represent very different types of training. For example:

* many short runs
* fewer but longer runs
* one pronounced long run versus evenly distributed mileage

For this reason, the next version should introduce additional metrics and visualizations that better describe the structure of training, especially for long-distance goals such as half marathon and marathon preparation.

---

# 2. Summary of Changes

## 2.1 Existing charts that should remain

The following charts remain valuable and should continue to exist:

* Distance Progress
* Pace / Speed Progress
* Training Frequency
* Training Status Score
* Projection

## 2.2 Existing charts that should be adjusted

The following charts should be revised:

* **Distance Progress**
* **Training Status Score**
* **Projection**

## 2.3 New charts that should be added

The following new charts should be introduced:

* **Longest Run Progress**
* **Average Distance per Run**
* **Training Structure Overview**

---

# 3. Rationale for the Changes

The original chart set describes volume and pace, but not enough about *how* the volume is achieved.

This is important because:

* weekly total distance indicates overall load
* number of runs indicates frequency and consistency
* average distance per run indicates the typical structure of training
* longest run indicates endurance-specific capacity and long-run progression

This becomes especially important for marathon-oriented training, where weekly mileage alone is not sufficient to assess preparedness.

Example:

### Period A

* 5 runs
* 50 km total
* longest run: 12 km
* average distance per run: 10 km

### Period B

* 5 runs
* 50 km total
* longest run: 28 km
* average distance per run: 10 km

Even though total distance and average distance per run are equal, the training meaning is very different. The longest run captures a key endurance dimension that would otherwise remain hidden.

---

# 4. Updated Functional Scope

The enhanced version shall preserve the original functionality and add a more complete representation of training structure.

The application shall now distinguish between three categories of training metrics:

## 4.1 Total Load Metrics

These describe overall training volume.

Included metrics:

* total distance per period
* total moving time per period
* number of runs per period

## 4.2 Training Structure Metrics

These describe how the total volume is distributed.

Included metrics:

* average distance per run
* longest run per period

## 4.3 Performance Metrics

These describe pace-related development.

Included metrics:

* average pace per period
* weighted average pace per period
* average speed per period

---

# 5. Changes to Existing Charts

## 5.1 Distance Progress Chart — Revised

### Current version

The current chart displays:

* total distance per period
* optional smoothed trend

### Revised version

The chart should continue to show total distance per period, but should now support optional overlays that make the interpretation more useful.

### New behavior

The chart shall support:

* total distance per period
* smoothed total distance trend
* optional overlay for total moving time
* optional overlay for number of runs

### Purpose

This makes it easier to distinguish between:

* a distance increase caused by more frequent running
* a distance increase caused by longer runs
* a stable distance with changing session structure

### UI requirement

The chart should have a small legend or toggle section to enable or disable overlays.

---

## 5.2 Training Status Score Chart — Revised

### Current version

The current score is based primarily on:

* distance
* frequency
* pace trend

### Revised version

The score chart itself may remain, but the score definition should now be interpreted more carefully in light of the new structural metrics.

### New recommendation

The chart should still show the composite score, but the UI shall present it as a **summary metric**, not as a replacement for detailed structural charts.

### Important design note

The following metrics should **not necessarily** be added directly to the composite score:

* average distance per run
* longest run

Reason:

* average distance per run may decrease when training improves through increased frequency
* longest run is highly valuable, but may overemphasize one weekly session

### UI change

The score chart should now include an explanatory note such as:

> The training score summarizes volume, consistency, and pace trend. Structural metrics such as longest run and average run distance are shown separately.

---

## 5.3 Projection Chart — Revised

### Current version

The chart projects future progression toward a chosen target distance.

### Limitation of current version

If projection is based only on total distance, the result may be too simplistic for endurance goals.

### Revised version

The projection chart shall support two projection modes:

#### Mode A — Volume Projection

Projects future total distance per period.

#### Mode B — Long-Run Projection

Projects the trend of the longest run per period.

### Why this matters

For marathon preparation, these are not the same question.

Examples:

* “When will weekly mileage reach 42.195 km?”
* “When will the longest run reach 30 km?”
* “When will the longest run reach marathon distance?”
  This is usually less relevant as a real training target, but may still be shown if requested.

### Revised milestone options

The projection chart shall allow the user to select:

* target total distance per period
* target longest-run distance

### Recommended defaults

For endurance training, suggested default targets:

* 10 km longest run
* 15 km longest run
* 21.1 km longest run
* 30 km longest run
* 42.195 km total weekly distance

---

# 6. New Charts

## 6.1 New Chart: Longest Run Progress

### Purpose

This chart visualizes the development of the longest run in each selected period.

### Why it is needed

The longest run is one of the most important endurance indicators for longer race preparation. It provides insight into specific long-run adaptation that total volume alone cannot show.

### Data shown

For each week or month:

* longest run distance
* optional smoothed trend

### Optional additions

The chart may also support:

* tooltips with date of the longest run
* pace of the longest run
* moving time of the longest run

### Interpretation

This chart helps answer:

* Is long-run endurance increasing?
* Is endurance progression stable or erratic?
* Are there stepwise increases that may indicate rapid load jumps?

### UI placement

This chart should appear in a new “Endurance” section or tab.

---

## 6.2 New Chart: Average Distance per Run

### Purpose

This chart visualizes the typical size of a run within each selected period.

### Why it is needed

This metric helps describe training structure.

A rise in total distance may come from:

* more runs
* longer runs
* both

Average distance per run helps distinguish between these patterns.

### Data shown

For each week or month:

* average distance per run
* optional smoothed trend

### Interpretation

This chart helps answer:

* Is training becoming longer per session?
* Is the athlete distributing volume across many short runs instead?
* Is a stable total load being achieved with different session structures?

### Important interpretation note

This metric should not be treated as a direct “better is always higher” measure. A lower average distance per run may be entirely appropriate if total volume and consistency improve.

### UI placement

This chart should appear in the same “Endurance” or “Structure” section as the longest run chart.

---

## 6.3 New Chart: Training Structure Overview

### Purpose

This chart gives a compact comparative view of how the training load is composed.

### Recommended design

This may be implemented as:

* a multi-line chart, or
* a combined dashboard panel with synchronized small charts

### Metrics included

* total distance per period
* number of runs per period
* average distance per run
* longest run per period

### Purpose of the overview

This allows the user to understand not only whether training increased, but also *how* it increased.

### Example interpretation

A period may show:

* increasing total distance
* increasing number of runs
* stable average distance per run
* slowly rising longest run

That pattern indicates a broad-based increase in training load with stable session structure.

Another period may show:

* stable total distance
* stable run count
* rising longest run
* falling average distance per run

That may indicate increasing specialization toward a weekly long run.

### UI placement

This chart or panel should appear either:

* in an Overview tab, or
* as a comparison dashboard below the main summary metrics

---

# 7. Updated Information Architecture

## 7.1 Existing sections

The current application likely contains sections such as:

* Overview
* Pace / Speed
* Score
* Projection

## 7.2 Proposed revised structure

The enhanced version should organize charts into clearer analytical categories.

### Recommended tab layout

#### Tab 1 — Overview

Contains:

* summary KPIs
* total distance chart
* pace/speed chart
* frequency chart

#### Tab 2 — Endurance

Contains:

* longest run chart
* average distance per run chart

#### Tab 3 — Structure

Contains:

* training structure overview
* optional comparison of total distance, run count, average distance, and longest run

#### Tab 4 — Score

Contains:

* training status score
* explanation of score inputs

#### Tab 5 — Projection

Contains:

* volume projection
* long-run projection
* milestone target selection

This structure makes the application more understandable because each tab answers a different kind of question.

---

# 8. Updated Metric Definitions

## 8.1 Longest Run per Period

Definition:

> The maximum single-run distance recorded within the selected week or month.

## 8.2 Average Distance per Run

Definition:

> Total distance in the period divided by number of runs in the period.

## 8.3 Total Distance per Period

Definition:

> Sum of all run distances in the selected period.

## 8.4 Number of Runs per Period

Definition:

> Count of all imported running activities in the selected period.

## 8.5 Weighted Average Pace

Definition:

> Total moving time divided by total distance for the selected period.

This should remain the preferred aggregation method for pace.

---

# 9. Updated UX Requirements

The new metrics introduce more analytical depth, so the UI must help the user interpret them correctly.

The application shall therefore:

* label charts clearly
* provide short help text for each metric
* avoid suggesting that every metric should always increase
* explain the different meaning of volume, structure, and endurance metrics

### Example help texts

#### Longest Run

> Shows the longest single run in each period. Useful for tracking endurance-specific progression.

#### Average Distance per Run

> Shows the typical length of a run in each period. Useful for understanding training structure, but not always a direct indicator of better fitness.

---

# 10. Updated Acceptance Criteria for the Enhanced Version

The enhanced version is accepted when:

1. the original charts still function correctly
2. the application computes longest run per period
3. the application computes average distance per run per period
4. a longest run chart is available
5. an average distance per run chart is available
6. the projection view supports both total-distance and longest-run projection modes
7. the chart layout is reorganized into clearer analytical categories
8. metric descriptions are shown in the UI
9. smoothing works for the new endurance charts
10. the application continues to build and run with the existing architecture and Nix setup

---

# 11. Recommended Versioning

A clean way to describe the evolution would be:

## Version 1.0

Core analytics release:

* sync from Strava
* total distance
* pace / speed
* training frequency
* composite score
* projection

## Version 1.1

Endurance analytics update:

* longest run chart
* average distance per run chart
* revised projection modes
* improved chart organization

## Version 1.2

Structure and interpretation update:

* training structure overview
* better metric explanations
* optional overlays between volume and structure metrics

---

# 12. Final Recommendation

If the current version is already implemented, I would make the next enhancement focus on this priority order:

## Highest priority

* add **Longest Run Progress**
* add **Average Distance per Run**
* extend **Projection** with long-run targets

## Medium priority

* revise **Distance Progress** with optional overlays
* reorganize tabs into Overview / Endurance / Structure / Score / Projection

## Lower priority

* create a more advanced comparative structure dashboard

The single most important addition is probably:

**Longest Run Progress**

because it adds a major endurance dimension that is especially relevant for half marathon and marathon preparation and is not captured well enough by total distance alone.

If you want, I can now turn this into a **clean patch-style spec addendum** with sections like “Replace section X with …”, “Add new section Y …”, so it fits directly into your original specification document.

