#!/usr/bin/env python3
"""
Analyze HR zones to understand why no easy runs are found.
"""
from app.storage.database import Database
from datetime import datetime, timedelta, timezone

# Initialize database
db = Database()
activities = db.get_all_activities()

# Convert activities
converted_activities = []
for activity in activities:
    distance_m = activity.get('distance', 0)
    moving_time_s = activity.get('moving_time', 0)

    if distance_m > 0 and moving_time_s > 0:
        distance_km = distance_m / 1000
        pace_s_per_m = moving_time_s / distance_m
        pace_min_per_km = pace_s_per_m * 1000 / 60

        converted_activities.append({
            'distance_km': distance_km,
            'pace_min_per_km': pace_min_per_km,
            'average_heartrate': activity.get('average_heartrate'),
            'start_date': activity.get('start_date')
        })

# Get max HR
max_hr_values = [a.get('max_heartrate') or 0 for a in activities]
max_hr_values = [hr for hr in max_hr_values if hr > 0]
lifetime_max_hr = max(max_hr_values) if max_hr_values else 0

print(f"Lifetime Max HR: {lifetime_max_hr}")
print(f"Total converted activities: {len(converted_activities)}")
print()

# Analyze why runs are excluded
cutoff_date = datetime.now(timezone.utc) - timedelta(days=6 * 30)
print(f"Cutoff date: {cutoff_date.date()}")
print()

# Stats
total_hr = 0
too_old = 0
too_short = 0
hr_too_low = 0
hr_too_high = 0
no_hr = 0
valid_easy_runs = 0

for run in converted_activities:
    avg_hr = run.get('average_heartrate')
    distance = run.get('distance_km', 0)
    start_date_str = run.get('start_date')

    # Count runs with HR
    if avg_hr and avg_hr > 0:
        total_hr += 1

        # Check date
        if start_date_str:
            try:
                run_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                if run_date < cutoff_date:
                    too_old += 1
                    continue
            except (ValueError, AttributeError):
                continue

        # Check distance
        if distance < 5.0:
            too_short += 1
            continue

        # Check HR zone
        hr_percentage = (avg_hr / lifetime_max_hr) * 100
        if hr_percentage < 60:
            hr_too_low += 1
            continue
        elif hr_percentage > 75:
            hr_too_high += 1
            continue

        # Valid easy run!
        valid_easy_runs += 1
        if valid_easy_runs <= 5:  # Show first 5
            print(f"Easy Run found: {distance:.1f}km @ {run['pace_min_per_km']:.2f} min/km, HR {avg_hr:.0f} ({hr_percentage:.1f}%)")
    else:
        no_hr += 1

print()
print("Summary:")
print(f"  Total with HR data: {total_hr}")
print(f"  Too old (>6 months): {too_old}")
print(f"  Too short (<5km): {too_short}")
print(f"  HR too low (<60%): {hr_too_low}")
print(f"  HR too high (>75%): {hr_too_high}")
print(f"  No HR data: {no_hr}")
print(f"  ✅ Valid Easy Runs: {valid_easy_runs}")
