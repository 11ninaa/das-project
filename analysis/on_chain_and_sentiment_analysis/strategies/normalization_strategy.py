"""
Normalization Strategy Pattern.

This module provides strategies for normalizing on-chain metrics to a [0, 1] scale.
Different normalization strategies can be applied based on the metric type.
"""

import math
from abc import ABC, abstractmethod
from typing import Dict


class NormalizationStrategy(ABC):
    """
    Abstract base class for normalization strategies.
    
    The Strategy Pattern allows us to define different normalization algorithms
    and switch between them easily. This makes the code more flexible and
    easier to extend with new normalization methods.
    """
    
    @abstractmethod
    def normalize(self, value: float, limit: float) -> float:
        """
        Normalize a value to [0, 1] scale.
        
        Args:
            value: The value to normalize
            limit: The maximum expected value (used for scaling)
            
        Returns:
            Normalized value between 0 and 1
        """
        pass


class LogarithmicNormalizationStrategy(NormalizationStrategy):
    """
    Logarithmic normalization strategy.
    
    Uses logarithmic scaling to normalize values. This is useful for metrics
    that have a wide range of values (e.g., addresses, transactions).
    Larger values are better.
    
    Formula: log(1 + value) / log(1 + limit)
    """
    
    def normalize(self, value: float, limit: float) -> float:
        """
        Normalize using logarithmic scaling.
        
        Args:
            value: The value to normalize (must be >= 0)
            limit: The maximum expected value
            
        Returns:
            Normalized value between 0 and 1
        """
        value = max(value, 0)
        
        if limit <= 1:
            return 0.5
        
        return min(math.log1p(value) / math.log1p(limit), 1.0)


class InverseNormalizationStrategy(NormalizationStrategy):
    """
    Inverse normalization strategy.
    
    Normalizes values where smaller is better (e.g., NVT, MVRV).
    Uses logarithmic normalization and then inverts the result.
    
    Formula: 1 - (log(1 + value) / log(1 + limit))
    """
    
    def __init__(self, base_strategy: NormalizationStrategy = None):
        """
        Initialize inverse normalization strategy.
        
        Args:
            base_strategy: Base normalization strategy to use (default: Logarithmic)
        """
        self.base_strategy = base_strategy or LogarithmicNormalizationStrategy()
    
    def normalize(self, value: float, limit: float) -> float:
        """
        Normalize using inverse scaling (smaller is better).
        
        Args:
            value: The value to normalize (must be >= 0)
            limit: The maximum expected value
            
        Returns:
            Normalized value between 0 and 1 (higher score for smaller values)
        """
        base_score = self.base_strategy.normalize(value, limit)
        return 1.0 - base_score


class LinearNormalizationStrategy(NormalizationStrategy):
    """
    Linear normalization strategy.
    
    Uses simple linear scaling. Useful for metrics with predictable ranges.
    Formula: value / limit (clamped to [0, 1])
    """
    
    def normalize(self, value: float, limit: float) -> float:
        """
        Normalize using linear scaling.
        
        Args:
            value: The value to normalize
            limit: The maximum expected value
            
        Returns:
            Normalized value between 0 and 1
        """
        if limit <= 0:
            return 0.0
        
        return max(0.0, min(1.0, value / limit))



