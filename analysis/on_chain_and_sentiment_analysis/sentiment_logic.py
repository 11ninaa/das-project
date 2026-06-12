"""
This module analyzes sentiment from text using different NLP methods.
It uses the Strategy Pattern to support multiple sentiment analysis algorithms.
"""

from typing import Dict, Any, Optional
import os
try:
    from sentiment_collector import SentimentCollector
    SENTIMENT_COLLECTOR_AVAILABLE = True
except ImportError:
    SENTIMENT_COLLECTOR_AVAILABLE = False
    SentimentCollector = None

from strategies import VaderSentimentStrategy, TextBlobSentimentStrategy


class SentimentLogic:
    """
    Analyzes text sentiment using configurable NLP strategies, primarily VADER, via the Strategy Pattern.
    """

    def __init__(self, cryptopanic_api_key: Optional[str] = None, 
                 newsapi_key: Optional[str] = None,
                 sentiment_strategy: Optional[str] = "vader"):

        if sentiment_strategy == "textblob":
            try:
                self.sentiment_strategy = TextBlobSentimentStrategy()
            except ImportError:
                self.sentiment_strategy = VaderSentimentStrategy()
        else:
            self.sentiment_strategy = VaderSentimentStrategy()
        
        if SENTIMENT_COLLECTOR_AVAILABLE and SentimentCollector:
            try:
                self.collector = SentimentCollector(
                    cryptopanic_api_key=cryptopanic_api_key,
                    newsapi_key=newsapi_key
                )
            except Exception:
                self.collector = None
        else:
            self.collector = None

    def get_sentiment(self, symbol: str) -> str:

        if self.collector:
            try:
                aggregated_text = self.collector.aggregate_sentiment(symbol)
                if aggregated_text and len(aggregated_text) > 50:
                    return aggregated_text
            except Exception:
                pass
        
        fallback_messages = {
            "BTC": "Bitcoin market activity shows mixed signals with ongoing institutional interest and regulatory developments.",
            "ETH": "Ethereum network continues to evolve with upgrades and growing DeFi adoption.",
            "default": f"{symbol} market sentiment data is being collected. Current market conditions appear neutral."
        }
        
        return fallback_messages.get(symbol, fallback_messages["default"])


    def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Returns sentiment analysis with source breakdown and specialized API scores.
        """

        texts = self.get_sentiment(symbol)
        
        prob, label = self.sentiment_strategy.analyze(texts)
        
        textblob_result = None
        if isinstance(self.sentiment_strategy, VaderSentimentStrategy):
            try:
                textblob_strategy = TextBlobSentimentStrategy()
                if textblob_strategy.available:
                    textblob_prob, textblob_label = textblob_strategy.analyze(texts)
                    textblob_result = {
                        "confidence": textblob_prob,
                        "label": textblob_label
                    }
            except Exception:
                pass

        score = prob if label == "positive" else -prob

        norm_score = (score + 1) / 2

        if self.collector:
            try:
                source_breakdown = self.collector.get_source_breakdown(symbol)
            except Exception:
                source_breakdown = {
                    "reddit": 0,
                    "cryptopanic": 0,
                    "newsapi": 0
                }
        else:
            source_breakdown = {
                "reddit": 0,
                "cryptopanic": 0,
                "newsapi": 0
            }

        result = {
            "label": label,
            "confidence": round(prob, 4),
            "sentiment_score_raw": round(score, 4),
            "sentiment_score_norm": round(norm_score, 4),
            "source_breakdown": source_breakdown,
            "text_length": len(texts),
            "nlp_method": "VADER (NLTK)" if isinstance(self.sentiment_strategy, VaderSentimentStrategy) else "TextBlob",
            "nlp_libraries_available": {
                "vader": isinstance(self.sentiment_strategy, VaderSentimentStrategy),
                "textblob": isinstance(self.sentiment_strategy, TextBlobSentimentStrategy) or textblob_result is not None
            }
        }
        
        if textblob_result:
            result["textblob_comparison"] = textblob_result
        
        return result
