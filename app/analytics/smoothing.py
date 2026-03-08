"""
Time series smoothing algorithms.
"""
from typing import List, Union
import numpy as np


class Smoother:
    """Provides smoothing algorithms for time series data."""

    @staticmethod
    def simple_moving_average(data: List[float], window: int) -> List[float]:
        """
        Apply simple moving average smoothing.

        Args:
            data: Input data series
            window: Window size for averaging

        Returns:
            Smoothed data series
        """
        if not data or window < 1:
            return data

        # Ensure window is not larger than data
        window = min(window, len(data))

        # Use numpy for efficient computation
        data_array = np.array(data)
        smoothed = np.zeros(len(data_array))

        # Calculate centered moving average for middle points
        for i in range(len(data_array)):
            # At the start: use forward-looking window
            if i < window // 2:
                start_idx = 0
                end_idx = min(window, len(data_array))
            # At the end: use backward-looking window
            elif i >= len(data_array) - window // 2:
                start_idx = max(0, len(data_array) - window)
                end_idx = len(data_array)
            # In the middle: use centered window
            else:
                start_idx = i - window // 2
                end_idx = i + window // 2 + 1

            smoothed[i] = np.mean(data_array[start_idx:end_idx])

        return smoothed.tolist()

    @staticmethod
    def exponential_moving_average(data: List[float], alpha: float = 0.3) -> List[float]:
        """
        Apply exponential moving average smoothing.

        Args:
            data: Input data series
            alpha: Smoothing factor (0-1). Lower = more smoothing

        Returns:
            Smoothed data series
        """
        if not data:
            return data

        if not (0 < alpha <= 1):
            alpha = 0.3

        smoothed = [data[0]]

        for value in data[1:]:
            smoothed_value = alpha * value + (1 - alpha) * smoothed[-1]
            smoothed.append(smoothed_value)

        return smoothed

    @staticmethod
    def smooth_series(
        data: List[float],
        method: str = 'sma',
        strength: str = 'medium'
    ) -> List[float]:
        """
        Smooth a data series using specified method and strength.

        Args:
            data: Input data series
            method: Smoothing method ('sma' or 'ema')
            strength: Smoothing strength ('off', 'light', 'medium', 'strong')

        Returns:
            Smoothed data series
        """
        if not data or strength == 'off':
            return data

        if method == 'sma':
            # Map strength to window size
            window_map = {
                'light': 3,
                'medium': 5,
                'strong': 7
            }
            window = window_map.get(strength, 5)
            return Smoother.simple_moving_average(data, window)

        elif method == 'ema':
            # Map strength to alpha
            alpha_map = {
                'light': 0.5,
                'medium': 0.3,
                'strong': 0.15
            }
            alpha = alpha_map.get(strength, 0.3)
            return Smoother.exponential_moving_average(data, alpha)

        else:
            return data
