# Running Progress Tracker - User Manual

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [User Interface](#user-interface)
4. [Metrics Explanations](#metrics-explanations)
5. [Charts and Visualizations](#charts-and-visualizations)
6. [Settings](#settings)
7. [Frequently Asked Questions](#frequently-asked-questions)
8. [About This Software](#about-this-software)

---

## Overview

Running Progress Tracker is a desktop application for analyzing your running training. It synchronizes your activities from Strava and provides comprehensive analytics for:

- Distance progress and training volume
- Pace and speed development
- Training frequency and consistency
- Long run capability (Long Runs)
- Training structure and patterns
- **Heart rate and aerobic fitness (Efficiency Factor)**
- Trend projections and milestone estimates

The application is particularly helpful for preparing for long-distance runs like half marathons and marathons.

---

## Getting Started

### 1. Set up Strava Connection

1. Click **"Settings"** in the toolbar
2. Enter your Strava API credentials:
   - **Client ID**: From https://www.strava.com/settings/api
   - **Client Secret**: From https://www.strava.com/settings/api
3. Click **"Save"**
4. Click **"Connect to Strava"** (in the Settings dialog)
5. Authorize the application in your browser

### 2. Synchronize Activities

**First Sync (on first launch):**

1. The Settings dialog opens automatically
2. Enter your Strava API credentials and click **"Connect to Strava"**
3. Authorize in the browser
4. You'll be asked if you want to synchronize now → Click **"Yes"**
5. All runs since January 1, 2000 will be imported (guaranteed to capture all Strava activities)

**Note:** The Start Date in the toolbar determines from when to import on first sync. Default is January 1, 2000, which covers all possible Strava activities (Strava was founded in 2009).

**Subsequent Syncs (automatic):**

After the first sync, synchronization runs automatically:
- On app start: Silent check for new activities in the background
- Only new/changed activities are loaded (incremental)

Only **outdoor runs** are imported. The following activities are excluded:
- Treadmill/VirtualRun
- Walk
- Cycling/Ride
- WeightTraining
- Yoga, swimming, etc.

### 3. Analyze Data

After synchronization, your runs are automatically aggregated and visualized:
- Select the **Period** (Week/Month) in the toolbar
- Adjust the **Start Date** to display only a specific timeframe
- Use **Smoothing** to better recognize trends
- Switch between different chart tabs (Overview, Endurance, Score, Projection)

---

## User Interface

### Toolbar

- **Settings**: Manage Strava API credentials, connect to Strava, synchronize activities
- **Start Date**: Start date for data filtering (from when runs are displayed in charts)
- **Period**: Aggregation period (Week/Month)
- **Metric**: Pace or Speed for speed charts
- **Smoothing**: Smoothing strength for charts (Off/Light/Medium/Strong)
- **Help**: Open this manual (far right in the toolbar)

### Summary Panel (left)

Shows current KPIs based on your data:

**Volume Metrics:**
- **Total Runs**: All recorded runs
- **Total Distance**: Sum of all runs (lifetime)
- **Period Distance**: Average distance per period (e.g., ~27 km/week)

**Performance Metrics:**
- **Current Average Pace**: Weighted average pace

**Heart Rate Metrics** (when HR data available):
- **Average Heart Rate**: Average for the current period
- **Lifetime Max Heart Rate**: Highest ever measured value
- **Efficiency Factor**: Pace-normalized heart rate (aerobic fitness)

**Progress Indicators:**
- **Training Score**: Combined metric from volume, frequency, pace, and efficiency (0-100)
- **Marathon Milestone**: Estimated date for 32 km Long Run / Marathon-Ready (or "Milestone Reached!")
- **Race Time Predictions**: Estimated race times for 5K, 10K, Half, and Marathon (HR-based)

**Training Load (ACWR):**
- **Load Score**: 0-100 scale showing overtraining risk based on Acute:Chronic Workload Ratio
- **Status**: Current load classification (SAFE, CAUTION, WARNING, DANGER)
- **Warning Message**: Appears when score ≥ 80 with specific recommendations to reduce injury risk

### Charts (right)

The charts are organized into 6 main categories:

#### 1. Overview Tab
- **Distance**: Total distance per period
- **Pace/Speed**: Pace or speed
- **Frequency**: Number of runs

#### 2. Heart Rate Tab
- **Heart Rate Range**: Min-Max heart rate range per period
- **Average HR**: Average heart rate
- **Efficiency Factor**: Pace-normalized heart rate

#### 3. Endurance Tab
- **Longest Run**: Longest run per period
- **Avg Distance/Run**: Average distance per run

#### 4. Score Tab
- **Training Score**: Combined training progress

#### 5. Training Load Tab
- **Training Load (ACWR)**: Overtraining risk detection with colored safe zones

#### 6. Projection Tab
- **Projection**: Trend projections for Volume or Long Runs

---

## Metrics Explanations

### Total Load Metrics

#### Total Distance per Period
**What it is:** Sum of all run distances in the selected period (week/month).

**Calculation:** `sum(all runs in the period)`

**Interpretation:**
- Shows training volume
- Higher values = more total load
- Important for endurance development

**Example:** 3 runs of 10km, 8km, 5km = 23 km total

#### Period Distance (Current Period Distance)
**What it is:** Average total distance per period for current aggregation.

**Calculation:** `average(total_distance of last 12 periods)`

**Interpretation:**
- Shows your **current average weekly volume** (in weekly view)
- Shows your **current average monthly volume** (in monthly view)
- Displayed in the Summary Panel
- Baseline for Training Score normalization

**Example:**
- Last 12 weeks: 20, 25, 30, 28, 22, 27, 30, 32, 28, 25, 30, 33 km
- **Period Distance**: ~27.5 km/week
- This is your current "normal state"

**Difference to Total Distance:**
- **Total Distance**: Specific distance of a single period (e.g., "This week: 30 km")
- **Period Distance**: Average distance over many periods (e.g., "Average: 27.5 km/week")

#### Total Moving Time
**What it is:** Total moving time of all runs in the period.

**Calculation:** `sum(moving_time of all runs)`

**Interpretation:**
- Shows invested training time
- Independent of speed

#### Number of Runs
**What it is:** Number of runs in the period.

**Calculation:** `count(runs)`

**Interpretation:**
- Shows training consistency
- More runs = more frequent training
- Not necessarily higher distance

### Training Structure Metrics

#### Average Distance per Run
**What it is:** Average length of a run in the period.

**Calculation:** `total_distance / number_of_runs`

**Interpretation:**
- Shows typical run length
- **Not always "higher is better"**
- Can decrease when you do more shorter runs
- Can increase when you do fewer but longer runs

**Important Difference:**
- **Same total distance** can result from different structures:
  - 30 km = 3 × 10 km (Avg: 10 km)
  - 30 km = 6 × 5 km (Avg: 5 km)

**Example:**
- Week A: 5 runs, 50 km total → Avg: 10 km/run
- Week B: 10 runs, 50 km total → Avg: 5 km/run

Both have the same volume but different structure!

#### Longest Run per Period
**What it is:** Maximum single run distance in the period.

**Calculation:** `max(distance of all runs in the period)`

**Interpretation:**
- **Most important metric for long-distance preparation**
- Shows specific endurance capability
- Critical for marathon/half marathon training
- Cannot be derived from total distance

**Why important:**
Two periods with the same total distance can show completely different endurance capabilities:

- **Period A**: 50 km total, longest run: 12 km
- **Period B**: 50 km total, longest run: 28 km

Period B shows significantly higher long-distance endurance!

### Performance Metrics

#### Weighted Average Pace
**What it is:** Weighted average pace of the period.

**Calculation:** `total_moving_time / total_distance`

**Important:** This is NOT the simple average of all paces!

**Why weighted:**
Longer runs influence the average more.

**Example:**
- Run 1: 10 km in 50 min = 5:00 min/km
- Run 2: 5 km in 30 min = 6:00 min/km
- Simple average: (5:00 + 6:00) / 2 = 5:30 min/km
- **Weighted average**: 80 min / 15 km = 5:20 min/km ✓

#### Average Speed
**What it is:** Average speed in km/h.

**Calculation:** `total_distance / total_moving_time`

**Relationship to Pace:** Reciprocal of pace, in km/h instead of min/km

#### Training Score (0-100)
**What it is:** Combined metric from volume, frequency, pace progress, and aerobic fitness.

**Calculation (with HR data):**
```
training_score = (
    0.30 × normalized_distance +
    0.20 × normalized_frequency +
    0.30 × normalized_pace +
    0.20 × normalized_efficiency
) × 50
```

**Components (with HR data):**
- **30% Distance**: Training volume
- **30% Pace**: Speed improvement
- **20% Efficiency Factor**: Aerobic fitness (pace-normalized HR)
- **20% Frequency**: Training consistency

**Calculation (without HR data):**
```
training_score = (
    0.375 × normalized_distance +
    0.250 × normalized_frequency +
    0.375 × normalized_pace
) × 50
```

**Components (without HR data):**
- **37.5% Distance**: Training volume
- **37.5% Pace**: Speed improvement
- **25% Frequency**: Training consistency

**Important:** The weights automatically adapt when no heart rate data is available for a period.

**Interpretation:**
- 0-25: Low training level
- 25-50: Moderate training
- 50-75: Good training level
- 75-100: Very high training level

**Important:** The score is a summary. It does NOT replace structural metrics like Longest Run or Average Distance per Run, which should be viewed separately.

#### Training Fitness (CTL) and Form (TSB)

**What it is:** An **absolute** training-fitness metric alongside the
self-relative Training Score (T38). Where the Score normalises against
your own rolling baseline and therefore plateaus around ~50 once you
stabilise at a given training level (`current_runs / baseline_runs ≈
1.0`), CTL **stays high** as long as you keep training.

**Three values under "Fitness:" in the Training Status panel:**

- **Training Fitness** = current **CTL** (Chronic Training Load) in
  TRIMP/day. Slow-moving number that grows with sustained training.
- **Form (TSB)** = `CTL − ATL` (Training Stress Balance). Tells you
  whether you're rested or fatigued — not whether you're fit.

**Banister TRIMP per activity** (HR-based training load):

```
TRIMP = duration_min × HRr × 0.64 × e^(b × HRr)
```

where `HRr = (HR_avg − HR_rest) / (HR_max − HR_rest)` clamped to
`[0, 1]`. The exponential factor `b = 1.92` (men) / `1.67` (women)
weights high-intensity sessions disproportionately — 30 min at tempo
produces more load than 30 min easy.

**CTL and ATL** are exponentially weighted moving averages of daily
TRIMP totals:

```
CTL_today = CTL_yesterday × (1 − 1/42) + daily_TRIMP × (1/42)
ATL_today = ATL_yesterday × (1 − 1/7)  + daily_TRIMP × (1/7)
```

CTL takes about 6 weeks to converge after a training change ("fitness
builds slowly"); ATL responds in a week ("fatigue clears fast"). While
your history is shorter than 42 days the EWMA is still warming up; the
app marks the CTL number with a `*` until you cross that threshold.

**CTL ranges** (TRIMP/day — the scale is HR-based, not power-based as
in TrainingPeaks; absolute values aren't directly comparable to
power-derived CTL from cycling, but the relative bands apply):

- **30–50**  recreational / casual
- **60–90**  well-trained
- **100+**   competitive

**TSB zones (Coggan, same units as CTL):**

| Range          | State                                              |
|----------------|----------------------------------------------------|
| > +25          | transitional (over-rested — losing fitness)        |
| +10 to +25     | race-fresh (taper has worked)                      |
| −10 to +10     | neutral                                            |
| −20 to −10     | productive overload (build phase)                  |
| −30 to −20     | approaching fatigue limit (consider deload)        |
| < −30          | overreaching risk                                  |

**Running-specific CTL ramp-up rates** (matches the "10 % rule" for
weekly mileage):

- Beginners: **+2 to +4** TRIMP/day per week
- Intermediate: **+3 to +5**
- Advanced: **+5 to +7**

Faster ramps correlate with elevated injury risk in the literature.

**When the app shows a number:**

- Activities carry `average_heartrate` (otherwise TRIMP can't be
  computed)
- **Date of Birth** set (for the Tanaka HRmax fallback) **or** a
  **manual Max HR** in Settings
- **Gender** set (for the b-factor in the Banister formula)
- **Resting HR** set (for the HR-reserve calculation)

If any prerequisite is missing the label spells out which field to
fill.

**When to look at CTL instead of Score:**

- You've been at the same training level for weeks/months and the
  Score sits around 50 → CTL tells you the **absolute** load you're
  sustaining.
- You're tapering for a race and want to know if it's working → TSB
  should swing positive (race-fresh).
- You feel tired → check the ATL or a negative TSB.

**Sources:**
- Banister, E. W. (1991). Modeling Elite Athletic Performance.
- Coggan, A., Performance Manager (TrainingPeaks).
- Running-specific CTL ramp rates verified at:
  <https://run.analyticszone.app/en/training-load/>

### Heart Rate Metrics

#### Average Heart Rate per Period
**What it is:** Average heart rate of all runs with HR data in the period.

**Calculation:** `sum(average_heartrate of all HR runs) / count(HR runs)`

**Interpretation:**
- Shows typical heart rate during training
- **Lower value at same pace** = better aerobic fitness
- Important: Only runs with HR data are considered

**Note:** Runs without a heart rate monitor are not included in this metric.

#### Min/Max Heart Rate Range
**What it is:** Range of heart rates in the period.

**Min Average HR:** Lowest average value of a single run
**Max HR:** Highest measured heart rate peak across all runs

**Calculation:**
- `min_avg_hr = min(average_heartrate of all HR runs)`
- `max_hr = max(max_heartrate of all HR runs)`

**Interpretation:**
- Shows the range of training intensities
- Large range = different training intensities
- **Min Average HR**: Shows relaxed pace (e.g., Recovery Runs)
- **Max HR**: Shows peak load (e.g., intervals, races)

**Example:**
- Week with 4 runs:
  - Recovery Run: Avg 135 bpm, Max 145 bpm
  - Easy Run: Avg 145 bpm, Max 155 bpm
  - Tempo Run: Avg 165 bpm, Max 175 bpm
  - Long Run: Avg 150 bpm, Max 170 bpm
- **Min Average HR**: 135 bpm (Recovery Run)
- **Max HR**: 175 bpm (Peak from Tempo Run)
- **Range**: 135-175 bpm

#### Lifetime Max Heart Rate
**What it is:** Highest ever measured heart rate across ALL runs.

**Calculation:** `max(max_heartrate of all runs in the database)`

**Interpretation:**
- Shows your maximum heart rate capacity
- Displayed in the Summary Panel (constant value)
- Only changes when a new maximum is reached
- Important for calculating HR zones

**Difference to Period Max HR:**
- **Period Max HR**: Highest value in a specific week/month
- **Lifetime Max HR**: Highest value EVER (across all time)

**Example:**
- Lifetime Max HR: 192 bpm (reached in a race in June 2024)
- Current week Max HR: 178 bpm (normal training intensity)

**Note:** Only displayed if at least one run with HR data exists.

#### Efficiency Factor (EF)

**What it is:** Ratio of speed to heart rate - a measure of aerobic efficiency.

**Formula:**
```
Efficiency Factor = Speed (m/s) / Average Heart Rate (bpm)
```

**Origin:** Industry-standard metric from TrainingPeaks/Joe Friel

**What it measures:**
- How many meters you cover per heartbeat
- **Higher value = better aerobic fitness**
- Normalizes heart rate for different speeds

**Why important:**
Raw heart rate alone is not meaningful because:
- Faster pace → naturally higher HR
- Slower pace → naturally lower HR

The Efficiency Factor allows a fair comparison!

**Example 1: Fitness Improvement**

**3 months ago:**
- Pace: 6:00 min/km (2.78 m/s)
- Avg HR: 155 bpm
- **EF = 2.78 / 155 = 0.0179**

**Today:**
- Pace: 5:30 min/km (3.03 m/s)
- Avg HR: 150 bpm
- **EF = 3.03 / 150 = 0.0202**

**Interpretation:** EF increased → aerobic fitness has improved! You're running faster at a lower heart rate.

**Example 2: Why EF is better than raw HR**

**Athlete A:**
- Tempo Run: 5:00 min/km (3.33 m/s), HR: 165 bpm
- **EF = 3.33 / 165 = 0.0202**

**Athlete B:**
- Easy Run: 6:30 min/km (2.56 m/s), HR: 140 bpm
- **EF = 2.56 / 140 = 0.0183**

Athlete B has lower HR, but Athlete A has better aerobic efficiency!

**Visualization:**
- In the chart, EF is displayed multiplied by 1000 for better readability
- EF = 0.0179 → displayed as 17.9
- EF = 0.0202 → displayed as 20.2

**Long-term Benefits:**
Track your EF over months to see aerobic fitness improvements:
- Rising EF = better endurance
- Constant EF despite higher volume = good recovery
- Falling EF = possible overtraining or fatigue

**Important:** Only compare EF with your own values, not with other athletes (individual HR ranges vary greatly).

### Training Load (ACWR)

#### What is ACWR?

**ACWR** = **Acute:Chronic Workload Ratio** - a scientifically-validated metric for detecting overtraining and injury risk.

**The Core Idea:**
Your body adapts best when training load increases gradually. ACWR compares your **recent workload** (acute) to your **baseline workload** (chronic) to detect dangerous spikes or drops.

**Key Formula:**
```
ACWR = Acute Load / Chronic Average Load

Where:
- Acute Load = Training load in the most recent week
- Chronic Load = Average training load from the 4 weeks BEFORE the acute week
```

**Visual Example:**
```
Week:        -4    -3    -2    -1    Acute (Current)
Distance:    20km  22km  21km  23km  | 26km  ← Current week

Chronic Avg = (20 + 22 + 21 + 23) / 4 = 21.5 km
Acute Load = 26 km
ACWR = 26 / 21.5 = 1.21 (SAFE - gradual increase)
```

**Why ACWR Matters:**
- **ACWR > 1.5**: Sharp spike = High injury risk (2-4x higher according to research)
- **ACWR 0.8-1.3**: Safe zone = Body can adapt
- **ACWR < 0.8**: Detraining = Loss of fitness

**Important:** ACWR is NOT just about distance. It considers **Distance**, **Pace**, and **Heart Rate** together for a complete picture.

---

#### How is Training Load Calculated?

RunTrend calculates a **composite Training Load score (0-100)** by combining three ACWR components:

**1. Component ACWRs:**
```
Distance ACWR = Acute Distance / Chronic Average Distance
Pace ACWR = Acute Speed / Chronic Average Speed (pace inverted)
HR ACWR = Acute HR / Chronic Average HR
```

**2. Weighted Combination:**
```
Composite ACWR = (Distance ACWR × 40%) +
                 (Pace ACWR × 30%) +
                 (HR ACWR × 30%)
```

**Why These Weights?**
- **Distance (40%)**: Primary load indicator - how much you run
- **Pace (30%)**: Intensity indicator - how hard you push
- **Heart Rate (30%)**: Physiological stress - how your body responds

**If HR data is missing**: HR ACWR defaults to 1.0 (neutral), and the score is calculated using Distance and Pace only.

**3. Score Mapping (0-100):**
The composite ACWR is mapped to a 0-100 scale for easy interpretation:

```
ACWR Range        Training Load Score
──────────────────────────────────────
0.00 - 0.80  →   0-40   (Undertraining)
0.80 - 1.30  →   40-65  (SAFE)
1.30 - 1.50  →   65-80  (CAUTION)
1.50 - 1.80  →   80-90  (WARNING)
1.80+        →   90-100 (DANGER)
```

**Example Calculation:**
```
Current week:  Distance: 30 km, Pace: 5:30/km, HR: 155 bpm
4 weeks ago:   Distance: 25 km, Pace: 5:45/km, HR: 150 bpm

Distance ACWR = 30 / 25 = 1.20
Pace ACWR = (60/5.30) / (60/5.75) = 10.91 / 10.43 = 1.05
HR ACWR = 155 / 150 = 1.03

Composite ACWR = (1.20 × 0.4) + (1.05 × 0.3) + (1.03 × 0.3)
               = 0.48 + 0.315 + 0.309
               = 1.10

Training Load Score = ~52 (SAFE zone)
Status: "SAFE - Gradual progressive overload"
```

---

#### Score Interpretation

| **Score** | **Status** | **ACWR Range** | **Meaning** | **Action** |
|-----------|------------|----------------|-------------|------------|
| **0-40** | Undertraining | < 0.8 | Significant drop in training load. Risk of detraining and fitness loss. | Consider gradually increasing volume/intensity if recovering from injury. Otherwise, maintain consistency. |
| **40-65** | **SAFE** | 0.8-1.3 | **Optimal training zone**. Your body can adapt to current load. Progressive overload without excessive risk. | Continue training as planned. This is the sweet spot for long-term improvement. |
| **65-80** | CAUTION | 1.3-1.5 | Moderate spike in training load. Increased injury risk. Monitor closely. | Be extra careful with recovery. Consider holding current load for 1-2 weeks instead of increasing further. |
| **80-90** | **WARNING** | 1.5-1.8 | Sharp spike. High injury risk (2-4x normal). Action needed. | **Reduce next week's volume by 20-30%**. Prioritize sleep, nutrition, and rest days. |
| **90-100** | **DANGER** | > 1.8 | Extreme spike. Very high injury risk. Immediate action required. | **Reduce volume by 40-50% immediately**. Consider taking 2-3 easy days. Risk of overtraining syndrome. |

**Visual Guide:**
```
    0        40              65        80   90    100
    ├─────────┼───────────────┼─────────┼────┼─────┤
  Under-   SAFE ZONE      CAUTION  WARNING DANGER
 training   (ideal)
```

---

#### Scientific Basis

The ACWR concept is based on peer-reviewed sports science research:

**Primary Source:**
> Gabbett, T.J. (2016). "The training-injury prevention paradox: should athletes be training smarter AND harder?" *British Journal of Sports Medicine*, 50(5), 273-280.

**Key Findings:**
- **ACWR 0.8-1.3**: Lowest injury risk (baseline)
- **ACWR 1.0-1.25**: "Sweet spot" for performance gains
- **ACWR > 1.5**: Injury risk increases 2-4x
- **ACWR < 0.8**: Detraining and fitness loss

**Applied to Running:**
ACWR was originally developed for team sports (rugby, football) but has been widely validated for endurance sports:
- Detects overtraining from sudden volume spikes
- Accounts for fitness decay during low-volume periods
- Combines volume AND intensity for complete picture

**Limitations of Research:**
- Most studies use 7-day acute / 28-day chronic windows (RunTrend uses this standard)
- Individual variation exists - some athletes tolerate higher ratios
- ACWR is a **risk indicator**, not a guarantee of injury
- Works best with consistent tracking over 8+ weeks

**Why RunTrend Uses Composite ACWR:**
Traditional ACWR only considers distance. RunTrend improves this by adding:
- **Pace component**: Detects intensity spikes (speed work, tempo runs)
- **HR component**: Captures physiological stress (heat, fatigue, illness)
- **Weighted formula**: Balances all three factors scientifically

---

#### Practical Examples

**Example 1: Safe Progressive Overload**
```
Scenario: Runner gradually increasing weekly volume

Week  | Distance | Pace    | HR  | Distance ACWR | Composite ACWR | Score | Status
──────|──────────|─────────|─────|───────────────|────────────────|───────|────────
-4    | 20 km    | 6:00/km | 145 | -             | -              | -     | -
-3    | 22 km    | 5:55/km | 147 | -             | -              | -     | -
-2    | 24 km    | 5:50/km | 148 | -             | -              | -     | -
-1    | 26 km    | 5:48/km | 149 | -             | -              | -     | -
Now   | 28 km    | 5:45/km | 150 | 1.17          | 1.12           | 54    | SAFE

Chronic Avg Distance = (20+22+24+26)/4 = 23 km
Acute Distance = 28 km
Distance ACWR = 28/23 = 1.17

Interpretation:
✓ Gradual 10% weekly increase
✓ ACWR in safe zone (0.8-1.3)
✓ Training Load Score 54 - keep going!
```

**Example 2: Dangerous Spike (Race + High Volume)**
```
Scenario: Runner does a hard race after steady base training

Week  | Distance | Pace    | HR  | Distance ACWR | Composite ACWR | Score | Status
──────|──────────|─────────|─────|───────────────|────────────────|───────|────────
-4    | 30 km    | 5:30/km | 150 | -             | -              | -     | -
-3    | 32 km    | 5:28/km | 151 | -             | -              | -     | -
-2    | 31 km    | 5:32/km | 149 | -             | -              | -     | -
-1    | 30 km    | 5:30/km | 150 | -             | -              | -     | -
Now   | 50 km    | 5:00/km | 165 | 1.63          | 1.71           | 87    | WARNING

Chronic Avg = 30.75 km at 5:30/km, HR 150
Acute = 50 km at 5:00/km, HR 165

Why so high?
- Distance ACWR: 50/30.75 = 1.63 (63% increase!)
- Pace ACWR: Much faster pace = high intensity spike
- HR ACWR: 165/150 = 1.10 (physiological stress)

Composite ACWR = 1.71 → Score 87 (WARNING)

Interpretation:
⚠ Race effort + high volume = dangerous combination
⚠ Score 87 - HIGH injury risk
→ Action: Reduce next week to 30-35 km, easy pace only
→ Allow 7-10 days recovery before resuming normal training
```

**Example 3: Undertraining (Injury Recovery)**
```
Scenario: Runner returning after 2-week injury break

Week  | Distance | Pace    | HR  | Distance ACWR | Composite ACWR | Score | Status
──────|──────────|─────────|─────|───────────────|────────────────|───────|────────
-4    | 40 km    | 5:20/km | 155 | -             | -              | -     | -
-3    | 42 km    | 5:18/km | 154 | -             | -              | -     | -
-2    | 0 km     | -       | -   | -             | -              | -     | Break
-1    | 0 km     | -       | -   | -             | -              | -     | Break
Now   | 15 km    | 6:00/km | 145 | 0.37          | 0.42           | 18    | Under

Chronic Avg Distance = (40+42+0+0)/4 = 20.5 km
Acute Distance = 15 km
Distance ACWR = 15/20.5 = 0.73

Interpretation:
↓ ACWR < 0.8 = Detraining zone
↓ Score 18 (Undertraining)
→ This is EXPECTED after injury recovery
→ Gradually rebuild: Week 2: 20km, Week 3: 25km, Week 4: 30km
→ Takes 3-4 weeks to return to chronic baseline safely
```

---

#### Requirements

To calculate ACWR accurately, RunTrend requires:

**Minimum Data:**
- **At least 5 complete periods** (weeks or months)
  - 1 acute period (most recent)
  - 4 chronic periods (baseline average)

**Complete Periods Only:**
- ACWR uses **only fully complete periods** to avoid distortion
- Incomplete current week is NOT included in calculation
- Example: If today is Wednesday, ACWR is calculated from last completed week

**Why 5 Weeks Minimum?**
```
Week:    -4    -3    -2    -1   | Acute (Now)
Status:  ✓     ✓     ✓     ✓   | ✓
         └──── Chronic Avg ────┘  Current

Need: 4 weeks for chronic baseline + 1 acute week = 5 total
```

**Data Quality:**
- **Distance**: Required (core metric)
- **Pace**: Required (cannot be 0 or missing)
- **Heart Rate**: Optional (defaults to neutral 1.0 if missing)

**What Happens with Insufficient Data?**
```
Display:
Training Load: --
Status: "Insufficient data (need 5 complete weeks)"
Message: "Complete at least 5 weeks of training to calculate ACWR"
```

**Best Practices:**
- ✓ Track consistently for 8+ weeks for stable ACWR
- ✓ Ensure GPS watches record accurate distance and pace
- ✓ Use heart rate monitor for complete picture
- ✓ Don't delete old activities - historical data improves accuracy

---

#### When to Take Action

Use Training Load score to guide your training decisions:

**Score 0-40 (Undertraining):**
```
What it means: Significant drop in training load
Common causes:
- Injury recovery / return from break
- Vacation / travel
- Illness recovery
- Intentional taper before race

Action:
✓ If recovering: Gradual return is GOOD (score will rise naturally)
✓ If unplanned: Increase volume by 10-15% per week
✓ Monitor: Should return to 40-65 range within 2-3 weeks
✗ Don't: Jump immediately back to old volume (injury risk)
```

**Score 40-65 (SAFE) ✓**
```
What it means: Optimal training zone - progressive overload without excessive risk
Common causes:
- Consistent week-to-week training
- Gradual volume increases (5-10% per week)
- Well-planned training cycles

Action:
✓ Continue current training plan
✓ This is the GOAL for sustainable long-term improvement
✓ Small week-to-week variations (45→55→50) are normal
✓ Focus on consistency, sleep, nutrition
```

**Score 65-80 (CAUTION):**
```
What it means: Moderate spike - increased injury risk
Common causes:
- Faster-than-planned volume increase
- Added speed work + high volume
- Race effort without reducing weekly volume

Action:
⚠ Hold current volume for 1-2 weeks (don't increase further)
⚠ Prioritize recovery: 8+ hours sleep, proper nutrition
⚠ Monitor for injury signs: unusual soreness, pain, fatigue
✓ Can continue training, but be conservative
✓ Next increase: Wait until score drops to 50-60 range
```

**Score 80-90 (WARNING) ⚠:**
```
What it means: Sharp spike - HIGH injury risk (2-4x normal)
Common causes:
- Race + high training volume same week
- Sudden 30-50% volume increase
- High-intensity week after easy weeks

Action:
→ REDUCE next week's volume by 20-30%
→ Next 3-5 days: Easy runs only (no speed work, no tempo)
→ Monitor daily: If pain/fatigue appears, take rest day immediately
→ Recovery week: Low intensity, focus on sleep/nutrition
→ After 1 week: Re-assess score before resuming normal training

Example:
Current week: 50km → Score 85
Next week: 35km easy pace → Score drops to ~55
Week after: Resume 40-45km → Gradual rebuild
```

**Score 90-100 (DANGER) 🚨:**
```
What it means: EXTREME spike - very high injury risk, overtraining syndrome risk
Common causes:
- Ultra race + continued high volume
- Double previous week's volume
- High volume + high intensity + insufficient recovery

Action:
🚨 IMMEDIATE reduction: Cut volume by 40-50%
🚨 Next 2-3 days: Complete rest OR very easy 20-30min jogs
🚨 Watch for overtraining symptoms:
   - Persistent fatigue despite rest
   - Elevated resting heart rate (+5-10 bpm)
   - Trouble sleeping
   - Loss of motivation
   - Getting sick frequently
🚨 If symptoms appear: Take full rest week, consider medical consultation
→ Recovery: 1-2 weeks of low volume before resuming normal training

Example:
Current week: 80km hard effort → Score 95
Next week: 30-40km EASY pace only
Week 2: 45km easy (if feeling good)
Week 3: 55km (resume normal training if score < 70)
```

**General Guidelines:**
- **Green zone (40-65)**: Train normally
- **Yellow zone (65-80)**: Hold current load, don't increase
- **Orange zone (80-90)**: Reduce load by 20-30%, easy week
- **Red zone (90-100)**: Reduce load by 40-50%, possible rest days

---

#### Complementary Metrics

Training Load (ACWR) works best when combined with other RunTrend metrics:

**1. Training Score**
```
What: Long-term progress (distance, pace, frequency combined)
ACWR: Short-term injury risk (acute vs chronic load)

Use together:
✓ Training Score rising + ACWR 40-65 = Excellent (improving safely)
⚠ Training Score rising + ACWR 80+ = Danger (improving too fast)
✓ Training Score stable + ACWR 40-65 = Maintenance phase (OK)
↓ Training Score falling + ACWR 0-40 = Detraining (expected)

Example:
Training Score: 78 (rising trend)
Training Load: 82 (WARNING)
→ You're improving, but TOO FAST - risk injury
→ Action: Hold current volume for 2 weeks, let body adapt
```

**2. Efficiency Factor**
```
What: Aerobic fitness (pace normalized by heart rate)
ACWR: Training load balance

Use together:
✓ EF rising + ACWR 40-65 = Optimal (fitness improving, safe load)
⚠ EF falling + ACWR 80+ = Overtraining (body not recovering)
⚠ EF falling + ACWR 40-65 = Possible fatigue, illness, or heat

Example:
Efficiency Factor: 11.2 → 10.8 (dropping)
Training Load: 75 (CAUTION)
→ Body is stressed despite "only" caution zone
→ Action: Extra rest days, check for illness/fatigue
```

**3. Average Heart Rate**
```
What: Cardiovascular stress per run
ACWR: Composite load including HR

Use together:
↑ Avg HR rising + ACWR 80+ = High physiological stress
↑ Avg HR rising + same pace = Possible fatigue/overtraining
✓ Avg HR stable + ACWR 40-65 = Good recovery

Example:
Avg HR: 155 → 165 (same pace)
Training Load: 78 (CAUTION)
→ Heart working harder for same effort = fatigue
→ Action: Easy week, prioritize recovery
```

**4. Longest Run**
```
What: Endurance capacity (single run distance)
ACWR: Weekly load balance

Use together:
✓ Long run increasing gradually + ACWR 40-65 = Safe endurance build
⚠ Long run spike (15km → 30km) = Will trigger high ACWR
→ Increase long run by 10-15% per week to keep ACWR safe

Example:
Longest Run: 20km → 32km (60% jump)
Training Load: 85 (WARNING)
→ Long run spike caused ACWR warning
→ Action: Next week's long run: 25km (step back)
```

**5. Rate of Change (RoC)**
```
What: Trend direction (rising/falling/stable)
ACWR: Spike detection

Use together:
✓ Distance RoC positive + ACWR 40-65 = Sustainable growth
⚠ Distance RoC steep + ACWR 80+ = Too aggressive progression
↓ Pace RoC negative (getting faster) + ACWR 80+ = Intensity spike

Example:
Distance RoC: +3 km/week (steep positive trend)
Training Load: 82 (WARNING)
→ Consistent steep progression caused spike
→ Action: Flatten progression to +1-2 km/week
```

**Summary Table:**

| **Metric** | **What it Measures** | **Time Frame** | **Complements ACWR By** |
|------------|----------------------|----------------|-------------------------|
| Training Score | Overall fitness progress | Long-term (months) | Shows if improvements are sustainable |
| Efficiency Factor | Aerobic fitness | Medium-term (weeks) | Detects fatigue/overtraining |
| Average HR | Cardiovascular stress | Per-period (week/month) | Shows physiological response |
| Longest Run | Endurance capacity | Per-period | Identifies long run spikes |
| Rate of Change | Trend direction | Rolling 8-period | Shows if progression is too steep |

**Best Practice:**
Review all metrics together in the Summary Panel for complete picture:
- ✓ All green = Continue training
- ⚠ One metric warning = Monitor closely, adjust if needed
- 🚨 Multiple metrics warning = Take action immediately (reduce load)

---

#### Limitations

ACWR is a powerful tool, but has important limitations:

**1. Individual Variation**
```
Limitation: Everyone tolerates training load differently
- Experienced runners: May handle ACWR 1.4-1.5 safely
- Beginners: May get injured at ACWR 1.2-1.3
- Age, genetics, recovery capacity: All affect tolerance

What this means:
✓ Use ACWR as a GUIDE, not absolute rule
✓ Learn your personal limits over months of tracking
✓ If injury-prone: Stay closer to 0.8-1.2 range
✗ Don't ignore pain/fatigue just because ACWR is "safe"
```

**2. Lagging Indicator**
```
Limitation: ACWR detects spikes AFTER they happen
- Shows THIS week's spike
- Doesn't predict NEXT week's risk
- By the time score is high, you've already done risky training

What this means:
✓ Use ACWR for NEXT week's planning (reduce load if score high)
✓ Plan ahead: Don't create spikes in first place
✓ Combine with forward-looking metrics (RoC trends)
✗ Don't only react - also plan conservatively
```

**3. Doesn't Capture Everything**
```
Limitation: ACWR uses distance, pace, HR - but misses:
- Terrain (trail vs road, hills vs flat)
- Weather (heat, cold, wind add stress)
- Life stress (work, sleep, nutrition)
- Muscular fatigue vs cardiovascular fatigue
- Cumulative fatigue over months

What this means:
✓ ACWR is one tool among many
✓ Listen to your body - fatigue, soreness, motivation
✓ Consider external factors when interpreting score
⚠ Example: ACWR 55 (SAFE) but running in 35°C heat = Still risky
```

**4. Requires Consistent Tracking**
```
Limitation: ACWR accuracy depends on complete data
- Missing weeks: Distorts chronic baseline
- Inconsistent tracking: Unreliable calculations
- Manual entries: May have errors

What this means:
✓ Track every run (GPS watch or manual entry)
✓ Don't delete old activities
✓ 8+ weeks of data = More reliable ACWR
⚠ After a break: ACWR will be skewed for 4-5 weeks
```

**5. Not Injury Proof**
```
Limitation: Low ACWR ≠ Guaranteed safety
- ACWR 0.9 still allows injuries (biomechanics, shoes, terrain)
- Sudden intensity changes can injure even at low ACWR
- Overuse injuries develop over weeks/months (not just acute spikes)

What this means:
✓ ACWR reduces risk, doesn't eliminate it
✓ Still need proper shoes, strength training, rest days
✓ Address pain early, even if ACWR is "safe"
✗ Don't push through pain because score is green
```

**6. Race Weeks are Tricky**
```
Limitation: Races spike ACWR but are necessary for performance
- Race effort = High intensity + high HR
- Often combined with high weekly volume
- Will trigger WARNING/DANGER scores

What this means:
✓ Expect high ACWR during race weeks
✓ Plan recovery week AFTER race (reduce volume 30-50%)
✓ Don't race every week (ACWR will stay dangerously high)
→ Strategy: Race → Recovery week → Gradual rebuild → Race
```

**7. Incomplete Current Period**
```
Limitation: ACWR not shown until period is complete
- If viewing mid-week: No ACWR for current week
- Only sees completed weeks/months
- Can't predict current week's score until it's done

What this means:
✓ Use previous week's score to guide THIS week
✓ If last week was 75 (CAUTION), keep this week conservative
✗ Can't see real-time ACWR during the week
```

**How to Use ACWR Effectively Despite Limitations:**

1. **Combine with subjective feedback:**
   - Morning resting HR (elevated = fatigue)
   - Sleep quality
   - Motivation level
   - Muscle soreness

2. **Use conservative thresholds if:**
   - You're injury-prone
   - You're a beginner (< 1 year running)
   - You're over 45 years old
   - You have prior injuries

3. **Plan ahead:**
   - Build volume gradually (10% rule)
   - Schedule recovery weeks (every 3-4 weeks, reduce 20-30%)
   - After races: Always plan recovery week

4. **Don't panic over single data point:**
   - One high score ≠ guaranteed injury
   - Look at trends over 3-4 weeks
   - Adjust if scores stay elevated

**Remember:** ACWR is a risk management tool, not a crystal ball. Use it to make smarter training decisions, but always listen to your body.

---

### Progress Indicators

#### Marathon Milestone
**What it is:** Estimated date when you'll likely be able to run a 32 km Long Run - the standard training run for marathon preparation.

**Calculation:** Based on **Long Run Projection** (linear regression of last 12 periods).

**Why 32 km and not 42 km?**
- **32 km = 20 miles**: Standard in all professional marathon training plans (Hal Higdon, Pete Pfitzinger, FIRST)
- **Not 42 km in training**: Too high injury risk, too long recovery (2-3 weeks)
- **Marathon-Ready means**: The last 10 km are covered on race day through race conditions

**Status displayed in Summary Panel:**
- **"Estimated: YYYY-MM-DD"**: Estimated date for 32 km Long Run (Marathon-Ready!)
- **"Milestone Reached!"**: You've already completed a 32+ km run
- **"Keep training!"**: Current trend doesn't reach 32 km (projection negative or too flat)

**Interpretation:**
- This is a **Long Run Milestone**, NOT a volume milestone
- Answers the question: "When am I Marathon-Ready?" (32 km Long Run)
- Based only on your Longest Run progression

**Important Difference:**
The Marathon Milestone in the Summary Panel shows ONLY the 32 km Long Run projection. In the Projection Tab, you can see additional milestones:
- **Volume Mode**: 5K, 10K, Half Marathon, Marathon Ready (32K) weekly volume
- **Long Run Mode**: 10K, 15K, Half Marathon, 30K, Marathon Ready (32K) Long Runs

**Example:**
```
Longest Runs last 12 weeks:
Week 1: 15 km
Week 6: 20 km
Week 12: 28 km

Trend: +1 km per week
→ Marathon Milestone: "Estimated: 2025-04-21"
(in ~4 weeks you'll reach 32 km - Marathon Ready!)
```

**Why important:**
- Marathon preparation requires Long Run endurance
- A 32 km Long Run shows Marathon-Readiness
- More important than high weekly volume
- See also: Projection Tab → Long Run Mode for detailed progression

**Training Tip:**
After reaching 32 km you're Marathon-Ready! Typical training plan afterwards:
- 3 weeks before marathon: 32 km Long Run
- 2 weeks before marathon: Tapering (20-25 km)
- 1 week before marathon: Tapering (10-15 km)
- Race day: 42.195 km (with adrenaline + race energy!)

**Note:** The estimate is only as good as your current trend. Changes in the training plan influence the date.

#### Race Time Predictions
**What it is:** Estimated race times for 5K, 10K, Half Marathon, and Marathon based on your Easy Run pace.

**Scientific Basis:** McMillan Calculator (training zone-based prediction)

**Method:**
1. **Identify Easy Runs** (HR-based):
   - Runs with 60-75% of HRmax (Zone 2 / Aerobic Zone)
   - At least 5 km distance
   - Only last 6 months

2. **Calculate Median Easy Pace**:
   - From all identified Easy Runs
   - Median (not Average) = robust against outliers

3. **Apply McMillan Formula**:
   ```
   5K Pace         = Easy Pace - 75 sec/km
   10K Pace        = Easy Pace - 60 sec/km
   Half Marathon   = Easy Pace - 45 sec/km
   Marathon Pace   = Easy Pace - 30 sec/km
   ```

**Example:**
```
Easy Runs identified:
- 10 km @ 6:00/km, HR 140 bpm (70% of 200)
- 8 km @ 6:10/km, HR 138 bpm (69% of 200)
- 12 km @ 5:50/km, HR 142 bpm (71% of 200)

Median Easy Pace: 6:00/km

Predictions:
- 5K:      4:45/km → 23:45 Minutes
- 10K:     5:00/km → 50:00 Minutes
- Half:    5:15/km → 1:50:34
- Marathon: 5:30/km → 3:52:04
```

**Requirements:**
- ✅ Heart rate data available
- ✅ HRmax known (estimated from data)
- ✅ At least 3 Easy Runs (5+ km) in last 6 months
- ✅ Runs in Zone 2 (60-75% HRmax)

**Display in Summary Panel:**
- **5K: 23:45 (4:45/km)** - Time and pace
- **10K: 50:00 (5:00/km)**
- **Half: 1:50:34 (5:15/km)**
- **Marathon: 3:52:04 (5:30/km)**
- Info: "Based on X easy runs (pace: Y/km). McMillan formula with HR zones."

**Important Notes:**

⚠️ **These are ESTIMATES!** Actual race times can vary due to:
- **Race Experience**: First races are often slower
- **Tapering**: Rested legs run faster
- **Course & Weather**: Hills, wind, heat influence greatly
- **Race Fitness vs. Training Fitness**: Some run faster in races

⚠️ **Only for Endurance-Ready Athletes:**
- **5K Prediction**: Meaningful from ~5 km Longest Run
- **10K Prediction**: Meaningful from ~8 km Longest Run
- **Half Prediction**: Meaningful from ~15 km Longest Run
- **Marathon Prediction**: Only after "Marathon Ready" (32 km Long Run!)

**Why HR-based is better than just pace:**

❌ **Just Training Pace**: Mixes Easy/Tempo/Long Runs → inaccurate
✅ **HR-based Easy Run Detection**: Filters real Zone 2 runs → more accurate

**Example of inaccuracy without HR:**
- Athlete A: Trains at 6:00/km (Easy)
- Athlete B: Trains at 6:00/km (Tempo - too hard!)

Both have the same training pace, but Athlete B is faster in races! HR detects the difference.

**Scientific Sources:**
- **McMillan Running Calculator**: Industry standard for 20+ years
- **Jack Daniels VDOT**: VO2max-based predictions (similar method)
- **Heart Rate Zones**: Karvonen Formula, 60-75% = Zone 2

**Improving Accuracy:**

1. **More Easy Runs**: More data, more accuracy
2. **Consistent Training**: Fluctuating fitness → fluctuating predictions
3. **Real Race as Reference**: After a race, estimation becomes more precise (future feature possibility)

### Smoothing

**What it is:** Mathematical smoothing of data for better trend visualization.

**Method:** Simple Moving Average (SMA)

**Options:**
- **Off**: Raw data without smoothing
- **Light**: 3-period window
- **Medium**: 5-period window
- **Strong**: 7-period window

**When to use:**
- With many fluctuations in the data
- To recognize long-term trends
- When individual outliers are distracting

---

## Charts and Visualizations

### Overview Tab

#### Distance Chart
**Shows:** Total distance per period

**Features:**
- Raw data and optionally smoothed line
- **Interactive Legend:**
  - Click on legend entries to show/hide series
  - **Total Distance**: Main metric
  - **Moving Time**: Moving time (initially hidden)
  - **Run Count**: Run count (initially hidden)

**Use of additional series:**
You can see whether a distance increase came from:
- More runs (Run Count increases)
- Longer runs (Run Count constant, but Distance increases)
- Both

**Example:**
- Distance increases from 20 km → 30 km
- Run Count increases from 2 → 3: **More runs**
- Run Count stays at 2: **Longer runs**

**Tip:** Click on "Moving Time" or "Run Count" in the legend to show these series.

**Rate of Change (RoC) Overlay:**
- **Enable:** Check "Show Rate of Change" checkbox above the chart
- **Shows:** Rolling 8-period linear regression slope (purple dashed line)
- **Measures:** How fast your distance is changing per period (km/week or km/month)
- **Right Y-axis:** RoC scale shows rate in km per period

**Interpretation:**
- **Positive RoC** (line above zero): Distance is increasing
  - Example: +2 km/week = adding 2 km per week on average
- **Negative RoC** (line below zero): Distance is decreasing
- **Steep positive slope**: Aggressive volume increase (may trigger high Training Load)
- **Flat line near zero**: Stable volume (maintenance phase)

**Use with Training Load:**
```
Steep Distance RoC (+3 km/week) + Training Load 82 (WARNING)
→ Volume increase is too aggressive
→ Action: Flatten progression to +1-2 km/week
```

**Tip:** Use RoC to see if your volume progression rate is sustainable before it triggers Training Load warnings.

---

#### Pace/Speed Chart
**Shows:** Pace (min/km) or Speed (km/h) per period

**Toggle:** Toolbar → Metric: "Pace" or "Speed"

**Interpretation:**
- **Pace decreases** = speed is improving
- **Speed increases** = speed is improving

**Rate of Change (RoC) Overlay:**
- **Enable:** Check "Show Rate of Change" checkbox above the chart
- **Shows:** Rolling 8-period linear regression slope (purple dashed line)
- **Measures:** How fast your pace/speed is changing per period
- **Right Y-axis:** RoC scale shows rate in min/km per week (pace) or km/h per week (speed)

**Interpretation (Pace mode):**
- **Negative RoC** (line below zero): Getting faster (pace decreasing) ✓
  - Example: -0.05 min/km per week = getting 3 seconds faster per km each week
- **Positive RoC** (line above zero): Getting slower (pace increasing)
- **Flat line near zero**: Stable pace

**Interpretation (Speed mode):**
- **Positive RoC** (line above zero): Getting faster (speed increasing) ✓
  - Example: +0.1 km/h per week = adding 0.1 km/h speed each week
- **Negative RoC** (line below zero): Getting slower
- **Flat line near zero**: Stable speed

**Use with Training Load:**
```
Pace RoC: -0.10 min/km per week (getting much faster)
Training Load: 78 (CAUTION)
→ Intensity increase is significant
→ Combine with volume increase = higher injury risk
→ Action: Stabilize pace while building volume
```

**Tip:** Sharp improvements in pace can contribute to Training Load spikes even if volume is stable. Monitor both metrics together.

---

#### Frequency Chart
**Shows:** Number of runs per period

**Interpretation:**
- Shows training consistency
- Higher values = more regular training
- Combine with Distance Chart for complete picture

### Heart Rate Tab

The Heart Rate Tab visualizes your heart rate data and aerobic fitness development. **Important:** This tab only shows data from runs where a heart rate monitor was used.

**Note when HR data is missing:** If no HR data is available, the message "No HR data available" appears in the chart. This happens when:
- You haven't used a heart rate monitor yet
- The selected timeframe (Start Date) doesn't contain HR runs
- Strava has no HR data for your activities

#### Heart Rate Range (Area Chart)
**Shows:** Min-Max heart rate range per period as blue area

**Visualization:**
- **Blue area**: Shows the range from lowest average HR to highest max HR in the period
- **Lower boundary**: Lowest average HR of a single run (e.g., Recovery Run)
- **Upper boundary**: Highest max HR across all runs (e.g., Tempo Run or race)

**Interpretation:**
- **Wide area**: Different training intensities (good for balanced training!)
- **Narrow area**: Similar intensities in all runs
- **Area rises**: Higher intensities in training
- **Area falls**: Lower intensities (e.g., after intense phase, recovery week)

**Example:**
Week with 4 runs:
- Recovery: Avg 135 bpm, Max 145 bpm
- Easy: Avg 145 bpm, Max 155 bpm
- Tempo: Avg 165 bpm, Max 175 bpm
- Long: Avg 150 bpm, Max 170 bpm

→ **Area from 135 bpm (lower boundary) to 175 bpm (upper boundary)**

**Use:**
- See if you're using different training zones
- See if you're training too monotonously (narrow area)
- Identify weeks with high intensity (high upper boundary)

#### Average Heart Rate Line
**Shows:** Average heart rate per period as red line

**Calculation:** Mean of all average HR values of runs with HR data in the period

**Interpretation:**
- **Constant line**: Consistent average intensity
- **Falling line at same pace**: Better aerobic fitness!
- **Rising line**: Higher training intensity or possible fatigue

**Important:** A falling Average HR alone does NOT automatically mean better fitness. You must view this in combination with your Pace/Speed!

**Example - Fitness Improvement:**
- Month 1: Avg HR 155 bpm at 6:00 min/km
- Month 3: Avg HR 150 bpm at 5:45 min/km
→ **HR falls AND pace improves = real fitness improvement!**

**Example - No Fitness Progress:**
- Month 1: Avg HR 155 bpm at 6:00 min/km
- Month 3: Avg HR 150 bpm at 6:30 min/km
→ HR falls, but pace is slower = probably just slower training

**That's exactly why there's the Efficiency Factor!**

#### Efficiency Factor (EF) Line
**Shows:** Pace-normalized heart rate as green line - THE key metric for aerobic fitness

**What it is:**
The Efficiency Factor (EF) is the ratio of speed to heart rate. It shows how efficiently your cardiovascular system works.

**Formula:**
```
EF = Speed (m/s) / Average Heart Rate (bpm)
```

**Display:** Multiplied by 1000 for better readability (e.g., 0.0179 → 17.9)

**Why is EF better than raw HR?**

Raw heart rate alone is misleading:
- Tempo Run with 165 bpm: Is that good or bad?
- Easy Run with 140 bpm: Is that more efficient?

**→ Without knowing the pace, HR is worthless!**

EF normalizes HR for different speeds and makes it comparable.

**Interpretation:**
- **Higher EF = better aerobic fitness**
- **Rising EF over months** = fitness is improving
- **Constant EF despite higher volume** = good recovery and adaptation
- **Falling EF** = possible overtraining, fatigue, or illness

**Example - EF shows real progress:**

**Month 1:**
- Pace: 6:00 min/km = 2.78 m/s
- Avg HR: 155 bpm
- **EF = 2.78 / 155 = 0.0179 (displayed: 17.9)**

**Month 3:**
- Pace: 5:30 min/km = 3.03 m/s
- Avg HR: 150 bpm
- **EF = 3.03 / 150 = 0.0202 (displayed: 20.2)**

**→ EF rose from 17.9 to 20.2 = significant fitness improvement!**

You're running faster at lower heart rate - that's real aerobic development!

**Long-term EF Development:**

**Beginner Phase (Months 1-3):**
- EF rises quickly (e.g., 15 → 18)
- Large aerobic adaptations

**Advanced Phase (Months 4-12):**
- EF rises slower (e.g., 18 → 20)
- Fine-tuning of aerobic capacity

**Elite Phase:**
- EF stabilizes at high level (e.g., 22-25)
- Small fluctuations due to training load

**Practical Use:**

1. **Fitness Check**: Compare EF every 4-6 weeks
2. **Training Adjustment**: Falling EF → plan more recovery
3. **Race Readiness**: Rising/stable EF → good form
4. **Overtraining Warning**: Constantly falling EF over weeks → take a break!

**Interactive Legend:**
Click on legend entries to show/hide series:
- **HR Range (Min-Max)**: Blue area
- **Average HR**: Red line
- **Efficiency Factor (×1000)**: Green line

**Smoothing:**
The smoothing filter from the toolbar is applied to Average HR and EF. Use Smoothing (Light/Medium/Strong) to better recognize trends with fluctuating data.

**Dual Y-Axes:**
- **Left Y-Axis**: Heart rate in bpm (for HR Range and Average HR)
- **Right Y-Axis**: Efficiency Factor ×1000 (for EF Line) OR HR RoC when RoC overlay is enabled

---

#### Rate of Change (RoC) Overlay

**Enable:** Check "Show Rate of Change" checkbox above the chart

**Shows:** Rolling 8-period linear regression slope for Average Heart Rate (purple dashed line)

**Measures:** How fast your average HR is changing per period (bpm/week or bpm/month)

**Right Y-axis:** When RoC is enabled, the right axis shows HR RoC scale (bpm per period) instead of EF

**Interpretation:**
- **Positive RoC** (line above zero): HR is increasing
  - Example: +2 bpm/week = heart rate rising by 2 beats per week
  - **Possible causes:**
    - Increasing training intensity
    - Fatigue accumulation
    - Overtraining
    - Heat stress (summer training)
    - Illness developing
- **Negative RoC** (line below zero): HR is decreasing ✓
  - Example: -1 bpm/week = heart rate falling by 1 beat per week
  - **Possible causes:**
    - Improving aerobic fitness
    - Better training adaptation
    - Recovery phase working well
- **Flat line near zero**: Stable HR (maintenance phase)

**Use with Training Load:**
```
Avg HR RoC: +3 bpm/week (rising trend)
Training Load: 75 (CAUTION)
Pace: Stable (no improvement)
→ Heart working harder for same pace = fatigue
→ Action: Extra recovery days, check for illness/overtraining
```

**Use with Efficiency Factor:**
```
Scenario 1: HR rising, EF stable
→ HR RoC: +2 bpm/week
→ EF: Stable at 18.5
→ Interpretation: Possibly just higher training intensity (OK if planned)

Scenario 2: HR rising, EF falling
→ HR RoC: +2 bpm/week
→ EF: Falling from 18.5 → 17.2
→ Interpretation: Warning sign of overtraining/fatigue
→ Action: Plan recovery week, reduce intensity
```

**Important Note:**
- HR RoC is especially useful for detecting **gradual fatigue accumulation**
- A single high HR day isn't concerning, but a **rising trend over weeks** signals a problem
- Always combine with EF and subjective feedback (sleep, motivation, soreness)

**Tip:** Enable RoC when you suspect overtraining or want to validate that your recovery weeks are working (RoC should flatten or turn negative during recovery).

---

**Tip for Marathon Training:**
Track your EF during the build-up phase. A rising or stable EF shows that your body is handling the increased training volume well. A falling EF can be a warning sign of overtraining - plan more recovery weeks!

### Endurance Tab

#### Longest Run Chart
**Shows:** Longest single run per period

**Why important:**
- **Core metric for marathon preparation**
- Shows long-distance endurance
- Cannot be derived from total distance

**Example Use:**
Track your Long Run progress:
- Week 1: 15 km
- Week 4: 18 km
- Week 8: 21 km (half marathon distance reached!)
- Week 12: 25 km
- Week 16: 30 km (marathon preparation on track)

#### Avg Distance/Run Chart
**Shows:** Average distance per run

**Interpretation:**
- Shows typical run structure
- **Not always "higher is better"**
- Can decrease when you do more shorter recovery runs
- Combine with Total Distance for complete picture

**Example Scenarios:**

**Scenario 1: Volume Build-up through Frequency**
- Avg Distance decreases: 10 km → 7 km
- Total Distance increases: 20 km → 28 km
- Run Count increases: 2 → 4
- **Interpretation**: More runs, stable structure

**Scenario 2: Specialization on Long Runs**
- Avg Distance constant: 10 km
- Total Distance constant: 30 km
- Longest Run increases: 12 km → 20 km
- **Interpretation**: Focus on weekly Long Run

### Score Tab

#### Training Score Chart
**Shows:** Combined training progress (0-100)

**Components (with HR data):**
- 30% Distance
- 30% Pace
- 20% Efficiency Factor (aerobic fitness)
- 20% Frequency

**Components (without HR data):**
- 37.5% Distance
- 37.5% Pace
- 25% Frequency

**Adaptive Weighting:**
The score automatically adapts to available data:
- **With HR data**: Efficiency Factor flows in with 20%
- **Without HR data**: Weights are proportionally adjusted

This enables consistent score calculation even with mixed data (some periods with HR, some without).

**Interpretation:**
- 0-30: Below baseline level
- 30-60: In baseline range
- 60-80: Above baseline, good progress
- 80-100: Well above baseline, excellent progress

**What the score measures:**
- **Volume**: Total distance compared to your average
- **Quality**: Pace improvement compared to your average
- **Efficiency**: Aerobic fitness (when HR data available)
- **Consistency**: Regularity of training

**Important Notes:**
- The score is a summary. It does NOT replace structural details!
- For marathon preparation, also look at Longest Run in the Endurance Tab
- The score reacts to long-term trends, not individual workouts
- Baseline is calculated as rolling average (adaptive)

**Example - Score Development:**
- **Week 1**: Score 45 (baseline level)
- **Week 4**: Score 62 (volume increased, pace improved)
- **Week 8**: Score 75 (Efficiency Factor increased, constant volume)
- **Week 12**: Score 58 (recovery week, lower score is OK!)

A falling score is not always bad - recovery weeks are important!

### Training Load Tab

#### Training Load (ACWR) Chart

**Shows:** Training Load score (0-100) over time with colored safe zones to detect overtraining risk.

**What is ACWR?**
ACWR (Acute:Chronic Workload Ratio) compares your recent training load to your baseline load. This scientifically-validated metric helps you train safely by detecting dangerous spikes or drops in training volume, intensity, and physiological stress.

**For detailed explanation** of how ACWR is calculated, see: **Metrics Explanations → Training Load (ACWR)**

---

#### Visualization Features

**1. Training Load Line (Blue)**
- Shows your composite Training Load score (0-100) per period
- Combines Distance (40%), Pace (30%), and Heart Rate (30%) into a single overtraining risk indicator
- Higher values = higher injury risk from training spikes
- Lower values = detraining risk from insufficient load

**2. Colored Background Zones**
The chart displays colored zones to help you quickly assess training safety:

```
Zone Color    Score Range    Status          Risk Level
──────────────────────────────────────────────────────────
Light Gray    0-40          Undertraining    Detraining risk
Green         40-65         SAFE             Optimal zone ✓
Yellow        65-80         CAUTION          Moderate risk
Orange        80-90         WARNING          High risk ⚠
Red           90-100        DANGER           Very high risk 🚨
```

**Visual Guide:**
```
100 ┤                                    ╔═══════════╗
 90 ┤                                    ║  DANGER   ║ RED
 80 ┤                            ╔═══════╩═══════════╝
 70 ┤                            ║    WARNING         ORANGE
 65 ┤                    ╔═══════╩═══════╗
 60 ┤                    ║    CAUTION     ║ YELLOW
 50 ┤        ╔═══════════╩════════════════╝
 40 ┤        ║         SAFE ZONE          ║ GREEN ✓
 30 ┤        ║                            ║
 20 ┤╔═══════╩════════════════════════════╝
 10 ┤║      UNDERTRAINING                 ║ GRAY
  0 ┴╚════════════════════════════════════╝
```

**3. Interactive Legend**
- Click legend entries to show/hide the Training Load line
- All series can be toggled on/off

---

#### How to Interpret the Chart

**Line in GREEN zone (40-65) - SAFE ✓**
```
What it means:
✓ Optimal training zone
✓ Progressive overload without excessive injury risk
✓ Body can adapt to current load

Action:
→ Continue training as planned
→ This is the GOAL for sustainable long-term improvement
```

**Line entering YELLOW zone (65-80) - CAUTION**
```
What it means:
⚠ Moderate spike in training load
⚠ Increased injury risk
⚠ Training progression may be too aggressive

Action:
→ Hold current volume for 1-2 weeks (don't increase further)
→ Prioritize recovery: sleep, nutrition, rest days
→ Monitor for injury signs: unusual soreness, pain, fatigue
```

**Line entering ORANGE zone (80-90) - WARNING ⚠**
```
What it means:
🚨 Sharp spike - HIGH injury risk (2-4x normal)
🚨 Dangerous combination of volume, intensity, or physiological stress
🚨 Immediate action needed

Action:
→ REDUCE next week's volume by 20-30%
→ Next 3-5 days: Easy runs only (no speed work, no tempo)
→ Focus on recovery week with low intensity
→ Re-assess score before resuming normal training
```

**Line entering RED zone (90-100) - DANGER 🚨**
```
What it means:
🔴 EXTREME spike - very high injury risk
🔴 Risk of overtraining syndrome
🔴 Immediate reduction required

Action:
→ IMMEDIATE reduction: Cut volume by 40-50%
→ Next 2-3 days: Complete rest OR very easy 20-30min jogs
→ Watch for overtraining symptoms:
   - Persistent fatigue despite rest
   - Elevated resting heart rate (+5-10 bpm)
   - Trouble sleeping
   - Loss of motivation
→ If symptoms appear: Full rest week, consider medical consultation
```

**Line in GRAY zone (0-40) - Undertraining**
```
What it means:
↓ Significant drop in training load
↓ Risk of detraining and fitness loss

Common causes:
- Injury recovery / return from break
- Vacation / travel
- Illness recovery
- Intentional taper before race

Action:
✓ If recovering: Gradual return is GOOD (score will rise naturally)
✓ If unplanned: Increase volume by 10-15% per week
✗ Don't jump immediately back to old volume (injury risk)
```

---

#### Practical Use Cases

**Use Case 1: Detecting Race Week Spikes**
```
Scenario: You ran a half marathon race

Week 1-4:  Score 52-58 (GREEN - consistent training)
Week 5:    Score 85 (ORANGE - race effort + race volume)
          ⚠ WARNING: High injury risk

Action:
→ Week 6: Recovery week (30-50% volume reduction)
→ Score will drop back to GREEN zone
→ Week 7: Gradual return to normal training
```

**Use Case 2: Monitoring Training Progression**
```
Scenario: Building up volume for marathon training

Week 1:  30 km, Score 48 (GREEN)
Week 2:  33 km, Score 52 (GREEN) ✓ Safe increase
Week 3:  36 km, Score 56 (GREEN) ✓ Safe increase
Week 4:  40 km, Score 61 (GREEN) ✓ Safe increase
Week 5:  55 km, Score 78 (YELLOW) ⚠ Too aggressive!

Action:
→ Week 6: Hold at 40-42 km (don't increase further)
→ Let body adapt for 1-2 weeks
→ Score will stabilize back to GREEN
→ Then continue gradual progression
```

**Use Case 3: Return from Injury**
```
Scenario: Returning after 2-week running break

Week -2 to -1:  0 km (injury break)
Week 1:         15 km, Score 18 (GRAY - undertraining)
                ✓ Expected after break

Week 2:         20 km, Score 28 (GRAY)
Week 3:         25 km, Score 42 (GREEN) ✓ Back to safe zone
Week 4:         30 km, Score 55 (GREEN) ✓ Fully recovered

Interpretation:
→ Gradual rebuild over 3-4 weeks is CORRECT approach
→ Score naturally rises as chronic baseline adjusts
→ Patience prevents re-injury
```

---

#### Data Requirements

To display the Training Load Chart:
- **Minimum 5 complete periods** (weeks or months)
  - 1 acute period (most recent)
  - 4 chronic periods (baseline average)

**When insufficient data:**
```
Display: Empty chart with message
"Training Load requires at least 5 complete periods"

Solution:
→ Continue training and tracking
→ Chart will appear once 5 periods are completed
```

**Complete periods only:**
- Only fully completed weeks/months are used
- Incomplete current period is NOT shown (prevents misleading data)
- Example: If today is Wednesday, chart shows up to last completed week

---

#### Tips for Using Training Load Chart

**1. Check After Every Week/Month**
Review your latest Training Load score to plan next period:
- GREEN (40-65): Continue as planned
- YELLOW (65-80): Hold volume, don't increase
- ORANGE/RED (80-100): Reduce volume, recovery needed

**2. Plan Recovery Weeks**
Use the chart to schedule strategic recovery:
- Every 3-4 weeks: Reduce volume by 20-30%
- After races: Expect ORANGE/RED scores → plan recovery week
- If score rises toward YELLOW: Hold load instead of increasing

**3. Compare with Training Score**
View both charts together for complete picture:
- **Training Score**: Long-term progress (am I improving?)
- **Training Load**: Short-term risk (am I training safely?)

**Ideal scenario:**
✓ Training Score rising (making progress)
✓ Training Load in GREEN zone (progressing safely)

**Warning scenario:**
⚠ Training Score rising (making progress)
⚠ Training Load in ORANGE/RED (progressing too fast)
→ You're improving, but risk injury - slow down progression

**4. Use with Rate of Change (RoC)**
Enable RoC overlays on Distance/Pace/HR charts to see:
- If trends are too steep (causes high Training Load)
- If progression rate is sustainable
- When to flatten progression to avoid spikes

**5. Track Patterns Over Months**
Look for patterns in your Training Load:
- Do you consistently spike after races?
- Do certain training blocks trigger YELLOW/ORANGE zones?
- How long does it take to recover from spikes?
- Learn your personal tolerance and adjust training accordingly

---

#### Important Notes

**Training Load vs Training Score:**

| Metric | Purpose | Time Frame | Interpretation |
|--------|---------|------------|----------------|
| **Training Score** | Measures progress/fitness | Long-term (months) | Higher = better fitness |
| **Training Load (ACWR)** | Detects injury risk | Short-term (acute vs chronic) | GREEN zone = optimal, HIGH scores = danger |

They measure DIFFERENT things:
- ✓ Training Score 75 + Training Load 52 (GREEN) = Excellent (fit AND safe)
- ⚠ Training Score 75 + Training Load 85 (ORANGE) = Risky (fit BUT unsafe progression)

**Limitations:**
- ACWR is a **risk indicator**, not a guarantee
- Individual tolerance varies (experience, age, injury history)
- Doesn't capture terrain, weather, life stress, or nutrition
- Use as **one tool among many** - always listen to your body
- See **Metrics Explanations → Training Load (ACWR) → Limitations** for full details

**Best Practice:**
Combine Training Load Chart with:
- Summary Panel (quick status overview)
- Efficiency Factor (detect fatigue/overtraining)
- Average Heart Rate (physiological stress indicator)
- Subjective feedback (fatigue, soreness, motivation, sleep quality)

---

### Performance Tab

Shows how your current form compares to an **age-adjusted reference** —
two scientifically distinct views in one tab.

#### When is this chart useful?

When you want to know *how far you are from your possible peak form for
your age* — unlike the Score chart, which only compares you to your own
rolling baseline.

#### Prerequisites

Under **Settings → General → Profile** you need:

- **Date of birth** (used by both views)
- **Gender** (only required for the WMA view — the tables are
  gender-specific)

Both are stored optionally; without a date of birth the tab stays empty
with a hint. "Prefer not to say" for gender disables only the WMA view,
not the HF view.

#### View 1: WMA Age-Graded %

**Data source:** [World Masters Athletics 2023](https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf)
age-factor tables (in force since 2023-01-01, derived from more than
2.8 million competition times, with per-year factors from age 30 to 110).

**Formula:**
```
Age-graded % = (world-record time × age factor) ÷ your time × 100
```

**Performance bands:**

| Range       | Classification       |
|-------------|----------------------|
| ≥ 90 %      | International class  |
| 80–90 %     | National class       |
| 70–80 %     | Regional class       |
| 60–70 %     | Local class          |
| < 60 %      | Recreational         |

**Chart content:**
- Four coloured lines for 5K, 10K, half marathon, marathon
- Each datapoint = HR-based McMillan prediction from a rolling 3-month
  window (same mechanism as the race-time predictions in the summary
  panel)
- Dotted reference lines at 60/70/80/90/100 %
- Actual race results (right-click on a run → "Mark as race") appear
  as larger scatter points with a darker shade on their distance line —
  real times are more reliable than predictions

**Note:** The factors are age-specific, so the chart uses *your age at
the time of each datapoint*. A 5K from two years ago at the same pace
shows a *different* % than today.

#### View 2: Aerobic Capacity %

**Data source:** Your own Efficiency Factor (EF) over time, with an
age-based decline model from the literature.

**Methodological caveats up front:**

- Friel (Joe Friel Training) and TrainingPeaks **explicitly warn**
  against comparing EF across athletes. We therefore do not — the
  reference line is your own personal best.
- HRmax is estimated via **Tanaka (2001):** `208 − 0.7 × age`
  (meta-analysis over 351 studies, n=18,712, gender-independent). More
  accurate than the old `220 − age` from about age 40 onward.

**Personal peak EF:**
- Best 4-week mean of your EF in the past 12 months
- Shown as a horizontal dotted grey line
- If you maintain training volume, your EF should oscillate near this

**Expected EF curve (dashed orange):**
Forward-extrapolated from your peak using an age-driven decline rate.
The rate depends on your recent training volume:

| Training status                    | Decline per year |
|------------------------------------|------------------|
| Volume maintained                  | 0.5–0.65 %       |
| Moderate reduction (11–20 %)       | 0.8–2.6 %        |
| Sedentary (reduction > 20 %)       | 1.5–4.6 %        |

Source: [Coppola et al. 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9517884/),
meta-analysis of longitudinal masters-athlete studies. Training-volume
change alone explains 54 % / 39 % (men / women) of individual decline
variance.

**Caveat:** Linear decline is a **first approximation**. After about
age 70 the decline accelerates as mitochondrial mechanisms become more
dominant than reduced cardiac output ([review PMC9975246](https://pmc.ncbi.nlm.nih.gov/articles/PMC9975246/)).
The linear path holds up well below 70.

**Header line:**
```
Current EF: 24.3 • 96% of age-adjusted peak • Decline rate ~0.7%/yr (vol ratio 0.95)
```

- **Current EF:** Your latest EF × 1000 (same unit as the Heart Rate tab)
- **% of age-adjusted peak:** How close you are to your age-adjusted peak
- **Decline rate:** The decline rate currently applied (derived from
  your volume ratio)
- **Vol ratio:** Current volume divided by peak-period volume

#### Interpretation

- The two views **rank** form over time — neither is "better".
- WMA is good for **competition perspective** (How would I rank in a
  masters category?).
- HF is good for **training response** (Am I currently responding to my
  training? Am I trailing my own potential?).

#### Sources

- [WMA 2023 Age Factors PDF](https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf)
- [Howard Grubb's WMA-2023 calculator + Excel data](https://howardgrubb.co.uk/athletics/wmatnf23.html)
- [Tanaka et al. (2001), "Age-predicted maximal heart rate revisited"](https://pubmed.ncbi.nlm.nih.gov/11153730/) — *J Am Coll Cardiol* 37(1)
- [Coppola et al. (2022), "Impact of Training on the Loss of CRF in Aging Masters Endurance Athletes"](https://pmc.ncbi.nlm.nih.gov/articles/PMC9517884/) — *Int J Environ Res Public Health* 19(17)
- [Joe Friel — Efficiency Factor in Running](https://joefrieltraining.com/the-efficiency-factor-in-running-2/)

---

### Projection Tab

#### Settings

**Projection Mode:**
- **Volume (Total Distance)**: Projects weekly/monthly total distance
- **Long Run**: Projects the longest run per period

**Periods Ahead:**
- Select how far into the future to project
- **Week mode**: 1-104 weeks (2 years)
- **Month mode**: 1-24 months (2 years)
- Default: 12 periods

**Note:** Settings are automatically saved and restored on next start.

#### Projection Modes

**Volume Projection Mode:**
- Projects weekly/monthly total distance
- Shows milestones:
  - 5K total
  - 10K total
  - Half Marathon (21.1 km) total
  - Marathon (42.195 km) total

**Question answered:** "When will my weekly volume reach 42 km?"

**Long Run Projection Mode:**
- Projects the longest run per period
- Shows endurance milestones:
  - 10K Long Run
  - 15K Long Run
  - Half Marathon (21.1 km) Long Run
  - 30K Long Run
  - **Marathon Ready (32 km) Long Run** - Standard for marathon preparation

**Question answered:** "When am I Marathon-Ready?" (able to run 32 km)

**Important Difference:**
These two questions are NOT the same for marathon preparation!

- Weekly volume of 42 km does NOT mean you can run 42 km in one go
- A 32 km Long Run shows Marathon-Readiness (standard in professional training plans)
- The full 42 km are achieved on race day through race energy

**Example:**
- Athlete A: 50 km/week with 5 × 10 km runs, longest: 10 km
- Athlete B: 40 km/week with 1 × 30 km + 2 × 5 km, longest: 30 km

Athlete B is closer to the marathon goal (only needs 2 km more to 32 km = Marathon Ready), despite lower weekly volume!

#### Understanding Projection

**Method:** Linear regression based on last 12 periods

**Interpretation:**
- **Solid line**: Historical data
- **Dashed line**: Projection into the future
- **Orange points**: Estimated milestone timepoints
- **X-Axis**: Shows actual calendar dates (e.g., "Jan 2024", "Feb 2024")
- **Interactive Legend**: Click on legend entries to show/hide

**Chart Controls:**
- Use the **Periods Ahead** setting to look further/less far into the future
- Switch between **Volume** and **Long Run** mode for different perspectives
- The milestone points show you WHEN you'll likely reach a specific goal

**Important:** Projections are estimates based on past progress. Actual results can vary due to:
- Training breaks
- Injuries
- Changes in training plan
- Seasonal fluctuations

---

## Settings

### Settings Dialog

The Settings dialog contains all important configurations and actions:

**Strava API Configuration:**
1. Go to https://www.strava.com/settings/api
2. Create a new API application (if not already done)
3. Copy **Client ID** and **Client Secret**
4. Enter them in the Settings dialog
5. Click **Save**

**Strava Actions:**
- **Connect to Strava**: Establish connection to Strava (opens browser for OAuth)
  - After successful connection, you'll be asked if you want to synchronize immediately
- **Sync Activities**: Download activities from Strava (enabled when connected)
- **Disconnect Strava & Delete All Data**: Complete disconnection and data removal (enabled when connected)
  - **What it does:**
    - Removes RunTrend from your Strava authorized apps (calls Strava's deauthorization endpoint)
    - Deletes all synced activities from your device
    - Clears all OAuth tokens
    - Keeps your API credentials so you can reconnect later
  - **Warning**: This action cannot be undone! You'll receive a confirmation dialog showing exactly what will be deleted
  - **Privacy**: Your data is stored locally only. This deletion removes it completely from your device
  - **Reconnecting**: After deletion, you can connect again anytime. Your Strava data remains on Strava's servers
  - **Manual alternative**: You can also revoke RunTrend's access at https://www.strava.com/settings/apps
- **Status**: Shows current connection status (Green = connected, Gray = not connected)

**Heart Rate Configuration:**
- **Max Heart Rate**: Optional manual HRmax setting
  - **Auto-detect** (default): The app automatically detects your HRmax from your activities
    - Automatically applies a 10% safety margin (since most runners never reach their true HRmax in training)
  - **Set manually**: If you know your true HRmax, you can enter it here (100-220 bpm)
    - Improves accuracy of Race Time Predictions
    - Use the warning in the Summary Panel as a hint if auto-detection is implausible
    - **After saving**: Summary Panel is automatically refreshed with new Race Predictions
    - You'll receive confirmation like "Manual HRmax set to 190 bpm. Race predictions will be updated."
  - **When to set manually?**
    - You've done an HRmax test (e.g., at sports doctor)
    - Summary Panel shows an orange warning with suggestion
    - Your Race Time Predictions appear unrealistic
  - **Context-aware messages**: The app automatically detects what you changed:
    - Only HRmax changed → Note about Race Predictions
    - Only Strava credentials changed → Note about connecting
    - Both changed → Combined message

**Automatic Synchronization:**
- **On start**: The app automatically checks on startup for new activities (silent sync)
- **After Connect**: You're asked after successful OAuth connection if you want to synchronize
- **Token Refresh**: Access tokens are automatically renewed (every ~6 hours) - no manual action needed

### Data Management

- **Start Date** (Toolbar): Filters from when data is displayed in charts
  - On first sync: Determines from when activities are imported (default: January 1, 2000)
  - After first sync: Only filters display, data remains in database
- **Period** (Toolbar): Week = ISO week calendar (Monday-Sunday), Month = calendar month
- **Sync**: Incremental synchronization (only new/changed activities)

### Saved Settings

The application automatically saves:
- Start Date
- Period (Week/Month)
- Metric (Pace/Speed)
- Smoothing Level
- Projection Mode
- Projection Periods Ahead

On next start, these settings are restored.

### Tips

- **First Synchronization**: Default (since 2000) guaranteed to import all Strava activities
- **Start Date as Filter**: After import, you can use the Start Date to display e.g., only the current training phase
- **Regular Synchronization**: Sync after new runs for current data (or use automatic sync on app start)
- **Adjust Smoothing**: Use stronger smoothing with many fluctuations

---

## Methodological Caveats

RunTrend uses established methods wherever possible and explicitly
flags self-assembled components. This section lists the substantive
metrics with their source and known limitations. When in doubt: use
the values as an **indicator**, not as a diagnostic tool.

### Metric overview

| Metric | Source | Status | Most important limitation |
|---|---|---|---|
| **Training Score (0–100)** | `specification.md` §10 (own definition) | self-assembled | Weights (30/20/30/20) chosen ad-hoc; at steady state the value plateaus around ~50 by design — see **Training Fitness (CTL)** for an absolute measure |
| **Training Fitness (CTL)** | Coggan (TrainingPeaks Performance Manager), Banister 1991 (TRIMP) | published / established | TRIMP scale isn't directly 1:1 with TSS-CTL from cycling — relative banding maps across, absolute numbers differ |
| **Form (TSB)** | Coggan | published | Zone thresholds (+25 / +10 / −10 / −20 / −30) are guidelines, not causally validated cutoffs |
| **ACWR (Training Load)** | Gabbett 2016 | published, contested | Impellizzeri et al. 2020 demonstrate mathematical artefacts at small chronic values and weak injury correlations in follow-up studies — read thresholds as indicator, not diagnosis |
| **Race Predictions** | McMillan Running Calculator | empirically widespread | Not peer-reviewed. 5K predictions tend to be tight; Marathon predictions ±10% typical |
| **WMA Age-Graded % (Performance tab)** | WMA 2023 factor tables (derived from 2.8M competition times) | published | Factors start at age 30; younger → factor 1.0 (open class) |
| **Aerobic Capacity % (Performance tab)** | Friel/TrainingPeaks (EF), Tanaka 2001 (HRmax), Coppola 2022 (decline) | published building blocks, own composite | The personal-peak extraction methodology is RunTrend-internal design, not published. Linear decline imprecise past age 70 |
| **Tanaka HRmax** (`208 − 0.7 × age`) | Tanaka 2001 (meta-analysis n=18,712) | published | More accurate than `220 − age` from ~age 40 on, gender-independent |
| **Banister TRIMP** | Banister 1991 | published, gold standard | Edwards' zone-TRIMP would be a simpler alternative without the HR-reserve requirement |
| **HR Zones (Performance tab)** | classic 5-zone model or Karvonen | established | Classic model ignores HR reserve; Karvonen variant corrects for that (needs HR-rest) |

### What "indicator vs. diagnosis" means

Sport-science metrics are **statistical correlations across athlete
populations**. They tell you where your training point typically falls
and which direction it's moving. They do **not** tell you with
certainty whether you're currently overtraining or building form —
that requires heart-rate variability, sleep quality, RPE, blood
markers, and other inputs taken together.

**Practical implications:**

- Trust the **direction** more than the absolute number. CTL rising
  over weeks = you're building fitness; TSB falling = you're absorbing
  load — both are robust statements.
- Trust your **body sensation** over a red number. ACWR > 1.5 while
  you feel good is probably not a crisis signal. ACWR in the sweet
  spot while you're exhausted means take a rest day.
- Compare **yourself to yourself over time**, not against other apps
  or other athletes. CTL from RunTrend is not directly comparable to
  CTL from TrainingPeaks (TRIMP vs TSS scale).

### Sources

- Banister, E. W. (1991). "Modeling Elite Athletic Performance."
- Coggan, A., "Performance Manager" — <https://www.trainingpeaks.com/learn/articles/the-science-of-the-performance-manager/>
- Coppola et al. 2022 — <https://pmc.ncbi.nlm.nih.gov/articles/PMC9517884/>
- Gabbett, T. J. (2016). "The training-injury prevention paradox" —
  *Br J Sports Med* 50(5): 273–280
- Impellizzeri, F. M., et al. (2020). "Acute:chronic workload ratio:
  conceptual issues and fundamental pitfalls" — *Int J Sports Physiol
  Perform* 15(6): 907–913
- McMillan Running Calculator — <https://www.mcmillanrunning.com/>
- Tanaka et al. 2001 — <https://pubmed.ncbi.nlm.nih.gov/11153730/>
- WMA 2023 Age Factors — <https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf>

---

## Frequently Asked Questions

### Why aren't my treadmill runs displayed?

Treadmill runs (VirtualRun) are deliberately excluded because the application focuses on outdoor training.

### How is weighted pace calculated?

Weighted Pace = Total Moving Time / Total Distance

This gives a more accurate average because longer runs are weighted more heavily.

### What's the difference between Total Distance and Longest Run?

- **Total Distance**: Sum of all runs (volume)
- **Longest Run**: Longest single run (endurance capability)

Both are important but different metrics. For marathon preparation, Longest Run is especially important.

### Why is my Average Distance per Run decreasing even though I'm training more?

That's normal! If you run more frequently but include shorter sessions (e.g., Recovery Runs), the average decreases. What matters is total distance AND structural balance.

### How do I use the interactive legend in charts?

All charts have an interactive legend at the bottom. Click on a legend entry to show/hide the corresponding series.

**Example Distance Chart:**
Click on "Run Count" in the legend to see:
- Distance increases + Run Count increases = More runs
- Distance increases + Run Count constant = Longer runs
- Distance constant + Run Count increases = More short runs

**Tip:** Deactivated series are displayed in gray. Click again to reactivate them.

### Are the projections reliable?

Projections are estimates based on linear regression of your past data. They're helpful for trend analysis but not exact. Real results can vary due to many factors.

### Do I need to synchronize manually or does it happen automatically?

The app partially synchronizes automatically:

**Automatic:**
- On app start, silent background synchronization is performed (if data already exists)
- Status messages only appear with new activities or errors
- Access tokens are automatically renewed without user interaction

**Manual:**
- After first "Connect to Strava" you're asked if you want to synchronize
- You can always click "Sync Activities" in Settings for immediate synchronization with progress dialog

**Tip:** For regular updates, simply start the app daily/weekly - automatic background sync keeps your data current!

### Why does the Heart Rate Tab show "No HR data available"?

The Heart Rate Tab only shows data from runs where a heart rate monitor was used. "No HR data available" appears when:

1. **You haven't used an HR monitor yet**: Runs without HR device have no heart rate data
2. **Time filter**: The selected Start Date filters out all HR runs
3. **Strava has no HR data**: Older runs or manually entered activities

**Solution:**
- Use a heart rate monitor (chest strap or optical sensor on watch)
- Adjust the Start Date in the toolbar to include runs with HR data
- Synchronize newer runs with HR monitor

### What is the Efficiency Factor and why is it important?

The Efficiency Factor (EF) is the ratio of speed to heart rate:

```
EF = Speed (m/s) / Average Heart Rate (bpm)
```

**Why important:**
- Raw heart rate alone is misleading (faster pace = naturally higher HR)
- EF normalizes HR for different speeds
- **Higher EF = better aerobic fitness**
- Enables fair comparison between different runs

**Example:**
- 3 months ago: 6:00 min/km at 155 bpm → EF = 17.9
- Today: 5:30 min/km at 150 bpm → EF = 20.2
- **→ EF increased = real fitness improvement!**

You're running faster at lower heart rate - that's aerobic development!

### How do I interpret the HR Range (blue area)?

The blue area in the Heart Rate Chart shows the range between:
- **Lower boundary**: Lowest average HR of a run (e.g., Recovery Run at 135 bpm)
- **Upper boundary**: Highest max HR across all runs (e.g., Tempo Run peak at 175 bpm)

**Interpretation:**
- **Wide area**: Different training intensities → good for balanced training!
- **Narrow area**: All runs similar intensity → possibly too monotonous
- **Area rises**: Training is becoming more intense
- **Area falls**: More Easy Runs / recovery

### Why is my Efficiency Factor decreasing?

A falling EF over several weeks can have various causes:

1. **Overtraining**: Too much load, too little recovery
2. **Illness**: Beginning cold or infection
3. **Heat/Weather**: High temperatures increase HR at same pace
4. **Fatigue**: Accumulated tiredness from intense training
5. **Stress**: Professional/personal stress influences HR

**What to do:**
- **Short-term fluctuation** (1-2 weeks): Probably normal (weather, stress)
- **Constantly falling** (3+ weeks): Take a recovery week!
- Compare with Training Score and feeling during runs
- Include more Easy Runs

**Tip:** Use EF as early warning system for overtraining!

### Can I add HR data to runs without HR monitor retrospectively?

No, heart rate data must be recorded during the run with an HR monitor. Retrospective addition is technically not possible.

**Recommendation:**
- Invest in a heart rate monitor (chest strap or optical sensor)
- Many modern sports watches have built-in optical HR sensors
- Chest straps are usually more accurate than optical sensors
- Strava automatically imports HR data from compatible devices

### Is a rising Efficiency Factor always good?

**Mostly yes**, but with nuances:

**Good (real fitness improvement):**
- EF rises with constant or increasing volume
- You feel good during training
- Training Score is stable or rising

**Caution (possible problems):**
- EF rises, but only because you're running slower (lower HR at slow pace)
- Always compare with Pace/Speed Chart!
- EF rises suddenly strongly → could be measurement inaccuracy

**Tip:** Always look at the combination of EF AND Pace. Ideal progress:
- Pace gets faster ✓
- HR stays same or falls ✓
- → EF rises = real fitness improvement! ✓

### Does the Efficiency Factor flow into the Training Score?

**Yes!** Since the latest version, the Training Score considers the Efficiency Factor.

**With HR data:**
- 30% Distance
- 30% Pace
- 20% Efficiency Factor
- 20% Frequency

**Without HR data:**
Weights automatically adapt:
- 37.5% Distance
- 37.5% Pace
- 25% Frequency

**Why this weighting?**
- **Distance & Pace equally important** (30% each): Volume and quality are equal
- **Efficiency Factor** (20%): Aerobic fitness as important indicator
- **Frequency** (20%): Consistency is important, but less than performance

**Benefits:**
- Score now reflects real fitness improvement (not just volume)
- EF improvement leads to higher score
- Warning for overtraining: Falling EF = lower score
- Works with mixed data (some runs with HR, some without)

### Why has my Training Score decreased even though I'm running more?

This can have several reasons:

**1. Pace has worsened**
- More volume but slower tempo
- Pace has 30% weighting in score

**2. Efficiency Factor has fallen** (when HR data available)
- Higher HR at same or slower pace
- Possible overtraining
- EF has 20% weighting

**3. Recovery week**
- Deliberately less distance/intensity
- Lower score is INTENDED and good here!

**4. Rolling baseline has adapted**
- Score compares with your rolling average
- If your average rises, current training must be even higher for same score

**Example:**
- **2 months ago**: 20 km/week = Score 60
- **Now**: 25 km/week = Score 55

→ Your baseline is now ~23 km/week (due to constant increase)
→ 25 km is only slightly above new baseline
→ At same time, pace has become slower (-10%)
→ **Result**: Score falls despite higher volume

### What does "Marathon Milestone: Keep training!" in Summary Panel mean?

This means the current projection does NOT show that you'll reach 32 km Long Run (Marathon-Ready) in the foreseeable future.

**Possible reasons:**

**1. Too little data**
- Fewer than 3-4 periods with Long Runs
- Projection cannot be calculated yet

**2. Negative trend**
- Your Longest Runs are getting shorter
- Example: 18 km → 15 km → 12 km
- Projection shows downward

**3. Very flat or stagnating trend**
- Longest Run remains constant (e.g., always ~10 km)
- No growth visible

**4. Long timespan until goal**
- Projection would take >2 years
- App shows "Keep training!" instead of unrealistic date

**What to do?**

**For marathon preparation:**
1. Increase your Long Run gradually (e.g., +10% per week)
2. Look at **Projection Tab** → **Long Run Mode**
3. Set intermediate goals: 15K, Half Marathon (21.1 km), 30K
4. Use **Endurance Tab** → **Longest Run Chart** to track progression

**Example:**
```
Currently: Longest Run ~12 km
Goal: 32 km Long Run (Marathon Ready)

Realistic progression:
- Week 1-4: 12 km → 15 km (+0.75 km/week)
- Week 5-8: 15 km → 18 km
- Week 9-12: 18 km → 21 km (Half Marathon!)
- Week 13-20: 21 km → 28 km
- Week 21-24: 28 km → 32 km (Marathon Ready!)

After ~12 weeks with constant trend, the milestone will show a date!
```

**Important:** This is NORMAL! Marathon preparation takes months. Focus on consistent Long Run increases.

**What to do?**
- Check Pace Chart: Has your tempo become slower?
- Check EF Chart (if HR data): Has your aerobic efficiency decreased?
- Analyze if you've built up too much volume too quickly (overtraining)
- Plan a recovery week if needed

### How accurate are the Race Time Predictions?

The predictions are **estimates** based on scientifically sound methodology (McMillan Calculator), but individual results vary.

**Typical Accuracy:**

- **Well-trained athletes**: ±2-5% deviation
- **Beginners/little race experience**: ±5-10% deviation
- **Extreme conditions** (heat, hills): Higher deviation

**Example:**
- Prediction: Marathon 3:50:00
- Possible Range: 3:40-4:05 (±7%)

**Factors for better accuracy:**

✅ **Helps:**
- Many Easy Runs (10+) in last 6 months
- Consistent HR data
- Similar training conditions to race
- Experience in pace management

❌ **Reduces accuracy:**
- Few Easy Runs (<5)
- Fluctuating fitness
- First race at the distance
- Very hilly/hot conditions

**Comparison with other methods:**

| Method | Accuracy | Requirement |
|---------|-------------|---------------|
| **McMillan (HR-based)** | Good | HR data, Easy Runs |
| Riegel's Formula | Very good | Real race time as reference |
| VDOT (Jack Daniels) | Very good | VO2max test or race time |
| Just training pace | Poor | Mixes intensities |

**Why deviations are normal:**

1. **Race Psychology**: Races often run faster than training
2. **Taper Effect**: Rested legs are 2-3% faster
3. **Adrenaline**: Can give 1-2% performance boost
4. **Course & Weather**: -10% in heat, +5% with hills possible

**Recommendation:**

Use predictions as **starting point** for race pace planning:
- **Conservative**: Start 5% slower than prediction
- **Experienced**: Start at prediction pace
- **Aggressive**: Start 2-3% faster (risk!)

**Practical Tip:**

After your first race: Compare Prediction vs. Actual Time!
- Faster than expected → Your Easy Pace is very conservative
- Slower than expected → Check tapering, race strategy

The app doesn't learn automatically, but you can use the insights for future races.

### Why does the Summary Panel show an orange HRmax warning?

The app performs a **plausibility check** of your automatically detected HRmax. A warning appears when:

**1. Detected HRmax too low (<150 bpm)**
- For runners, an HRmax under 150 bpm is extremely unusual
- Even 60-year-olds typically have HRmax ~160-170 bpm

**2. Average HR consistently too high (>85% of detected HRmax)**
- When >50% of your runs are above 85% of detected HRmax
- Indicates your true HRmax is higher

**Example:**
```
Detected HRmax: 169 bpm
Your typical Easy Runs: 135-148 bpm (80-88% of 169)
→ That's too high for "Easy Runs"!

Suggestion: Set HRmax ~190 bpm
→ Easy Runs would then be 114-143 bpm (60-75% of 190) ✅
```

**What to do?**

1. **Check the warning**: Summary Panel shows a suggested value
2. **Go to Settings**: Open Settings dialog
3. **Set manual HRmax**: Enter suggested value (or your known value)
4. **Save**: Click Save

**How do I know my true HRmax?**

- **HRmax test at sports doctor** (most accurate method)
- **Self-test**: All-out 5min hill run (max HR in last minute)
- **Formula (inaccurate)**: 220 - Age (only rough estimate, ±10-15 bpm variance!)
- **Strava data**: Highest ever measured value during a very hard interval/race

**Important:**
- Most runners NEVER reach their true HRmax in normal training
- That's why auto-detection applies a 10% safety margin
- Manual entry bypasses this margin (uses exact value)

### What is ACWR and why is it important?

**ACWR** = **Acute:Chronic Workload Ratio** - a scientifically-validated metric that compares your recent training load (acute) to your baseline training load (chronic) to detect overtraining risk.

**Why it's important:**
- **Prevents injuries**: ACWR > 1.5 = 2-4x higher injury risk
- **Optimizes training**: Keep ACWR in 0.8-1.3 range (safe zone)
- **Detects spikes early**: Warns you BEFORE injury occurs
- **Scientifically validated**: Based on peer-reviewed research (Gabbett et al. 2016)

**How it works:**
```
ACWR = Acute Load (last week) / Chronic Avg Load (previous 4 weeks)

Example:
Last week: 30 km
Previous 4 weeks: 22, 24, 23, 25 km (avg: 23.5 km)
ACWR = 30 / 23.5 = 1.28 (SAFE zone)
```

**RunTrend's enhancement:**
Instead of distance only, RunTrend calculates a **composite ACWR** using:
- Distance (40%)
- Pace (30%)
- Heart Rate (30%)

This gives you a complete picture of training stress.

**Where to find it:**
- **Summary Panel**: Shows current Training Load score (0-100) and status
- **Training Load Tab**: Chart with colored safe zones
- **Metrics Explanations**: Full explanation of calculation and interpretation

**See also:** Metrics Explanations → Training Load (ACWR) for detailed explanation.

### Why is my Training Load score high even though I'm running the same distance?

Training Load (ACWR) considers **more than just distance**. A high score can occur even with stable distance due to:

**1. Pace intensity increased**
```
Last 4 weeks: 30 km/week at 6:00 min/km
This week: 30 km/week at 5:30 min/km
→ Same distance, but MUCH higher intensity
→ Pace ACWR = 1.55 (spike!)
→ Training Load Score: 78 (CAUTION)
```

**2. Heart rate increased** (fatigue/heat/illness)
```
Last 4 weeks: Avg HR 150 bpm
This week: Avg HR 165 bpm (same pace!)
→ Heart working harder = higher physiological stress
→ HR ACWR = 1.10
→ Combined with other factors → higher Training Load
```

**3. Combination of multiple factors**
```
Small distance increase (+10%) +
Slightly faster pace (+5%) +
Slightly elevated HR (+3%)
= Composite ACWR 1.42 → Score 72 (CAUTION)

Each factor alone is small, but combined = spike!
```

**4. Race effort**
```
Week 1-4: 35 km easy pace
Week 5: 35 km including 10K race effort
→ Distance same, but race = HIGH intensity + HR spike
→ Training Load Score: 85 (WARNING)
```

**What to do:**
- Check **Training Load Chart** to see which component spiked
- Look at **Pace Chart**: Did pace improve too fast?
- Look at **HR Chart**: Is average HR rising?
- Use **RoC overlays** to see if trends are too steep
- If score high: Hold current load, prioritize recovery

**Remember:** Training Load protects you by detecting ALL forms of training stress, not just volume.

### What should I do if my Training Load is in the WARNING zone?

A **WARNING zone** score (80-90) indicates HIGH injury risk - immediate action needed!

**Step 1: Don't Panic**
- One WARNING score ≠ guaranteed injury
- It's an early warning system
- You caught it in time - that's the point!

**Step 2: Immediate Action (Next 3-5 Days)**
```
✓ Reduce next week's volume by 20-30%
✓ Easy runs ONLY (no speed work, no tempo runs)
✓ If any pain/unusual soreness appears: Take rest day immediately
✗ Don't continue planned progression
✗ Don't race or do hard workouts
```

**Example:**
```
Current week: 50 km → Score 85 (WARNING)
Next week plan: 55 km → STOP! Too risky

Better:
Next week: 35-40 km easy pace
Week after: 40-45 km (if score drops to GREEN)
Then: Resume gradual progression
```

**Step 3: Recovery Week Strategy**
```
Focus on:
✓ Sleep: 8+ hours per night
✓ Nutrition: Adequate protein, hydration
✓ Rest days: Include 1-2 extra rest days
✓ Easy pace: All runs conversational (can talk normally)
✓ Stress reduction: Minimize life stress if possible
```

**Step 4: Monitor Progress**
```
After recovery week:
- Check Training Load in Summary Panel
- Score dropped to 50-65 (GREEN)? → Resume training
- Score still 70+? → Another easy week needed
```

**Step 5: Prevent Future Spikes**
```
Going forward:
✓ Plan recovery weeks every 3-4 weeks (20-30% volume reduction)
✓ After races: ALWAYS include recovery week
✓ Use RoC overlays to see if progression is too steep
✓ Listen to body: Fatigue + high Training Load = extra rest
```

**When to see a doctor:**
```
🚨 Persistent pain that doesn't improve with rest
🚨 Elevated resting HR (+10 bpm) for multiple days
🚨 Extreme fatigue despite adequate rest
🚨 Frequent illness/getting sick repeatedly
🚨 Loss of motivation lasting >2 weeks
→ These are overtraining syndrome symptoms - seek medical advice
```

**Success story example:**
```
Week 1-4: Score 52-58 (GREEN)
Week 5: Score 82 (WARNING) - noticed early!
Week 6: Reduced to 30 km easy → Score 54 (GREEN)
Week 7: 38 km → Score 58 (GREEN)
Week 8: 42 km → Score 62 (GREEN) - back on track!

Result: Avoided injury by responding to warning
```

**See also:** Training Load Tab → How to Interpret the Chart for detailed guidance.

### Why is ACWR not shown for the current week?

ACWR is only calculated for **complete periods** to ensure accuracy. You won't see a Training Load score for the current week/month until it's finished.

**Why complete periods only?**
```
Example (viewing on Wednesday):
Mon-Tue: 15 km run so far
Remaining Wed-Sun: Unknown

If we calculated ACWR now:
→ Acute Load = 15 km (incomplete!)
→ ACWR would show 15/23 = 0.65 (Undertraining)
→ Misleading! You might run 30 km total by Sunday

Solution: Wait until Sunday to calculate actual weekly ACWR
```

**What you see instead:**
```
In Summary Panel:
Training Load: 52 (SAFE) ← Last completed week
Status: "SAFE - Gradual progressive overload"

In Training Load Chart:
Graph shows up to last Sunday (complete week)
Current week (Mon-today) is NOT shown yet
```

**How to use this:**
Use **last week's score** to guide **this week's** training:

```
Last week: Score 75 (CAUTION)
This week: Keep volume conservative, don't increase
Next week: Check if score dropped before resuming progression

Last week: Score 52 (SAFE)
This week: Can continue planned progression
```

**When will I see current week's ACWR?**
```
Weekly aggregation:
- Monday 00:00: Last week becomes "complete"
- Summary Panel updates with last week's score
- Chart adds last week's data point

Monthly aggregation:
- 1st of month 00:00: Last month becomes "complete"
- Scores update with last month's data
```

**Workaround for mid-week awareness:**
Use **RoC overlays** on Distance/Pace/HR charts:
- Shows if current trend is too steep
- Forward-looking indicator (unlike ACWR which is lagging)
- Example: Distance RoC +4 km/week = aggressive (likely to trigger high ACWR)

**Best practice:**
```
✓ Review Training Load every Monday morning (weekly)
✓ Review Training Load every 1st of month (monthly)
✓ Use last week's score to plan THIS week
✓ Use RoC trends to catch steep progressions early
✗ Don't expect real-time ACWR during the week
```

**See also:** Metrics Explanations → Training Load (ACWR) → Requirements

### What is Rate of Change (RoC) and how do I use it?

**Rate of Change (RoC)** is a trend indicator that shows how fast a metric is changing over time using rolling 8-period linear regression.

**Where to find it:**
- Distance Chart: "Show Rate of Change" checkbox
- Pace Chart: "Show Rate of Change" checkbox
- Heart Rate Chart: "Show Rate of Change" checkbox

**What it shows:**
```
Distance RoC: How fast your weekly/monthly distance is changing
- Example: +2 km/week = adding 2 km per week on average

Pace RoC: How fast your pace is improving/worsening
- Example: -0.05 min/km per week = getting 3 sec/km faster each week

HR RoC: How fast your average heart rate is changing
- Example: +2 bpm/week = HR rising by 2 beats per week
```

**How to read it:**
```
Purple dashed line on chart:
- Line above zero: Metric is increasing
- Line below zero: Metric is decreasing
- Flat line near zero: Metric is stable
- Steep slope: Fast change
- Gentle slope: Gradual change
```

**Practical examples:**

**Example 1: Sustainable Volume Build**
```
Distance Chart with RoC enabled:
Weeks 1-8: Distance rising from 20→34 km
RoC line: +1.5 km/week (gradual positive slope)
Training Load: 55 (SAFE)
→ Interpretation: Sustainable progression ✓
```

**Example 2: Too Aggressive Progression**
```
Distance Chart with RoC enabled:
Weeks 1-4: Distance jumps from 25→45 km
RoC line: +4 km/week (steep positive slope)
Training Load: 82 (WARNING)
→ Interpretation: Too aggressive! ⚠
→ Action: Flatten progression to +1-2 km/week
```

**Example 3: Pace Improvement**
```
Pace Chart with RoC enabled:
Months 1-6: Pace improving from 6:00→5:30/km
RoC line: -0.08 min/km per month (negative = getting faster)
Training Load: 58 (SAFE)
→ Interpretation: Nice steady improvement ✓
```

**Example 4: HR Fatigue Warning**
```
HR Chart with RoC enabled:
Weeks 1-8: Avg HR rising from 150→158 bpm (same pace!)
RoC line: +1 bpm/week (positive slope)
Training Load: 72 (CAUTION)
→ Interpretation: Fatigue accumulating ⚠
→ Action: Recovery week needed
```

**Use with Training Load:**
```
RoC is FORWARD-LOOKING:
- Shows trends BEFORE they trigger Training Load warnings
- Steep Distance RoC → Will likely cause high Training Load soon
- Use RoC to adjust progression before ACWR spikes

Training Load is BACKWARD-LOOKING:
- Shows spike AFTER it happened
- Tells you to reduce load in response

Best practice: Use BOTH
1. Monitor RoC trends weekly
2. If RoC too steep → flatten progression proactively
3. If Training Load spikes anyway → recovery week
```

**When RoC is most useful:**
```
✓ Planning volume progressions (is +3 km/week too much?)
✓ Tracking pace improvement trends (am I plateauing?)
✓ Detecting gradual HR fatigue (subtle warning sign)
✓ Validating recovery weeks (RoC should flatten/reverse)
✓ Understanding why Training Load spiked (steep RoC = cause)
```

**Limitations:**
```
- Requires 8+ complete periods for calculation
- First 7 periods show no RoC (not enough data)
- Sensitive to outliers (one race can skew the trend)
- Shows rate, not absolute values (use with main metric)
```

**Tip:** Enable RoC when you want to understand the "story" behind your training trends - are you building too fast, plateauing, or progressing ideally?

**See also:**
- Distance Chart → Rate of Change Overlay
- Pace Chart → Rate of Change Overlay
- Heart Rate Chart → Rate of Change Overlay

### Can I use RunTrend without a heart rate monitor?

**Yes!** RunTrend works great without heart rate data - many features don't require HR.

**Features that work WITHOUT HR:**

**✓ Summary Panel:**
- Total Distance, Pace, Frequency, Longest Run
- Training Score (adapted weighting without EF component)
- Training Load (ACWR) - uses Distance + Pace only (HR defaults to 1.0)
- Marathon Milestone
- Race Time Predictions (based on pace only)

**✓ Charts - Overview Tab:**
- Distance Chart (with RoC overlay)
- Pace/Speed Chart (with RoC overlay)
- Frequency Chart

**✓ Charts - Endurance Tab:**
- Longest Run Chart
- Average Distance per Run Chart

**✓ Charts - Score Tab:**
- Training Score (adapted formula)

**✓ Charts - Training Load Tab:**
- Training Load Chart (Distance + Pace components only)
- Colored safe zones still work

**✓ Charts - Projection Tab:**
- Volume Projection
- Long Run Projection
- Milestone predictions

**Features that REQUIRE HR data:**

**✗ Heart Rate Tab:**
- Shows "No HR data available" message
- HR Range, Average HR, Efficiency Factor not available

**✗ Efficiency Factor:**
- Not calculated without HR
- Training Score uses adapted weighting (no EF component)

**✗ HR-specific Training Load component:**
- ACWR HR component defaults to 1.0 (neutral)
- Training Load still works, but slightly less accurate

**Adapted metrics without HR:**

**Training Score weighting:**
```
With HR:
- 30% Distance
- 30% Pace
- 20% Efficiency Factor
- 20% Frequency

Without HR (automatic adaptation):
- 37.5% Distance
- 37.5% Pace
- 0% Efficiency Factor (not calculated)
- 25% Frequency
→ Total still 100%, weights adjusted proportionally
```

**Training Load (ACWR) without HR:**
```
Composite ACWR = (Distance ACWR × 50%) +
                 (Pace ACWR × 50%) +
                 (1.0 × 0%)  ← HR defaults to neutral

Still detects:
✓ Volume spikes (Distance ACWR)
✓ Intensity spikes (Pace ACWR)
✗ Physiological stress (HR ACWR missing)

Still useful! Catches most overtraining risks.
```

**Benefits of adding HR monitor:**
```
With HR monitor you gain:
✓ Efficiency Factor (best aerobic fitness indicator)
✓ HR Range visualization (training intensity distribution)
✓ More accurate Training Load (includes physiological stress)
✓ Early fatigue detection (rising HR at same pace)
✓ Better Training Score (includes fitness component)

Recommended devices:
- Chest strap: Most accurate (Garmin HRM-Dual, Polar H10)
- Optical wrist: Convenient but less accurate (built into most sports watches)
- Strava automatically imports HR from compatible devices
```

**Recommendation:**
```
Beginner (0-6 months running):
→ Start without HR monitor, focus on consistency
→ RunTrend provides plenty of insights from distance/pace alone

Intermediate (6-12 months):
→ Consider adding HR monitor
→ Efficiency Factor becomes very valuable
→ Better overtraining detection

Advanced/Marathon training:
→ HR monitor highly recommended
→ Training Load with HR = much more accurate
→ Catch fatigue earlier
```

**Bottom line:** RunTrend is fully functional without HR, but HR data adds significant value for serious training optimization.

---

## About This Software

**Running Progress Tracker** (Run Trend)
Version 0.1.0

**Developer:** Arne Weiß
**Contact:** run-trend@arne-weiss.de

### License

This software is licensed under **MIT License with Commons Clause**.

**What does this mean?**

✅ **Allowed:**
- Private use
- Non-commercial use
- View, modify, and share code
- Contributions and further development

❌ **Not allowed:**
- Commercial distribution of the software
- Selling derivative works based on this software

You can find the full license in the LICENSE file in the project repository.

### Privacy

- All data is stored locally on your computer
- No external transmission except to Strava API (after your authorization)
- No telemetry or analytics
- You can revoke the connection to Strava at any time

### Open Source

The source code is publicly available. Information about the repository can be found in the About dialog (Toolbar → About).

---

## Further Help

If you have questions or problems:
- Check Strava API credentials in Settings
- Make sure Strava connection is active
- Try synchronizing again
- Contact: run-trend@arne-weiss.de

Good luck with your training! 🏃‍♂️
