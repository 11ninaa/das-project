"""
Sentiment Analysis Strategy Pattern.

This module provides strategies for analyzing sentiment using different NLP methods.
The Strategy Pattern allows us to easily switch between different sentiment analysis
algorithms (VADER, TextBlob, etc.) without changing the client code.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional


class SentimentAnalysisStrategy(ABC):
    """
    Abstract base class for sentiment analysis strategies.
    
    The Strategy Pattern allows us to define different NLP methods and switch
    between them easily. This makes it easy to add new sentiment analysis
    methods or compare different approaches.
    """
    
    @abstractmethod
    def analyze(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (confidence, label) where:
            - confidence: Confidence score (0.0 to 1.0)
            - label: Sentiment label ("positive", "negative", or "neutral")
        """
        pass


class VaderSentimentStrategy(SentimentAnalysisStrategy):
    """
    VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment strategy.
    
    Uses NLTK's VADER sentiment analyzer. This is the primary NLP method
    as required by the homework requirements.
    """
    
    def __init__(self):
        """Initialize VADER sentiment analyzer."""
        try:
            import nltk
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            
            # Download VADER lexicon if not available
            try:
                nltk.data.find('vader_lexicon')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)
            
            self.analyzer = SentimentIntensityAnalyzer()
        except ImportError:
            raise ImportError("NLTK is required for VADER sentiment analysis")
    
    def analyze(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (confidence, label)
        """
        if not text:
            return 0.0, "neutral"
        
        scores = self.analyzer.polarity_scores(text)
        compound_score = scores['compound']  # Range: [-1, 1]
        
        # Map to (confidence, label)
        if compound_score >= 0.05:
            return round(abs(compound_score), 4), "positive"
        elif compound_score <= -0.05:
            return round(abs(compound_score), 4), "negative"
        else:
            return round(abs(compound_score), 4), "neutral"


class TextBlobSentimentStrategy(SentimentAnalysisStrategy):
    """
    TextBlob sentiment analysis strategy.
    
    Uses TextBlob library for sentiment analysis. This is an alternative
    NLP method that can be used for comparison.
    """
    
    def __init__(self):
        """Initialize TextBlob sentiment analyzer."""
        try:
            from textblob import TextBlob
            self.TextBlob = TextBlob
            self.available = True
        except ImportError:
            self.available = False
    
    def analyze(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment using TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (confidence, label)
        """
        if not self.available or not text:
            return 0.0, "neutral"
        
        try:
            blob = self.TextBlob(text)
            polarity = blob.sentiment.polarity  # Range: [-1, 1]
            
            if polarity >= 0.05:
                return round(polarity, 4), "positive"
            elif polarity <= -0.05:
                return round(abs(polarity), 4), "negative"
            else:
                return round(abs(polarity), 4), "neutral"
        except Exception:
            return 0.0, "neutral"



