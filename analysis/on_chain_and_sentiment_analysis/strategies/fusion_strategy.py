"""
Signal Fusion Strategy Pattern.

This module provides strategies for combining multiple signals (e.g., on-chain
and sentiment) into a final trading signal. The Strategy Pattern allows us
to easily switch between different fusion algorithms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class SignalFusionStrategy(ABC):
    """
    Abstract base class for signal fusion strategies.
    
    The Strategy Pattern allows us to define different algorithms for combining
    signals and switch between them easily. This makes it easy to experiment
    with different fusion methods or adjust weights.
    """
    
    @abstractmethod
    def fuse(self, signals: Dict[str, float]) -> Dict[str, Any]:
        """
        Combine multiple signals into a final decision.
        
        Args:
            signals: Dictionary mapping signal names to their scores (0-1 scale)
            
        Returns:
            Dictionary containing:
            - final_score: Combined score (0-1)
            - signal: Trading signal ("STRONG_BUY", "BUY", "NEUTRAL", "SELL")
            - contribution: Individual contributions from each signal
        """
        pass


class WeightedAverageFusionStrategy(SignalFusionStrategy):
    """
    Weighted average fusion strategy.
    
    Combines signals using a weighted average. Each signal is assigned a weight,
    and the final score is the weighted sum of all signals.
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize weighted average fusion strategy.
        
        Args:
            weights: Dictionary mapping signal names to their weights.
                    If None, uses default weights (onchain: 0.75, sentiment: 0.25)
        """
        if weights is None:
            self.weights = {
                "onchain": 0.75,
                "sentiment": 0.25
            }
        else:
            self.weights = weights
        
        # Normalize weights to sum to 1.0
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
    
    def fuse(self, signals: Dict[str, float]) -> Dict[str, Any]:
        """
        Combine signals using weighted average.
        
        Args:
            signals: Dictionary mapping signal names to scores (0-1 scale)
            
        Returns:
            Dictionary with final score, signal, and contributions
        """
        # Calculate weighted sum
        final_score = sum(
            signals.get(signal_name, 0.0) * weight
            for signal_name, weight in self.weights.items()
        )
        
        # Determine trading signal based on final score
        if final_score > 0.80:
            signal = "STRONG_BUY"
        elif final_score > 0.60:
            signal = "BUY"
        elif final_score > 0.40:
            signal = "NEUTRAL"
        else:
            signal = "SELL"
        
        # Calculate individual contributions
        contribution = {
            signal_name: round(signals.get(signal_name, 0.0) * weight, 4)
            for signal_name, weight in self.weights.items()
        }
        
        return {
            "final_score": round(final_score, 4),
            "signal": signal,
            "contribution": contribution
        }


class MaxFusionStrategy(SignalFusionStrategy):
    """
    Maximum fusion strategy.
    
    Takes the maximum score from all signals. Useful when you want to be
    optimistic (if any signal is strong, the overall signal is strong).
    """
    
    def fuse(self, signals: Dict[str, float]) -> Dict[str, Any]:
        """
        Combine signals by taking the maximum.
        
        Args:
            signals: Dictionary mapping signal names to scores (0-1 scale)
            
        Returns:
            Dictionary with final score, signal, and contributions
        """
        if not signals:
            return {
                "final_score": 0.0,
                "signal": "NEUTRAL",
                "contribution": {}
            }
        
        final_score = max(signals.values())
        
        # Determine trading signal
        if final_score > 0.80:
            signal = "STRONG_BUY"
        elif final_score > 0.60:
            signal = "BUY"
        elif final_score > 0.40:
            signal = "NEUTRAL"
        else:
            signal = "SELL"
        
        contribution = {
            signal_name: round(score, 4)
            for signal_name, score in signals.items()
        }
        
        return {
            "final_score": round(final_score, 4),
            "signal": signal,
            "contribution": contribution
        }



