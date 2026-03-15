#!/usr/bin/env python3
"""
Debug script to check why race predictions are not showing.
"""
from app.storage.database import Database
from app.analytics.race_predictor import RacePredictor

# Initialize database
db = Database()

# Get all activities
activities = db.get_all_activities()

print(f"Total activities: {len(activities)}")
print()

if activities:
    print("Sample activity (first one):")
    sample = activities[0]
    print(f"Keys: {sample.keys()}")
    print(f"Start date: {sample.get('start_date')}")
    print(f"Distance: {sample.get('distance')} (meters?)")
    print(f"Moving time: {sample.get('moving_time')} (seconds?)")
    print(f"Average HR: {sample.get('average_heartrate')}")
    print(f"Has HR: {sample.get('has_heartrate')}")
    print()

# Find max HR (handle None values)
max_hr_values = [a.get('max_heartrate') or 0 for a in activities]
max_hr_values = [hr for hr in max_hr_values if hr > 0]
lifetime_max_hr = max(max_hr_values) if max_hr_values else 0
print(f"Lifetime max HR: {lifetime_max_hr}")
print()

# Count activities with HR
hr_count = sum(1 for a in activities if (a.get('average_heartrate') or 0) > 0)
print(f"Activities with HR data: {hr_count}/{len(activities)}")
print()

# Check format - convert one activity
if activities:
    raw = activities[0]
    print("Conversion needed:")
    print(f"  distance: {raw.get('distance')} m -> {raw.get('distance', 0) / 1000:.2f} km")

    distance_m = raw.get('distance', 0)
    moving_time_s = raw.get('moving_time', 0)
    if distance_m > 0 and moving_time_s > 0:
        pace_s_per_m = moving_time_s / distance_m
        pace_min_per_km = pace_s_per_m * 1000 / 60
        print(f"  pace: {moving_time_s}s / {distance_m}m -> {pace_min_per_km:.2f} min/km")
    print()

# Try to estimate race times with raw data (will probably fail)
print("Attempting race prediction with RAW data (expected to fail):")
result = RacePredictor.estimate_race_times(
    activities,
    lifetime_max_hr,
    efficiency_factor=0.018
)
print(f"Has prediction: {result.get('has_prediction') if result else 'None'}")
if result and not result.get('has_prediction'):
    print(f"Reason: {result.get('reason')}")
    print(f"Message: {result.get('message')}")
print()

# Convert activities to expected format
print("Converting activities to expected format...")
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
            'average_heartrate': activity.get('average_heartrate', 0),
            'start_date': activity.get('start_date')
        })

print(f"Converted {len(converted_activities)} activities")
print()

# Try again with converted data
print("Attempting race prediction with CONVERTED data:")
result = RacePredictor.estimate_race_times(
    converted_activities,
    lifetime_max_hr,
    efficiency_factor=0.018
)
print(f"Has prediction: {result.get('has_prediction') if result else 'None'}")
if result:
    if result.get('has_prediction'):
        print(f"Easy runs found: {result.get('easy_runs_count')}")
        print(f"Median easy pace: {result.get('median_easy_pace_formatted')}")
        print()
        print("Predictions:")
        for race, pred in result['predictions'].items():
            print(f"  {race}: {pred['total_time_formatted']} @ {pred['pace_min_per_km']:.2f} min/km")
    else:
        print(f"Reason: {result.get('reason')}")
        print(f"Message: {result.get('message')}")
