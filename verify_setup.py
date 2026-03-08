#!/usr/bin/env python3
"""
Verify that the Running Progress Tracker setup is complete.
"""
import os
import sys
from pathlib import Path


def check_directory(path, name):
    """Check if directory exists."""
    if Path(path).is_dir():
        print(f"✓ {name} directory exists")
        return True
    else:
        print(f"✗ {name} directory missing")
        return False


def check_file(path, name):
    """Check if file exists."""
    if Path(path).is_file():
        print(f"✓ {name} exists")
        return True
    else:
        print(f"✗ {name} missing")
        return False


def main():
    """Run setup verification."""
    print("Running Progress Tracker - Setup Verification")
    print("=" * 60)

    checks_passed = 0
    total_checks = 0

    # Check main directories
    directories = [
        ("app", "Main application"),
        ("app/ui", "UI modules"),
        ("app/charts", "Chart widgets"),
        ("app/strava", "Strava integration"),
        ("app/storage", "Database storage"),
        ("app/sync", "Sync manager"),
        ("app/analytics", "Analytics"),
        ("app/projection", "Projection"),
        ("app/settings", "Settings"),
        ("tests", "Tests"),
    ]

    print("\nChecking directories:")
    for path, name in directories:
        total_checks += 1
        if check_directory(path, name):
            checks_passed += 1

    # Check key files
    files = [
        ("app/main.py", "Main entry point"),
        ("app/ui/main_window.py", "Main window"),
        ("app/ui/summary_panel.py", "Summary panel"),
        ("app/charts/distance_chart.py", "Distance chart"),
        ("app/charts/pace_chart.py", "Pace chart"),
        ("app/charts/frequency_chart.py", "Frequency chart"),
        ("app/charts/score_chart.py", "Score chart"),
        ("app/charts/projection_chart.py", "Projection chart"),
        ("app/strava/auth.py", "Strava auth"),
        ("app/strava/client.py", "Strava client"),
        ("app/storage/database.py", "Database layer"),
        ("app/sync/sync_manager.py", "Sync manager"),
        ("app/analytics/aggregator.py", "Activity aggregator"),
        ("app/analytics/smoothing.py", "Smoothing algorithms"),
        ("app/analytics/training_score.py", "Training score"),
        ("app/projection/forecaster.py", "Forecaster"),
        ("app/settings/config.py", "Settings config"),
        ("flake.nix", "Nix flake"),
        ("README.md", "README"),
        ("specification.md", "Specification"),
        ("tests/test_analytics.py", "Analytics tests"),
        ("tests/test_projection.py", "Projection tests"),
    ]

    print("\nChecking key files:")
    for path, name in files:
        total_checks += 1
        if check_file(path, name):
            checks_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Verification complete: {checks_passed}/{total_checks} checks passed")

    if checks_passed == total_checks:
        print("\n✓ All checks passed! The application is ready to run.")
        print("\nNext steps:")
        print("1. Set up Strava API credentials in 'strava_token' file")
        print("2. Enter Nix development shell: nix develop")
        print("3. Run the application: python app/main.py")
        print("4. Run tests: pytest tests/")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
