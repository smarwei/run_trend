#!/usr/bin/env python3
"""
Show actual HR values of recent runs.
"""
from app.storage.database import Database
from datetime import datetime, timedelta, timezone

# Initialize database
db = Database()
activities = db.get_all_activities()

# Get max HR
max_hr_values = [a.get('max_heartrate') or 0 for a in activities]
max_hr_values = [hr for hr in max_hr_values if hr > 0]
lifetime_max_hr = max(max_hr_values) if max_hr_values else 0

print(f"Detected HRmax: {lifetime_max_hr} bpm")
print(f"Easy Zone (60-75%): {lifetime_max_hr * 0.6:.0f}-{lifetime_max_hr * 0.75:.0f} bpm")
print(f"Zone 3 (75-85%): {lifetime_max_hr * 0.75:.0f}-{lifetime_max_hr * 0.85:.0f} bpm")
print()

# Get recent runs with HR
cutoff_date = datetime.now(timezone.utc) - timedelta(days=180)  # 6 months

recent_runs = []
for activity in activities:
    avg_hr = activity.get('average_heartrate')
    distance_m = activity.get('distance', 0)
    start_date_str = activity.get('start_date')

    if not avg_hr or avg_hr <= 0:
        continue

    if distance_m < 3000:  # Skip very short runs
        continue

    if start_date_str:
        try:
            run_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            if run_date < cutoff_date:
                continue

            recent_runs.append({
                'date': run_date,
                'distance': distance_m / 1000,
                'avg_hr': avg_hr,
                'hr_pct': (avg_hr / lifetime_max_hr) * 100
            })
        except (ValueError, AttributeError):
            continue

# Sort by date
recent_runs.sort(key=lambda x: x['date'], reverse=True)

print(f"Last {min(20, len(recent_runs))} runs (>3km, last 6 months):")
print()

for i, run in enumerate(recent_runs[:20], 1):
    hr_pct = run['hr_pct']
    zone_indicator = ""
    if hr_pct < 60:
        zone_indicator = "⬇️ Zone 1 (Recovery)"
    elif hr_pct <= 75:
        zone_indicator = "✅ Zone 2 (Easy)"
    elif hr_pct <= 85:
        zone_indicator = "⚠️ Zone 3 (Moderate)"
    else:
        zone_indicator = "❌ Zone 4+ (Hard)"

    print(f"{i:2}. {run['date'].strftime('%Y-%m-%d')} | "
          f"{run['distance']:5.1f}km | "
          f"HR {run['avg_hr']:3.0f} ({hr_pct:4.1f}%) | "
          f"{zone_indicator}")

print()
print("Analysis:")
hr_values = [r['avg_hr'] for r in recent_runs]
if hr_values:
    avg_hr = sum(hr_values) / len(hr_values)
    print(f"Average HR: {avg_hr:.0f} bpm ({(avg_hr/lifetime_max_hr)*100:.1f}% of detected HRmax)")
    print()

    # Count by zone
    zone1 = sum(1 for r in recent_runs if r['hr_pct'] < 60)
    zone2 = sum(1 for r in recent_runs if 60 <= r['hr_pct'] <= 75)
    zone3 = sum(1 for r in recent_runs if 75 < r['hr_pct'] <= 85)
    zone4 = sum(1 for r in recent_runs if r['hr_pct'] > 85)

    print("Distribution:")
    print(f"  Zone 1 (<60%):    {zone1}")
    print(f"  Zone 2 (60-75%):  {zone2} ✅ Easy Runs")
    print(f"  Zone 3 (75-85%):  {zone3}")
    print(f"  Zone 4+ (>85%):   {zone4}")
    print()

    if zone2 == 0 and zone3 > 0:
        print("💡 Suggestion:")
        print("   All your runs are in Zone 3 (75-85% HRmax).")
        print("   This suggests one of two things:")
        print()
        print("   1. Your actual HRmax might be HIGHER than 169 bpm")
        print("      → If HRmax was 190, these runs would be Zone 2!")
        print()
        print("   2. You're training in Zone 3, not Zone 2")
        print("      → Consider slowing down slightly")
        print()
        print("   Option: Expand Easy Zone to 60-80% to include Zone 3?")
