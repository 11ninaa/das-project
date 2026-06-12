"""
- Reddit (via Reddit API)
- CryptoPanic (via CryptoPanic API)
- NewsAPI (via NewsAPI)
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
import time


class SentimentCollector:

    REDDIT_BASE_URL = "https://www.reddit.com/r"
    CRYPTOPANIC_BASE_URL = "https://cryptopanic.com/api/developer/v2/posts"
    NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"
    
    REDDIT_SUBREDDITS = [
        "cryptocurrency",
        "Bitcoin",
        "ethereum",
        "CryptoCurrency",
        "CryptoMarkets",
        "altcoin"
    ]
    
    def __init__(self, cryptopanic_api_key: Optional[str] = None, newsapi_key: Optional[str] = None):

        cp_key = cryptopanic_api_key or os.getenv("CRYPTOPANIC_API_KEY")
        na_key = newsapi_key or os.getenv("NEWSAPI_KEY")
        
        self.cryptopanic_api_key = cp_key.strip('"\'') if cp_key else None
        self.newsapi_key = na_key.strip('"\'') if na_key else None
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _safe_request(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Make a safe HTTP request with error handling."""
        try:
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            response = self.session.get(url, params=params, headers=request_headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    return None
            elif response.status_code == 401:
                return None
            elif response.status_code == 404:
                return None
            elif response.status_code == 429:
                time.sleep(1)
                return None
            else:
                return None
        except Exception:
            return None
    
    def get_reddit_sentiment(self, symbol: str, limit: int = 10) -> List[str]:
        """
        Get sentiment text from Reddit posts about the cryptocurrency.
        Uses Reddit's search API to find posts containing the symbol.
        """
        texts = []
        symbol_upper = symbol.upper()
        
        symbol_search_map = {
            "BTC": ["BTC", "Bitcoin"],
            "ETH": ["ETH", "Ethereum"],
            "BNB": ["BNB", "Binance Coin"],
            "SOL": ["SOL", "Solana"],
            "ADA": ["ADA", "Cardano"],
            "XRP": ["XRP", "Ripple"],
            "DOGE": ["DOGE", "Dogecoin"],
            "DOT": ["DOT", "Polkadot"],
            "MATIC": ["MATIC", "Polygon"],
            "AVAX": ["AVAX", "Avalanche"],
            "LTC": ["LTC", "Litecoin"],
        }
        
        search_terms = symbol_search_map.get(symbol_upper, [symbol])
        
        for subreddit in self.REDDIT_SUBREDDITS[:5]:  # Use more subreddits
            for search_term in search_terms[:2]:  # Try first 2 search terms
                try:
                    url = f"{self.REDDIT_BASE_URL}/{subreddit}/search.json"
                    params = {
                        "q": search_term,
                        "sort": "relevance",
                        "limit": min(limit, 25),
                        "restrict_sr": "true",
                        "t": "week"
                    }
                    
                    data = self._safe_request(url, params=params)
                    if data and "data" in data and "children" in data["data"]:
                        for post in data["data"]["children"]:
                            post_data = post.get("data", {})
                            title = post_data.get("title", "")
                            selftext = post_data.get("selftext", "")
                            
                            if title and len(title) > 10:
                                texts.append(title)
                            
                            if selftext and len(selftext) > 20:
                                texts.append(selftext[:500])  # Limit length
                    
                    time.sleep(0.6)
                    
                    if len(texts) >= limit * 2:
                        break
                except Exception:
                    continue
            
            if len(texts) >= limit * 2:
                break
        
        seen = set()
        unique_texts = []
        for text in texts:
            text_lower = text.lower()
            if text_lower not in seen:
                seen.add(text_lower)
                unique_texts.append(text)
        
        return unique_texts[:limit * 3]  # Return up to 3x limit to have more data
    
    def get_cryptopanic_sentiment(self, symbol: str, limit: int = 10) -> List[str]:

        texts = []
        
        if not self.cryptopanic_api_key:
            return texts
        
        try:
            currency_map = {
                "BTC": "BTC", "ETH": "ETH", "BNB": "BNB", "SOL": "SOL",
                "ADA": "ADA", "XRP": "XRP", "DOGE": "DOGE", "DOT": "DOT",
                "MATIC": "MATIC", "AVAX": "AVAX", "LTC": "LTC", "UNI": "UNI",
                "LINK": "LINK", "ATOM": "ATOM", "ETC": "ETC", "XLM": "XLM",
                "ALGO": "ALGO", "VET": "VET", "ICP": "ICP", "FIL": "FIL",
                "TRX": "TRX", "EOS": "EOS", "AAVE": "AAVE", "MKR": "MKR"
            }
            
            currency = currency_map.get(symbol.upper(), symbol.upper())
            
            # CryptoPanic API v2 - auth_token goes in URL
            # Format: https://cryptopanic.com/api/developer/v2/posts/?auth_token=YOUR_API_KEY
            url = f"{self.CRYPTOPANIC_BASE_URL}/?auth_token={self.cryptopanic_api_key}"
            
            # CryptoPanic API v2 parameters
            params = {
                "currencies": currency,
                "kind": "news",
                "public": "true",
                "limit": min(limit, 100)
            }
            
            data = self._safe_request(url, params=params)
            
            if data and "results" in data:
                results = data["results"]
                if isinstance(results, list) and len(results) > 0:
                    for result in results[:limit]:
                        title = result.get("title", "")
                        if title and title.strip():
                            texts.append(title.strip())

                        description = result.get("description", "") or result.get("summary", "") or result.get("text", "")
                        if description and len(description.strip()) > 20:
                            texts.append(description.strip()[:500])
                        
                        source = result.get("source", {})
                        if isinstance(source, dict):
                            source_title = source.get("title", "")
                            if source_title and source_title.strip() and source_title != title:
                                texts.append(source_title.strip())
                        
                        metadata = result.get("metadata", {})
                        if isinstance(metadata, dict):
                            meta_desc = metadata.get("description", "")
                            if meta_desc and len(meta_desc.strip()) > 20:
                                texts.append(meta_desc.strip()[:500])
        except Exception as e:
            pass
        
        return texts
    
    def get_newsapi_sentiment(self, symbol: str, limit: int = 10) -> List[str]:

        texts = []
        
        if not self.newsapi_key:
            return texts
        
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=7)
            
            query = f"{symbol} cryptocurrency OR {symbol} crypto OR Bitcoin {symbol}"
            
            params = {
                "apiKey": self.newsapi_key,
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": min(limit, 100),  # NewsAPI max is 100
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d")
            }
            
            data = self._safe_request(self.NEWSAPI_BASE_URL, params=params)
            
            if data and "articles" in data:
                for article in data["articles"][:limit]:
                    title = article.get("title", "")
                    description = article.get("description", "")
                    
                    if title and symbol.upper() in title.upper():
                        texts.append(title)
                    if description and len(description) > 20:
                        texts.append(description[:500])
        except Exception:
            pass
        
        return texts
    
    def aggregate_sentiment(self, symbol: str) -> str:
        """
        Aggregate sentiment text from all sources (Reddit, CryptoPanic, NewsAPI).

        """
        all_texts = []
        
        reddit_texts = self.get_reddit_sentiment(symbol, limit=10)
        all_texts.extend(reddit_texts)
        
        cryptopanic_texts = self.get_cryptopanic_sentiment(symbol, limit=10)
        all_texts.extend(cryptopanic_texts)
        
        newsapi_texts = self.get_newsapi_sentiment(symbol, limit=10)
        all_texts.extend(newsapi_texts)
        
        aggregated = " ".join(all_texts)
        
        aggregated = " ".join(aggregated.split())
        
        return aggregated
    
    def get_source_breakdown(self, symbol: str) -> Dict[str, int]:
        """
        Get breakdown of sentiment sources (count of items from each source).
        This method makes lightweight calls to count items without fetching full content.

        """
        try:
            reddit_count = len(self.get_reddit_sentiment(symbol, limit=5))
        except Exception:
            reddit_count = 0
        
        try:
            cryptopanic_count = len(self.get_cryptopanic_sentiment(symbol, limit=5))
        except Exception:
            cryptopanic_count = 0
        
        try:
            newsapi_count = len(self.get_newsapi_sentiment(symbol, limit=5))
        except Exception:
            newsapi_count = 0
        
        return {
            "reddit": reddit_count,
            "cryptopanic": cryptopanic_count,
            "newsapi": newsapi_count
        }
