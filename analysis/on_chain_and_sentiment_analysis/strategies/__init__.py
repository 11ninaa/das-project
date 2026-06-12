"""
Strategy Pattern implementations.

This module provides strategy interfaces and implementations for:
- Normalization strategies (for scaling metrics)
- Sentiment analysis strategies (for different NLP methods)
- Signal fusion strategies (for combining signals)
"""

from .normalization_strategy import NormalizationStrategy, LogarithmicNormalizationStrategy, InverseNormalizationStrategy
from .sentiment_strategy import SentimentAnalysisStrategy, VaderSentimentStrategy, TextBlobSentimentStrategy
from .fusion_strategy import SignalFusionStrategy, WeightedAverageFusionStrategy

__all__ = [
    'NormalizationStrategy',
    'LogarithmicNormalizationStrategy',
    'InverseNormalizationStrategy',
    'SentimentAnalysisStrategy',
    'VaderSentimentStrategy',
    'TextBlobSentimentStrategy',
    'SignalFusionStrategy',
    'WeightedAverageFusionStrategy'
]



