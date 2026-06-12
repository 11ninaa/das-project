"""
Shared utility functions used across analysis modules.
This module provides common functionality to avoid code duplication.
"""

from typing import Any, Dict, List, Union
import numpy as np
import pandas as pd


def convert_to_native(obj: Any) -> Any:
    """
    Recursively converts numpy and pandas types (ints, floats, arrays, Series, Timestamps)
     to native Python types for JSON serialization.
    """
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, (np.ndarray, pd.Series)):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return convert_to_native(obj.__dict__)
    else:
        return obj


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divides two numbers, returning a default value if the denominator is zero.
    """
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamps a value within a specified minimum and maximum range.
    """
    return max(min_value, min(value, max_value))



