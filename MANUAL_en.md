# Running Progress Tracker - User Manual

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [User Interface](#user-interface)
4. [Metrics Explanations](#metrics-explanations)
5. [Charts and Visualizations](#charts-and-visualizations)
6. [Settings](#settings)
7. [About This Software](#about-this-software)

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

### Charts (right)

The charts are organized into 5 main categories:

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

#### 5. Projection Tab
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

#### Pace/Speed Chart
**Shows:** Pace (min/km) or Speed (km/h) per period

**Toggle:** Toolbar → Metric: "Pace" or "Speed"

**Interpretation:**
- **Pace decreases** = speed is improving
- **Speed increases** = speed is improving

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
- **Right Y-Axis**: Efficiency Factor ×1000 (for EF Line)

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
- **Disconnect from Strava**: Disconnect
- **Sync Activities**: Download activities from Strava
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
