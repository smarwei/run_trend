"""
Strava API client for fetching activity data.
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import time


class StravaClient:
    """Client for Strava API v3."""

    BASE_URL = "https://www.strava.com/api/v3"

    def __init__(self, auth):
        """
        Initialize Strava client.

        Args:
            auth: StravaAuth instance
        """
        self.auth = auth

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Make authenticated request to Strava API.

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters

        Returns:
            JSON response or None on error
        """
        access_token = self.auth.get_access_token()
        if not access_token:
            print("No valid access token available")
            return None

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                headers=headers,
                params=params or {}
            )

            # Handle rate limiting
            if response.status_code == 429:
                print("Rate limited by Strava API. Please wait...")
                return None

            # Handle unauthorized
            if response.status_code == 401:
                print("Unauthorized. Token may be invalid.")
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def get_athlete(self) -> Optional[Dict[str, Any]]:
        """
        Get authenticated athlete information.

        Returns:
            Athlete data or None
        """
        return self._make_request("athlete")

    def get_activities(
        self,
        after: Optional[int] = None,
        before: Optional[int] = None,
        page: int = 1,
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get athlete activities.

        Args:
            after: Unix timestamp - return activities after this time
            before: Unix timestamp - return activities before this time
            page: Page number
            per_page: Number of activities per page (max 200)

        Returns:
            List of activity summaries
        """
        params = {
            'page': page,
            'per_page': min(per_page, 200)
        }

        if after:
            params['after'] = after
        if before:
            params['before'] = before

        result = self._make_request("athlete/activities", params)
        return result if isinstance(result, list) else []

    def get_all_activities_since(self, start_date: datetime, activity_type: str = 'Run') -> List[Dict[str, Any]]:
        """
        Get all activities since a specific date.

        Args:
            start_date: Start date for activity fetch
            activity_type: Filter by activity type (default: 'Run')

        Returns:
            List of all activities since start_date (excluding treadmill/virtual runs)
        """
        all_activities = []
        after_timestamp = int(start_date.timestamp())
        page = 1
        per_page = 200

        # Excluded activity types
        excluded_types = {
            'VirtualRun',      # Treadmill/Laufband
            'Walk',            # Gehen
            'Hike',            # Wandern
            'Ride',            # Radfahren
            'VirtualRide',     # Indoor Cycling
            'WeightTraining',  # Gewichtheben
            'Workout',         # Allgemeines Training
            'Yoga',
            'Swim',
        }

        print(f"Fetching activities since {start_date.isoformat()}...")

        while True:
            activities = self.get_activities(
                after=after_timestamp,
                page=page,
                per_page=per_page
            )

            if not activities:
                break

            # Filter by activity type - only outdoor running
            filtered = [
                a for a in activities
                if a.get('type') == activity_type and a.get('type') not in excluded_types
            ]
            all_activities.extend(filtered)

            print(f"Fetched page {page}: {len(filtered)} outdoor {activity_type} activities")

            # Check if we got a full page (more might be available)
            if len(activities) < per_page:
                break

            page += 1

            # Be nice to the API - small delay between requests
            time.sleep(0.2)

        print(f"Total {activity_type} activities fetched: {len(all_activities)}")
        return all_activities

    def get_activity_details(self, activity_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific activity.

        Args:
            activity_id: Strava activity ID

        Returns:
            Detailed activity data or None
        """
        return self._make_request(f"activities/{activity_id}")

    def normalize_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize activity data for storage.

        Args:
            activity: Raw activity data from Strava

        Returns:
            Normalized activity dictionary
        """
        return {
            'strava_id': activity['id'],
            'name': activity.get('name', 'Untitled'),
            'type': activity.get('type', 'Run'),
            'start_date': activity['start_date'],
            'timezone': activity.get('timezone'),
            'distance': activity.get('distance', 0.0),
            'moving_time': activity.get('moving_time', 0),
            'elapsed_time': activity.get('elapsed_time', 0),
            'average_speed': activity.get('average_speed'),
            'max_speed': activity.get('max_speed'),
            'elevation_gain': activity.get('total_elevation_gain'),
            'average_heartrate': activity.get('average_heartrate'),
            'max_heartrate': activity.get('max_heartrate'),
            'has_heartrate': activity.get('has_heartrate', False)
        }
